"""
test_config.py - Test Configuration Setup
Run this to verify your configuration is working.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.core.logging import setup_logging, get_logger, log_startup_info


def test_config():
    """Test the configuration setup."""

    print("\n" + "=" * 60)
    print("🧪 Testing Configuration")
    print("=" * 60)

    # Setup logging
    setup_logging()
    logger = get_logger("test")

    # Log startup info
    log_startup_info()

    # Test settings
    print("\n📋 Configuration Values:")
    print(f"   Gemini API Key: {'✅' if settings.GEMINI_API_KEY else '❌ Missing'}")
    print(f"   Groq API Key: {'✅' if settings.GROQ_API_KEY else '❌ Missing'}")
    print(f"   HF Token: {'✅' if settings.HF_TOKEN else '❌ Missing'}")
    print(f"   Qdrant URL: {settings.QDRANT_URL}")
    print(f"   Qdrant Collection: {settings.QDRANT_COLLECTION}")
    print(f"   Embedding Model: {settings.EMBEDDING_MODEL}")
    print(f"   Chunk Size: {settings.CHUNK_SIZE}")
    print(f"   Log Level: {settings.LOG_LEVEL}")

    # Check if required keys are present
    print("\n📊 API Key Status:")
    if settings.GEMINI_API_KEY:
        print("   ✅ Gemini API Key is set")
    else:
        print("   ❌ Gemini API Key is missing! Please add to .env")

        if settings.GROQ_API_KEY:
            print("   ✅ Groq API Key is set")
        else:
            print("   ❌ Groq API Key is missing! Please add to .env")

            print("\n" + "=" * 60)
            print("✅ Configuration test complete!")
            print("=" * 60)


if __name__ == "__main__":
    test_config()
