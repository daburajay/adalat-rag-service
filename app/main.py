"""
app/main.py - FastAPI Entry Point
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.api.routes import router
from app.core.config import settings
from app.core.logging import setup_logging, get_logger, log_startup_info
from app.core.exceptions import handle_exception

# Setup logging
setup_logging()
logger = get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AdalatMitra RAG Service",
    description="""
    # AdalatMitra RAG Service
    
    A Retrieval-Augmented Generation (RAG) service for Indian legal cases.
    
    ## Features
    - 📚 Knowledge base management (upload PDFs)
    - 🔍 Semantic search using Qdrant vector database
    - 🤖 LLM-powered responses (Gemini + Groq fallback)
    - 🌐 Multi-language support
    - 📄 Case search integration
    
    ## Architecture
    1. User uploads legal documents → Indexed in Qdrant
    2. User asks questions → RAG pipeline retrieves context
    3. LLM generates answer with sources
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "AdalatMitra Team",
        "email": "contact@adalatmitra.com",
    },
)

# ============================================
# CORS Middleware
# ============================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# Exception Handlers
# ============================================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors."""
    logger.error(f"❌ Validation error: {exc}")
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": "Validation error",
            "details": exc.errors(),
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    error_data = handle_exception(exc)
    logger.error(f"❌ Unhandled exception: {error_data}")
    return JSONResponse(
        status_code=500,
        content=error_data
    )


# ============================================
# Include Routes
# ============================================

app.include_router(router, prefix="/api/v1")


# ============================================
# Startup Events
# ============================================

@app.on_event("startup")
async def startup_event():
    """Run on service startup."""
    log_startup_info()
    logger.info("✅ RAG Service is ready!")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on service shutdown."""
    logger.info("👋 RAG Service shutting down...")


# ============================================
# Root Endpoints
# ============================================

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "AdalatMitra RAG Service",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    from datetime import datetime
    return {
        "status": "healthy",
        "service": "AdalatMitra RAG Service",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }