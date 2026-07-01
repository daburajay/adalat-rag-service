"""
app/api/models.py - Pydantic Models for API
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


# ============================================
# Request Models
# ============================================

class QueryRequest(BaseModel):
    """
    Request model for RAG query endpoint.
    """
    query: str = Field(..., description="User's question", min_length=1)
    case_context: Optional[Dict[str, Any]] = Field(
        None, 
        description="Optional case context (CNR, case number, etc.)"
    )
    language: str = Field(
        "English", 
        description="Response language (English, Hindi, Tamil, Telugu, Marathi)"
    )
    max_sources: int = Field(
        5, 
        description="Maximum number of sources to return",
        ge=1,
        le=10
    )


class DocumentUploadRequest(BaseModel):
    """
    Request model for document upload.
    """
    document_type: str = Field(
        ..., 
        description="Type of document: Bare Act, Judgment, Case Law, etc."
    )
    name: str = Field(..., description="Document name", min_length=1)
    description: Optional[str] = Field(None, description="Document description")
    tags: Optional[List[str]] = Field(None, description="List of tags")


# ============================================
# Response Models
# ============================================

class Source(BaseModel):
    """
    Source document for RAG response.
    """
    title: str = Field(..., description="Source title")
    content: str = Field(..., description="Source content snippet")
    relevance_score: float = Field(..., description="Relevance score (0-1)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class QueryResponse(BaseModel):
    """
    Response model for RAG query.
    """
    success: bool = Field(..., description="Whether the query succeeded")
    answer: str = Field(..., description="Generated answer")
    sources: List[Source] = Field(default_factory=list, description="Sources used")
    provider: str = Field(..., description="LLM provider used")
    language: str = Field(..., description="Response language")
    processing_time: float = Field(..., description="Processing time in seconds")


class CaseSearchResponse(BaseModel):
    """
    Response model for case search.
    """
    success: bool = Field(..., description="Whether the search succeeded")
    data: Optional[Dict[str, Any]] = Field(None, description="Case data")
    error: Optional[str] = Field(None, description="Error message if any")


class DocumentResponse(BaseModel):
    """
    Response model for document upload.
    """
    success: bool = Field(..., description="Whether the upload succeeded")
    document_id: Optional[str] = Field(None, description="Document ID")
    name: Optional[str] = Field(None, description="Document name")
    pages: Optional[int] = Field(None, description="Number of pages")
    chunks: Optional[int] = Field(None, description="Number of chunks created")
    message: Optional[str] = Field(None, description="Success message")
    error: Optional[str] = Field(None, description="Error message if any")


class DocumentListResponse(BaseModel):
    """
    Response model for document list.
    """
    documents: List[Dict[str, Any]] = Field(default_factory=list, description="List of documents")
    total: int = Field(0, description="Total number of documents")


class HealthResponse(BaseModel):
    """
    Response model for health check.
    """
    status: str = Field(..., description="Health status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    timestamp: str = Field(..., description="Timestamp")


class ErrorResponse(BaseModel):
    """
    Response model for errors.
    """
    success: bool = Field(False, description="Success status")
    error: str = Field(..., description="Error message")
    type: Optional[str] = Field(None, description="Error type")
    details: Optional[Dict[str, Any]] = Field(None, description="Error details")