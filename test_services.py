"""
test_services.py - Test Core Services
Run this to verify Phase 2 services are working.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.services.llm_gateway import LLMGateway
from app.services.qdrant_service import QdrantService
from app.services.embedding_service import EmbeddingService


def test_llm_gateway():
    """Test the LLM Gateway."""
    print("\n" + "=" * 60)
    print("🧪 Testing LLM Gateway")
    print("=" * 60)

    try:
        llm = LLMGateway()
        print(f"   Available providers: {llm.get_available_providers()}")

        # Test generation
        response = llm.generate(
            prompt="What is the meaning of justice in one sentence?",
            max_tokens=100,
            temperature=0.7,
        )

        if response.get("success"):
            print(f"   ✅ Provider: {response.get('provider')}")
            print(f"   ✅ Response: {response.get('response')[:100]}...")
            print(f"   ✅ Usage: {response.get('usage')}")
        else:
            print(f"   ❌ Failed: {response}")

    except Exception as e:
        print(f"   ❌ Error: {e}")


def test_qdrant_service():
    """Test the Qdrant Service."""
    print("\n" + "=" * 60)
    print("🧪 Testing Qdrant Service")
    print("=" * 60)

    try:
        qdrant = QdrantService()

        # Check health
        healthy = qdrant.health_check()
        if healthy:
            print(f"   ✅ Qdrant is healthy")
        else:
            print(f"   ❌ Qdrant is not healthy")

        # Get collection info
        info = qdrant.get_collection_info()
        if info:
            print(f"   ✅ Collection: {info.get('name')}")
            print(f"   ✅ Points: {info.get('points_count', 0)}")
            print(f"   ✅ Status: {info.get('status')}")
        else:
            print(f"   ❌ Failed to get collection info")

    except Exception as e:
        print(f"   ❌ Error: {e}")


def test_embedding_service():
    """Test the Embedding Service."""
    print("\n" + "=" * 60)
    print("🧪 Testing Embedding Service")
    print("=" * 60)

    try:
        embedding = EmbeddingService()

        # Test single embedding
        test_text = "This is a test sentence for embedding."
        embedding_vector = embedding.embed(test_text)

        print(f"   ✅ Model: {embedding.get_model_info().get('model_name')}")
        print(f"   ✅ Dimension: {len(embedding_vector)}")
        print(f"   ✅ Sample: {embedding_vector[:5]}...")

        # Test batch embedding
        test_texts = [
            "First test sentence.",
            "Second test sentence.",
            "Third test sentence.",
        ]
        batch_vectors = embedding.embed_batch(test_texts)
        print(f"   ✅ Batch size: {len(batch_vectors)}")
        print(f"   ✅ Batch dimension: {len(batch_vectors[0])}")

    except Exception as e:
        print(f"   ❌ Error: {e}")


def main():
    """Run all Phase 2 tests."""
    print("\n" + "=" * 60)
    print("🚀 Testing Phase 2 - Core Services")
    print("=" * 60)

    # Setup logging
    setup_logging()
    logger = get_logger("test")

    # Run tests
    test_llm_gateway()
    test_qdrant_service()
    test_embedding_service()

    print("\n" + "=" * 60)
    print("✅ Phase 2 tests complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
