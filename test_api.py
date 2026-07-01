"""
test_api.py - Test Phase 3 API Layer
"""

import sys
import os
import requests

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

BASE_URL = "http://localhost:8000"


def test_health():
    """Test health endpoint."""
    print("\n" + "=" * 60)
    print("🧪 Testing Health Endpoint")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_query():
    """Test query endpoint."""
    print("\n" + "=" * 60)
    print("🧪 Testing Query Endpoint")
    print("=" * 60)
    
    try:
        payload = {
            "query": "What is Section 302 IPC?",
            "language": "English",
            "max_sources": 3
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/query",
            json=payload
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success: {data.get('success')}")
            print(f"   📝 Answer: {data.get('answer', '')[:100]}...")
            print(f"   🤖 Provider: {data.get('provider')}")
            print(f"   ⏱️ Time: {data.get('processing_time'):.2f}s")
        else:
            print(f"   ❌ Error: {response.text}")
        return response.status_code == 200
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_docs():
    """Test that docs are accessible."""
    print("\n" + "=" * 60)
    print("🧪 Testing API Docs")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/docs")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ API docs available at: {BASE_URL}/docs")
        return response.status_code == 200
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def main():
    """Run all Phase 3 tests."""
    print("\n" + "=" * 60)
    print("🚀 Testing Phase 3 - API Layer")
    print("=" * 60)
    print(f"\n🌐 API URL: {BASE_URL}")
    print("⚠️  Make sure the server is running: uvicorn app.main:app --reload")
    
    input("\nPress Enter when server is ready...")
    
    results = []
    
    # Run tests
    results.append(("Health", test_health()))
    results.append(("Docs", test_docs()))
    results.append(("Query", test_query()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    passed = 0
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"   {status} {name}: {result}")
        if result:
            passed += 1
    
    print(f"\n   Total: {passed}/{len(results)} passed")
    print("=" * 60)


if __name__ == "__main__":
    main()