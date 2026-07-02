
---

## 📄 **README.md - RAG Service (LegalRAG)**

```markdown
# 🧠 LegalRAG - AI-Powered Legal Document Q&A System

> A production-grade RAG (Retrieval-Augmented Generation) system for semantic search and question-answering on legal documents.

## 🎯 What is LegalRAG?

LegalRAG is a complete RAG pipeline that enables:
- 📄 **Document Processing** - Upload PDFs (Bare Acts, Judgments, Legal Documents)
- 🔍 **Semantic Search** - Find relevant information using vector search
- 🤖 **AI Q&A** - Get accurate answers with source attribution
- 📚 **Knowledge Base** - Build and manage legal knowledge
- 🌐 **Multi-Language** - Get answers in 10+ Indian languages

## 🚀 Key Features

| Feature | Description |
|---------|-------------|
| **PDF Upload** | Upload legal documents (Bare Acts, Judgments, etc.) |
| **Auto-Processing** | Automatic text extraction, chunking, and embedding |
| **Semantic Search** | Vector-based search using Qdrant |
| **AI Q&A** | Accurate answers with source attribution |
| **Source Attribution** | Every answer includes references to source documents |
| **Multi-Language** | Support for English, Hindi, Tamil, Telugu, Marathi |
| **Docker Ready** | Containerized for easy deployment |

## 🛠️ Technology Stack

### Backend
- **FastAPI** - REST API framework
- **Qdrant** - Vector database
- **Sentence Transformers** - Text embeddings
- **PyPDF2 + pdfplumber** - PDF text extraction

### AI & LLM
- **Gemini** - Primary LLM
- **Groq** - Fallback LLM
- **LangChain** - RAG orchestration
- **Sentence Transformers** - Embedding generation (all-MiniLM-L6-v2)

### Frontend
- **Streamlit** - Knowledge base management UI

### Infrastructure
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration

## 📁 Project Structure
adalat-rag-service/
├── app/
│ ├── api/ # REST API endpoints
│ │ ├── routes.py # API routes
│ │ └── models.py # Pydantic models
│ ├── agents/ # RAG pipeline agents
│ │ ├── rag_pipeline.py # Main orchestrator
│ │ ├── query_classifier.py
│ │ ├── legal_researcher.py
│ │ └── response_generator.py
│ ├── services/ # External services
│ │ ├── qdrant_service.py # Vector DB
│ │ ├── llm_gateway.py # Gemini + Groq
│ │ └── embedding_service.py
│ └── core/ # Core configuration
│ ├── config.py
│ ├── logging.py
│ └── exceptions.py
├── frontend/
│ └── knowledge_base_ui.py # Streamlit UI
├── data/ # Data storage
├── tests/ # Unit tests
└── requirements.txt # Python dependencies


## 🔧 Installation

### Prerequisites
- Python 3.11 or higher
- Docker (for Qdrant)
- API Keys: Gemini and Groq

### Quick Setup

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/adalat-rag-service.git
cd adalat-rag-service

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# 5. Start Qdrant (Docker required)
docker run -d -p 6333:6333 --name qdrant qdrant/qdrant

# 6. Start RAG Service
uvicorn app.main:app --reload

# 7. Start Knowledge Base UI (in another terminal)
streamlit run streamlit_app.py

# Required
GEMINI_API_KEY=your_gemini_api_key
GROQ_API_KEY=your_groq_api_key
HF_TOKEN=your_huggingface_token

# Qdrant
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION=legal_knowledge

# Embedding
EMBEDDING_MODEL=all-MiniLM-L6-v2
CHUNK_SIZE=512
CHUNK_OVERLAP=50

# Service
RAG_SERVICE_HOST=0.0.0.0
RAG_SERVICE_PORT=8000
LOG_LEVEL=INFO

Usage Guide
1. Upload a Document
Open Knowledge Base UI (http://localhost:8501)

Click 📤 Upload PDF tab

Select document type (Bare Act, Judgment, etc.)

Enter document name and description

Upload PDF file

Wait for processing (automatic chunking & embedding)

2. Search Knowledge Base
Click 🔍 Search tab

Enter your question

View AI-generated answer with sources

3. API Usage
python
import requests

# Query the RAG service
response = requests.post(
    "http://localhost:8000/api/v1/query",
    json={
        "query": "What is Section 302 of BNS?",
        "language": "English",
        "max_sources": 5
    }
)

print(response.json())
🔄 Flow Diagram
text
User Query → Query Classifier → Legal Researcher → Qdrant Vector Search
                              ↓
                          Relevant Chunks
                              ↓
                     Response Generator → LLM (Gemini/Groq)
                              ↓
                     Answer + Sources
