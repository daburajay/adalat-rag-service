"""
app/services/embedding_service.py - Embedding Service
"""

from typing import List, Union, Optional
from app.core.config import settings
from app.core.logging import get_logger
from app.core.exceptions import QdrantError

logger = get_logger(__name__)


class EmbeddingService:
    """
    Service for generating text embeddings using sentence-transformers.
    """
    
    def __init__(self):
        """Initialize the embedding model."""
        self.model = None
        self.model_name = settings.EMBEDDING_MODEL
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the sentence-transformer model."""
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"✅ Embedding model loaded: {self.model_name}")
            
            # Test the model
            test_embedding = self.model.encode("test")
            logger.info(f"✅ Embedding size: {len(test_embedding)}")
            
        except ImportError as e:
            logger.error(f"❌ SentenceTransformer not installed: {e}")
            logger.info("   Run: pip install sentence-transformers")
            raise
        except Exception as e:
            logger.error(f"❌ Failed to load embedding model: {e}")
            raise
    
    def embed(
        self,
        text: Union[str, List[str]],
        normalize: bool = True
    ) -> Union[List[float], List[List[float]]]:
        """
        Generate embeddings for text.
        
        Args:
            text: Single text string or list of text strings
            normalize: Whether to normalize the embeddings
        
        Returns:
            Embedding vector or list of vectors
        """
        if not self.model:
            raise QdrantError("Embedding model not initialized")
        
        try:
            if isinstance(text, str):
                embedding = self.model.encode(
                    text,
                    normalize_embeddings=normalize,
                    show_progress_bar=False
                )
                return embedding.tolist()
            else:
                embeddings = self.model.encode(
                    text,
                    normalize_embeddings=normalize,
                    show_progress_bar=False
                )
                return [e.tolist() for e in embeddings]
                
        except Exception as e:
            logger.error(f"❌ Embedding generation failed: {e}")
            raise QdrantError(f"Embedding failed: {e}")
    
    def embed_batch(
        self,
        texts: List[str],
        batch_size: int = 32,
        normalize: bool = True
    ) -> List[List[float]]:
        """
        Generate embeddings for a batch of texts.
        
        Args:
            texts: List of text strings
            batch_size: Batch size for processing
            normalize: Whether to normalize embeddings
        
        Returns:
            List of embedding vectors
        """
        if not self.model:
            raise QdrantError("Embedding model not initialized")
        
        try:
            embeddings = self.model.encode(
                texts,
                normalize_embeddings=normalize,
                batch_size=batch_size,
                show_progress_bar=False
            )
            return [e.tolist() for e in embeddings]
            
        except Exception as e:
            logger.error(f"❌ Batch embedding failed: {e}")
            raise QdrantError(f"Batch embedding failed: {e}")
    
    def get_dimension(self) -> int:
        """Get the embedding dimension."""
        if not self.model:
            return 384  # Default for all-MiniLM-L6-v2
        
        # Get a sample embedding to determine dimension
        sample = self.model.encode("test")
        return len(sample)
    
    def get_model_info(self) -> dict:
        """Get information about the embedding model."""
        return {
            "model_name": self.model_name,
            "dimension": self.get_dimension(),
            "max_sequence_length": getattr(self.model, 'max_seq_length', 512),
        }