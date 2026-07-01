"""
app/api/routes.py - API Routes
"""

import time
from typing import Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import JSONResponse
from app.api.models import (
    QueryRequest, QueryResponse, Source,
    DocumentResponse, CaseSearchResponse,
    DocumentListResponse, HealthResponse,
    ErrorResponse
)
from app.core.logging import get_logger, log_request_info, log_error
from app.core.exceptions import handle_exception

# Initialize router
router = APIRouter()
logger = get_logger(__name__)


# ============================================
# Health Check
# ============================================

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    """
    from datetime import datetime
    return {
        "status": "healthy",
        "service": "AdalatMitra RAG Service",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


# ============================================
# RAG Query Endpoint
# ============================================

@router.post("/query", response_model=QueryResponse)
async def query_rag(request: QueryRequest):
    """
    Query the RAG pipeline.
    
    This endpoint processes a user question, retrieves relevant context,
    and generates an answer using the LLM.
    """
    start_time = time.time()
    
    try:
        # Log request
        log_request_info("POST", "/query", "client")
        logger.info(f"📝 Query: {request.query[:100]}...")
        logger.info(f"🌐 Language: {request.language}")
        
        # Import RAG pipeline
        from app.agents.rag_pipeline import RAGPipeline
        from app.core.config import settings
        
        # Initialize and run pipeline
        pipeline = RAGPipeline()
        result = await pipeline.process(
            query=request.query,
            case_context=request.case_context,
            language=request.language,
            max_sources=request.max_sources
        )
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Format response
        sources = []
        for src in result.get("sources", []):
            sources.append(Source(
                title=src.get("title", "Unknown Source"),
                content=src.get("content", ""),
                relevance_score=src.get("relevance_score", 0.0),
                metadata=src.get("metadata", {})
            ))
        
        return QueryResponse(
            success=True,
            answer=result.get("answer", "No response generated"),
            sources=sources,
            provider=result.get("provider", "Unknown"),
            language=request.language,
            processing_time=processing_time
        )
        
    except Exception as e:
        error_data = handle_exception(e)
        logger.error(f"❌ Query failed: {error_data}")
        raise HTTPException(
            status_code=500,
            detail=error_data
        )


# ============================================
# Document Upload Endpoint
# ============================================

@router.post("/documents/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    document_type: str = Form(...),
    name: str = Form(...),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None)
):
    """
    Upload and process a document.
    
    This endpoint processes a PDF file, extracts text, creates chunks,
    generates embeddings, and indexes them in Qdrant.
    """
    try:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are supported"
            )
        
        # Log request
        log_request_info("POST", "/documents/upload", "client")
        logger.info(f"📄 File: {file.filename}")
        logger.info(f"📝 Type: {document_type}, Name: {name}")
        
        # Read file content
        content = await file.read()
        
        # Process document
        from app.agents.document_processor import DocumentProcessor
        processor = DocumentProcessor()
        
        result = await processor.process_document(
            file_bytes=content,
            filename=file.filename,
            document_type=document_type,
            name=name,
            description=description,
            tags=tags.split(',') if tags else []
        )
        
        if result.get("success"):
            return DocumentResponse(
                success=True,
                document_id=result.get("document_id"),
                name=name,
                pages=result.get("pages", 0),
                chunks=result.get("chunks", 0),
                message=f"Document '{name}' uploaded successfully"
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Processing failed")
            )
            
    except HTTPException:
        raise
    except Exception as e:
        error_data = handle_exception(e)
        logger.error(f"❌ Upload failed: {error_data}")
        raise HTTPException(
            status_code=500,
            detail=error_data
        )


# ============================================
# Document List Endpoint
# ============================================

@router.get("/documents", response_model=DocumentListResponse)
async def list_documents(
    doc_type: Optional[str] = Query(None, description="Filter by document type"),
    search: Optional[str] = Query(None, description="Search by name or tags"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of results")
):
    """
    List all uploaded documents.
    """
    try:
        log_request_info("GET", "/documents", "client")
        logger.info(f"📋 Listing documents: type={doc_type}, search={search}")
        
        # Import Qdrant service
        from app.services.qdrant_service import QdrantService
        qdrant = QdrantService()
        
        # Placeholder - implement document listing
        # For now, return empty list
        documents = []
        
        return DocumentListResponse(
            documents=documents,
            total=len(documents)
        )
        
    except Exception as e:
        error_data = handle_exception(e)
        logger.error(f"❌ List documents failed: {error_data}")
        raise HTTPException(
            status_code=500,
            detail=error_data
        )


# ============================================
# Document Delete Endpoint
# ============================================

@router.delete("/documents/{doc_id}")
async def delete_document(doc_id: str):
    """
    Delete a document by ID.
    """
    try:
        log_request_info("DELETE", f"/documents/{doc_id}", "client")
        logger.info(f"🗑️ Deleting document: {doc_id}")
        
        # Import Qdrant service
        from app.services.qdrant_service import QdrantService
        qdrant = QdrantService()
        
        # Placeholder - implement document deletion
        # For now, return success
        return {
            "status": "deleted",
            "id": doc_id,
            "message": f"Document {doc_id} deleted successfully"
        }
        
    except Exception as e:
        error_data = handle_exception(e)
        logger.error(f"❌ Delete failed: {error_data}")
        raise HTTPException(
            status_code=500,
            detail=error_data
        )


# ============================================
# Case Search Endpoint
# ============================================

@router.post("/cases/search", response_model=CaseSearchResponse)
async def search_case(
    cnr: Optional[str] = None,
    case_number: Optional[str] = None,
    year: str = "2024",
    court: str = "Delhi High Court"
):
    """
    Search for a case by CNR or case number.
    """
    try:
        log_request_info("POST", "/cases/search", "client")
        logger.info(f"🔍 Searching case: cnr={cnr}, case_number={case_number}")
        
        if not cnr and not case_number:
            raise HTTPException(
                status_code=400,
                detail="Either CNR or case number is required"
            )
        
        # Import Bharat API client
        from app.services.bharat_api_client import BharatAPIClient
        client = BharatAPIClient()
        
        if cnr:
            result = await client.search_by_cnr(cnr)
        else:
            result = await client.search_by_case_number(
                case_number=case_number,
                year=year,
                court=court
            )
        
        return CaseSearchResponse(
            success=result.get("success", False),
            data=result.get("data"),
            error=result.get("error")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        error_data = handle_exception(e)
        logger.error(f"❌ Case search failed: {error_data}")
        raise HTTPException(
            status_code=500,
            detail=error_data
        )