"""
app/core/exceptions.py - Custom Exceptions
Defines custom exception classes for the RAG service.
"""

from typing import Optional, Dict, Any


class RAGException(Exception):
    """
    Base exception for all RAG service errors.
    """
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(message)


# ============================================
# Configuration Errors
# ============================================

class ConfigurationError(RAGException):
    """Raised when configuration is invalid or missing."""
    pass


class MissingAPIKeyError(ConfigurationError):
    """Raised when an API key is missing."""
    def __init__(self, key_name: str):
        super().__init__(
            message=f"Missing API key: {key_name}",
            details={"key": key_name}
        )


# ============================================
# Qdrant Errors
# ============================================

class QdrantError(RAGException):
    """Raised when Qdrant operations fail."""
    pass


class QdrantConnectionError(QdrantError):
    """Raised when Qdrant is not reachable."""
    def __init__(self, url: str):
        super().__init__(
            message=f"Cannot connect to Qdrant at {url}",
            details={"url": url}
        )


class CollectionNotFoundError(QdrantError):
    """Raised when a collection doesn't exist."""
    def __init__(self, collection_name: str):
        super().__init__(
            message=f"Collection '{collection_name}' not found",
            details={"collection": collection_name}
        )


# ============================================
# LLM Errors
# ============================================

class LLMError(RAGException):
    """Raised when LLM operations fail."""
    pass


class LLMProviderError(LLMError):
    """Raised when a specific LLM provider fails."""
    def __init__(self, provider: str, error: str):
        super().__init__(
            message=f"{provider} error: {error}",
            details={"provider": provider, "error": error}
        )


# ============================================
# Document Processing Errors
# ============================================

class DocumentProcessingError(RAGException):
    """Raised when document processing fails."""
    pass


class PDFExtractionError(DocumentProcessingError):
    """Raised when PDF extraction fails."""
    def __init__(self, filename: str, error: str):
        super().__init__(
            message=f"Failed to extract text from PDF '{filename}': {error}",
            details={"filename": filename, "error": error}
        )


# ============================================
# Query Errors
# ============================================

class QueryError(RAGException):
    """Raised when query processing fails."""
    pass


class QueryClassificationError(QueryError):
    """Raised when query classification fails."""
    def __init__(self, query: str, error: str):
        super().__init__(
            message=f"Failed to classify query: {error}",
            details={"query": query, "error": error}
        )


# ============================================
# Rate Limiting Errors
# ============================================

class RateLimitError(RAGException):
    """Raised when rate limit is exceeded."""
    def __init__(self, resource: str, limit: int):
        super().__init__(
            message=f"Rate limit exceeded for {resource}. Limit: {limit}",
            details={"resource": resource, "limit": limit}
        )


# ============================================
# Helper Functions
# ============================================

def handle_exception(e: Exception) -> Dict[str, Any]:
    """
    Convert any exception to a standardized error response.
    
    Args:
        e: The exception to handle
    
    Returns:
        Dictionary with error details
    """
    if isinstance(e, RAGException):
        return {
            "success": False,
            "error": e.message,
            "details": e.details,
            "type": e.__class__.__name__
        }
    
    return {
        "success": False,
        "error": str(e),
        "type": e.__class__.__name__
    }