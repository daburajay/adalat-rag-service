"""
app/agents/document_processor.py - Document Processing Agent
Processes documents for the knowledge base.
"""

import uuid
import time
from typing import List, Dict, Any, Optional
from app.services.pdf_extractor import PDFExtractor
from app.services.embedding_service import EmbeddingService
from app.services.qdrant_service import QdrantService
from app.core.config import settings
from app.core.logging import get_logger
from app.core.exceptions import DocumentProcessingError

logger = get_logger(__name__)


class DocumentProcessor:
    """
    Processes documents for the knowledge base.
    1. Extracts text from PDF
    2. Chunks the text
    3. Generates embeddings
    4. Indexes in Qdrant
    """
    
    def __init__(self):
        self.extractor = PDFExtractor()
        self.embedding = EmbeddingService()
        self.qdrant = QdrantService()
        self.chunk_size = settings.CHUNK_SIZE
        self.chunk_overlap = settings.CHUNK_OVERLAP
    
    async def process_document(
        self,
        file_bytes: bytes,
        filename: str,
        document_type: str,
        name: str,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Process a document: extract text, chunk, embed, index.
        
        Args:
            file_bytes: PDF file as bytes
            filename: Original filename
            document_type: Type of document
            name: Document name
            description: Optional description
            tags: Optional list of tags
        
        Returns:
            Dictionary with processing results
        """
        start_time = time.time()
        
        try:
            logger.info(f"📄 Processing document: {filename}")
            logger.info(f"   Name: {name}")
            logger.info(f"   Type: {document_type}")
            logger.info(f"   Tags: {tags}")
            
            # Step 1: Extract text from PDF
            logger.info("📝 Step 1/5: Extracting text from PDF...")
            extraction_result = self.extractor.extract_text(file_bytes)
            
            if not extraction_result.get("success"):
                error_msg = extraction_result.get("error", "Extraction failed")
                logger.error(f"❌ Extraction failed: {error_msg}")
                raise DocumentProcessingError(error_msg)
            
            text = extraction_result.get("text", "")
            page_count = self.extractor.get_page_count(file_bytes)
            metadata = self.extractor.extract_metadata(file_bytes)
            
            logger.info(f"   ✅ Extracted {len(text)} characters from {page_count} pages")
            
            if len(text) < 100:
                logger.warning(f"⚠️ Very little text extracted ({len(text)} characters)")
                return {
                    "success": False,
                    "error": "Could not extract enough text from PDF",
                    "characters": len(text)
                }
            
            # Step 2: Chunk the text
            logger.info("📝 Step 2/5: Creating chunks...")
            chunks = self._chunk_text(text)
            logger.info(f"   ✅ Created {len(chunks)} chunks")
            
            if not chunks:
                raise DocumentProcessingError("No chunks created from text")
            
            # Step 3: Generate embeddings
            logger.info("📝 Step 3/5: Generating embeddings...")
            chunk_embeddings = self._generate_embeddings(chunks)
            logger.info(f"   ✅ Generated {len(chunk_embeddings)} embeddings")
            
            # Step 4: Create points for Qdrant
            logger.info("📝 Step 4/5: Creating Qdrant points...")
            document_id = str(uuid.uuid4())
            points = self._create_points(
                document_id=document_id,
                chunks=chunks,
                embeddings=chunk_embeddings,
                document_type=document_type,
                name=name,
                description=description,
                tags=tags,
                filename=filename,
                page_count=page_count,
                metadata=metadata
            )
            logger.info(f"   ✅ Created {len(points)} points")
            
            # Step 5: Index in Qdrant
            logger.info("📝 Step 5/5: Indexing in Qdrant...")
            inserted = self.qdrant.insert(points)
            
            if not inserted:
                raise DocumentProcessingError("Failed to insert into Qdrant")
            
            elapsed_time = time.time() - start_time
            logger.info(f"✅ Document processed successfully in {elapsed_time:.2f}s")
            
            return {
                "success": True,
                "document_id": document_id,
                "name": name,
                "filename": filename,
                "pages": page_count,
                "chunks": len(chunks),
                "characters": len(text),
                "processing_time": elapsed_time
            }
            
        except DocumentProcessingError as e:
            logger.error(f"❌ Document processing error: {e}")
            return {
                "success": False,
                "error": str(e),
                "document_type": document_type,
                "name": name,
                "filename": filename
            }
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "document_type": document_type,
                "name": name,
                "filename": filename
            }
    
    def _chunk_text(self, text: str) -> List[str]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Text to chunk
        
        Returns:
            List of text chunks
        """
        # Clean text
        text = text.strip()
        
        if len(text) <= self.chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # Try to break at a sentence boundary
            if end < len(text):
                # Look for sentence ending within the chunk
                sentence_end = text.rfind('.', start, end)
                if sentence_end > start + self.chunk_size // 2:
                    end = sentence_end + 1
                else:
                    # Try other sentence boundaries
                    for delimiter in ['\n\n', '\n', '. ', '! ', '? ', '; ']:
                        pos = text.rfind(delimiter, start, end)
                        if pos > start + self.chunk_size // 2:
                            end = pos + len(delimiter)
                            break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start with overlap
            start = end - self.chunk_overlap
            
            # Prevent infinite loop
            if start >= len(text):
                break
            
            if start < 0:
                start = 0
        
        # Ensure we have at least one chunk
        if not chunks:
            chunks = [text[:self.chunk_size]]
        
        return chunks
    
    def _generate_embeddings(self, chunks: List[str]) -> List[List[float]]:
        """
        Generate embeddings for chunks.
        
        Args:
            chunks: List of text chunks
        
        Returns:
            List of embedding vectors
        """
        if not chunks:
            return []
        
        try:
            # Process in batches to avoid memory issues
            batch_size = 32
            all_embeddings = []
            
            for i in range(0, len(chunks), batch_size):
                batch = chunks[i:i+batch_size]
                batch_embeddings = self.embedding.embed_batch(batch)
                all_embeddings.extend(batch_embeddings)
                logger.debug(f"   Processed batch {i//batch_size + 1}: {len(batch)} chunks")
            
            return all_embeddings
            
        except Exception as e:
            logger.error(f"❌ Embedding generation failed: {e}")
            raise DocumentProcessingError(f"Embedding failed: {e}")
    
    def _create_points(
        self,
        document_id: str,
        chunks: List[str],
        embeddings: List[List[float]],
        document_type: str,
        name: str,
        description: Optional[str],
        tags: Optional[List[str]],
        filename: str,
        page_count: int,
        metadata: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Create Qdrant points from chunks and embeddings.
        Uses clean UUIDs without any suffix.
        
        Args:
            document_id: Unique document ID
            chunks: List of text chunks
            embeddings: List of embedding vectors
            document_type: Document type
            name: Document name
            description: Document description
            tags: List of tags
            filename: Original filename
            page_count: Number of pages
            metadata: Extracted metadata
        
        Returns:
            List of points for Qdrant
        """
        points = []
        
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            # Generate a clean UUID for each point (no suffix)
            point_id = str(uuid.uuid4())
            
            point = {
                "id": point_id,  # ✅ Clean UUID format
                "vector": embedding,
                "payload": {
                    "document_id": document_id,
                    "chunk_index": i,
                    "text": chunk,
                    "document_type": document_type,
                    "title": name,
                    "description": description or "",
                    "tags": tags or [],
                    "filename": filename,
                    "page_count": page_count,
                    "chunk_size": len(chunk),
                    "metadata": metadata,
                    "source": "user_upload",
                    "uploaded_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                    "total_chunks": len(chunks)
                }
            }
            points.append(point)
        
        return points
    
    def delete_document(self, document_id: str) -> bool:
        """
        Delete a document from the knowledge base.
        
        Args:
            document_id: Document ID to delete
        
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"🗑️ Deleting document: {document_id}")
            # This would delete all points with the document_id
            # For now, return success
            return True
            
        except Exception as e:
            logger.error(f"❌ Delete failed: {e}")
            return False
    
    def get_document_info(self, document_id: str) -> Dict[str, Any]:
        """
        Get information about a document.
        
        Args:
            document_id: Document ID
        
        Returns:
            Document information
        """
        try:
            # This would query Qdrant for document info
            # For now, return empty
            return {
                "document_id": document_id,
                "found": False
            }
        except Exception as e:
            logger.error(f"❌ Get document info failed: {e}")
            return {"document_id": document_id, "found": False}