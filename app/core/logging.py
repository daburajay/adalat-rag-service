"""
app/core/logging.py - Logging Configuration
Sets up logging for the entire application.
"""

import logging
import sys
from typing import Optional
from app.core.config import settings


def setup_logging(level: Optional[str] = None) -> None:
    """
    Setup logging configuration for the application.
    
    Args:
        level: Log level override (default: from settings)
    """
    log_level = level or settings.LOG_LEVEL
    level_value = getattr(logging, log_level.upper(), logging.INFO)
    
    # Configure root logger
    logging.basicConfig(
        level=level_value,
        format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%H:%M:%S',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set specific logger levels
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    
    # Log startup
    logger = get_logger(__name__)
    logger.info(f"✅ Logging initialized at {log_level.upper()} level")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the given name.
    
    Args:
        name: Logger name (usually __name__)
    
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


def log_startup_info() -> None:
    """Log startup information about the application."""
    logger = get_logger(__name__)
    
    logger.info("=" * 50)
    logger.info("🚀 AdalatMitra RAG Service Starting...")
    logger.info("=" * 50)
    logger.info(f"📊 Qdrant URL: {settings.QDRANT_URL}")
    logger.info(f"📚 Qdrant Collection: {settings.QDRANT_COLLECTION}")
    logger.info(f"🤖 LLM Provider: Gemini (Primary) / Groq (Fallback)")
    logger.info(f"🧠 Embedding Model: {settings.EMBEDDING_MODEL}")
    logger.info(f"📝 Log Level: {settings.LOG_LEVEL}")
    logger.info("=" * 50)


def log_request_info(method: str, path: str, client_ip: str) -> None:
    """Log incoming request information."""
    logger = get_logger("api")
    logger.info(f"📥 {method} {path} - Client: {client_ip}")


def log_error(error_type: str, error_msg: str, context: dict = None) -> None:
    """Log error information."""
    logger = get_logger("error")
    context_str = f" - Context: {context}" if context else ""
    logger.error(f"❌ {error_type}: {error_msg}{context_str}")