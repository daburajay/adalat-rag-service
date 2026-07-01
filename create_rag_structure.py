import os

# ============================================================================
# FOLDER STRUCTURE
# ============================================================================

folders = [
    "app",
    "app/api",
    "app/agents",
    "app/services",
    "app/core",
    "app/schemas",
    "app/utils",
    "frontend",
    "data",
    "data/cache",
    "data/uploads",
    "data/indexes",
    "tests",
]

# ============================================================================
# FILE STRUCTURE
# ============================================================================

files = [
    "requirements.txt",
    ".env.example",
    "README.md",
    "docker-compose.yml",
    "Dockerfile",
    "pytest.ini",
    "app/__init__.py",
    "app/main.py",
    "app/api/__init__.py",
    "app/api/routes.py",
    "app/api/models.py",
    "app/agents/__init__.py",
    "app/agents/query_classifier.py",
    "app/agents/legal_researcher.py",
    "app/agents/case_context_provider.py",
    "app/agents/rag_pipeline.py",
    "app/agents/response_generator.py",
    "app/agents/document_processor.py",
    "app/services/__init__.py",
    "app/services/qdrant_service.py",
    "app/services/llm_gateway.py",
    "app/services/embedding_service.py",
    "app/services/pdf_extractor.py",
    "app/services/bharat_api_client.py",
    "app/services/cache_service.py",
    "app/core/__init__.py",
    "app/core/config.py",
    "app/core/logging.py",
    "app/core/exceptions.py",
    "app/schemas/__init__.py",
    "app/schemas/case_schema.py",
    "app/schemas/document_schema.py",
    "app/schemas/response_schema.py",
    "app/utils/__init__.py",
    "app/utils/helpers.py",
    "app/utils/validators.py",
    "frontend/__init__.py",
    "frontend/knowledge_base_ui.py",
    "frontend/pdf_upload_ui.py",
    "frontend/document_list_ui.py",
    "data/.gitkeep",
    "data/cache/.gitkeep",
    "data/uploads/.gitkeep",
    "data/indexes/.gitkeep",
    "tests/__init__.py",
    "tests/test_agents.py",
    "tests/test_services.py",
    "tests/test_api.py",
]

# ============================================================================
# CREATE STRUCTURE
# ============================================================================

print("\n" + "=" * 60)
print("🚀 Creating AdalatMitra RAG Project Structure")
print("=" * 60)

# Step 1: Create folders
print("\n📁 Creating folders...")
for folder in folders:
    os.makedirs(folder, exist_ok=True)
    print(f"  ✅ {folder}/")

# Step 2: Create empty files
print("\n📄 Creating files...")
for file in files:
    with open(file, "w", encoding="utf-8") as f:
        f.write("")  # Empty file
    print(f"  ✅ {file}")

# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "=" * 60)
print("✅ RAG Project Structure Created Successfully!")
print("=" * 60)
print(f"\n📊 Summary:")
print(f"   📁 Folders Created: {len(folders)}")
print(f"   📄 Files Created: {len(files)}")
print("\n📋 Next Steps:")
print("   cd adalat-rag-service")
print("   Then add content to files as needed")
print("=" * 60)