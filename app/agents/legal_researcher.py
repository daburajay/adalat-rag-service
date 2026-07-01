"""
app/agents/legal_researcher.py - Legal Researcher Agent
"""

from typing import List, Dict, Any, Optional
from app.services.qdrant_service import QdrantService
from app.services.embedding_service import EmbeddingService
from app.core.logging import get_logger

logger = get_logger(__name__)


class LegalResearcher:
    """
    Searches Qdrant for legal knowledge relevant to the query.
    """
    
    def __init__(self):
        self.qdrant = QdrantService()
        self.embedding = EmbeddingService()
    
    def search(
        self,
        query: str,
        limit: int = 5,
        score_threshold: float = 0.5,
        filter_conditions: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant legal documents.
        
        Args:
            query: Search query
            limit: Maximum number of results
            score_threshold: Minimum similarity score
            filter_conditions: Optional filters (e.g., document_type)
        
        Returns:
            List of search results with payload and scores
        """
        try:
            # Generate embedding for the query
            query_vector = self.embedding.embed(query)
            
            # Search Qdrant
            results = self.qdrant.search(
                query_vector=query_vector,
                limit=limit,
                score_threshold=score_threshold,
                filter_conditions=filter_conditions
            )
            
            logger.info(f"🔍 Found {len(results)} legal documents")
            return results
            
        except Exception as e:
            logger.error(f"❌ Legal research failed: {e}")
            return []
    
    def search_by_section(self, section: str) -> List[Dict[str, Any]]:
        """
        Search for a specific legal section.
        
        Args:
            section: Section number (e.g., "302", "Section 302")
        
        Returns:
            List of search results
        """
        query = f"Section {section} Indian Penal Code"
        return self.search(query, limit=3)
    
    def search_by_act(self, act_name: str) -> List[Dict[str, Any]]:
        """
        Search for an act.
        
        Args:
            act_name: Name of the act (e.g., "IPC", "CrPC")
        
        Returns:
            List of search results
        """
        query = f"{act_name} complete act sections"
        return self.search(query, limit=5)
    
    def search_by_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        """
        Search by keyword.
        
        Args:
            keyword: Legal keyword
        
        Returns:
            List of search results
        """
        return self.search(keyword, limit=5)
    
    def format_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Format search results for LLM context.
        
        Args:
            results: Raw search results from Qdrant
        
        Returns:
            Formatted results with text and metadata
        """
        formatted = []
        for result in results:
            payload = result.get("payload", {})
            formatted.append({
                "id": result.get("id"),
                "title": payload.get("title", "Unknown Document"),
                "content": payload.get("text", ""),
                "relevance_score": result.get("score", 0.0),
                "metadata": {
                    "document_type": payload.get("document_type", "Unknown"),
                    "source": payload.get("source", ""),
                    "chunk_index": payload.get("chunk_index", 0),
                }
            })
        return formatted
    
    def get_context(self, results: List[Dict[str, Any]]) -> str:
        """
        Combine search results into context string.
        
        Args:
            results: Search results from Qdrant
        
        Returns:
            Combined context for LLM
        """
        if not results:
            return ""
        
        context_parts = []
        for i, result in enumerate(results, 1):
            payload = result.get("payload", {})
            text = payload.get("text", "")
            if text:
                context_parts.append(f"[{i}] {text[:500]}...")
        
        return "\n\n".join(context_parts)