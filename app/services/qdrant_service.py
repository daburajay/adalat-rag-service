"""
app/services/qdrant_service.py - Qdrant Vector DB Service
"""

from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import (
    VectorParams,
    Distance,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    PointIdsList,
)
from app.core.config import settings
from app.core.logging import get_logger
from app.core.exceptions import QdrantConnectionError, CollectionNotFoundError
import uuid

logger = get_logger(__name__)


class QdrantService:
    """
    Qdrant vector database service for storing and searching legal documents.
    """
    
    def __init__(self):
        """Initialize Qdrant client."""
        self.client = None
        self.collection_name = settings.QDRANT_COLLECTION
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Qdrant client."""
        try:
            if settings.QDRANT_API_KEY:
                self.client = QdrantClient(
                    url=settings.QDRANT_URL,
                    api_key=settings.QDRANT_API_KEY,
                )
                logger.info(f"✅ Qdrant Cloud connected: {settings.QDRANT_URL}")
            else:
                self.client = QdrantClient(
                    url=settings.QDRANT_URL,
                )
                logger.info(f"✅ Qdrant Local connected: {settings.QDRANT_URL}")
            
            self._ensure_collection()
            
        except Exception as e:
            logger.error(f"❌ Qdrant connection failed: {e}")
            raise QdrantConnectionError(settings.QDRANT_URL)
    
    def _ensure_collection(self):
        """Ensure the collection exists."""
        try:
            collections = self.client.get_collections().collections
            collection_names = [c.name for c in collections]
            
            if self.collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=384,
                        distance=Distance.COSINE,
                    ),
                )
                logger.info(f"✅ Created collection: {self.collection_name}")
            else:
                logger.info(f"✅ Collection exists: {self.collection_name}")
        except Exception as e:
            logger.error(f"❌ Failed to ensure collection: {e}")
            raise QdrantConnectionError(str(e))
    
    def search(
        self,
        query_vector: List[float],
        limit: int = 10,
        score_threshold: float = 0.5,
        filter_conditions: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar vectors in Qdrant."""
        try:
            search_filter = None
            if filter_conditions:
                conditions = []
                for key, value in filter_conditions.items():
                    conditions.append(
                        FieldCondition(
                            key=key,
                            match=MatchValue(value=value)
                        )
                    )
                search_filter = Filter(must=conditions)
            
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit,
                score_threshold=score_threshold,
                query_filter=search_filter,
                with_payload=True,
            )
            
            formatted_results = []
            for hit in results:
                formatted_results.append({
                    "id": hit.id,
                    "score": hit.score,
                    "payload": hit.payload,
                })
            
            logger.info(f"🔍 Found {len(formatted_results)} results")
            return formatted_results
            
        except Exception as e:
            logger.error(f"❌ Search failed: {e}")
            return []
    
    def insert(self, points: List[Dict[str, Any]]) -> bool:
        """
        Insert points into Qdrant.
        
        Args:
            points: List of points with vectors and payload
        
        Returns:
            True if successful, False otherwise
        """
        try:
            point_structures = []
            for point in points:
                # Ensure ID is a valid UUID
                point_id = point.get("id")
                if isinstance(point_id, str):
                    try:
                        # Validate UUID format
                        uuid.UUID(point_id)
                    except ValueError:
                        # If invalid, generate a new UUID
                        point_id = str(uuid.uuid4())
                
                point_structures.append(
                    PointStruct(
                        id=point_id,
                        vector=point.get("vector"),
                        payload=point.get("payload", {}),
                    )
                )
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=point_structures,
            )
            
            logger.info(f"✅ Inserted {len(point_structures)} points")
            return True
            
        except Exception as e:
            logger.error(f"❌ Insert failed: {e}")
            return False
    
    def delete(self, point_ids: List[str]) -> bool:
        """Delete points by ID."""
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=PointIdsList(
                    points=point_ids
                ),
            )
            logger.info(f"🗑️ Deleted {len(point_ids)} points")
            return True
        except Exception as e:
            logger.error(f"❌ Delete failed: {e}")
            return False
    
    def get_point(self, point_id: str) -> Optional[Dict[str, Any]]:
        """Get a point by ID."""
        try:
            result = self.client.retrieve(
                collection_name=self.collection_name,
                ids=[point_id],
                with_payload=True,
            )
            if result:
                return result[0].payload
            return None
        except Exception as e:
            logger.error(f"❌ Get point failed: {e}")
            return None
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the collection."""
        try:
            info = self.client.get_collection(self.collection_name)
            return {
                "name": self.collection_name,
                "points_count": info.points_count,
                "status": info.status,
            }
        except Exception as e:
            logger.error(f"❌ Get collection info failed: {e}")
            return {}
    
    def delete_collection(self) -> bool:
        """Delete the entire collection."""
        try:
            self.client.delete_collection(self.collection_name)
            logger.info(f"🗑️ Deleted collection: {self.collection_name}")
            return True
        except Exception as e:
            logger.error(f"❌ Delete collection failed: {e}")
            return False
    
    def health_check(self) -> bool:
        """Check if Qdrant is healthy."""
        try:
            self.client.get_collections()
            return True
        except Exception:
            return False