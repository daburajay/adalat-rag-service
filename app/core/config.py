"""
app/core/config.py - Configuration Management
Loads environment variables and provides settings for the application.
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    All settings can be overridden by setting environment variables.
    """
    
    # ============================================
    # API Keys
    # ============================================
    
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    HF_TOKEN: str = os.getenv("HF_TOKEN", "")
    
    # ============================================
    # Qdrant Configuration
    # ============================================
    
    QDRANT_URL: str = os.getenv("QDRANT_URL", "http://localhost:6333")
    QDRANT_API_KEY: Optional[str] = os.getenv("QDRANT_API_KEY", None)
    QDRANT_COLLECTION: str = os.getenv("QDRANT_COLLECTION", "legal_knowledge")
    
    # ============================================
    # RAG Service Configuration
    # ============================================
    
    RAG_SERVICE_HOST: str = os.getenv("RAG_SERVICE_HOST", "0.0.0.0")
    RAG_SERVICE_PORT: int = int(os.getenv("RAG_SERVICE_PORT", "8000"))
    RAG_SERVICE_URL: str = os.getenv("RAG_SERVICE_URL", "http://localhost:8000/api/v1")
    
    # ============================================
    # Embedding Configuration
    # ============================================
    
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "512"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "50"))
    
    # ============================================
    # CORS Configuration
    # ============================================
    
    ALLOWED_ORIGINS: List[str] = os.getenv("ALLOWED_ORIGINS", "*").split(",")
    
    # ============================================
    # Logging
    # ============================================
    
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # ============================================
    # Bharat Courts
    # ============================================
    
    DEFAULT_COURT: str = os.getenv("DEFAULT_COURT", "delhi")
    DEFAULT_YEAR: str = os.getenv("DEFAULT_YEAR", "2024")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# ============================================
# Create settings instance - THIS IS IMPORTANT!
# ============================================

settings = Settings()


# ============================================
# Helper Functions
# ============================================

def get_settings() -> Settings:
    """Get the settings instance."""
    return settings


def is_development() -> bool:
    """Check if running in development mode."""
    return settings.LOG_LEVEL.lower() == "debug"


def is_production() -> bool:
    """Check if running in production mode."""
    return settings.LOG_LEVEL.lower() == "info"