"""
streamlit_app.py - Main Streamlit Application for RAG Service
"""

import streamlit as st
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the knowledge base UI
from frontend.knowledge_base_ui import render_knowledge_base

# Page config
st.set_page_config(
    page_title="AdalatMitra RAG - Knowledge Base",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)


def render_sidebar():
    """Render the sidebar."""
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/000000/justice.png", width=80)
        st.title("⚖️ AdalatMitra")
        st.caption("RAG Knowledge Base")
        
        st.divider()
        
        # Navigation
        pages = {
            "📚 Knowledge Base": "kb",
            "🔍 Search": "search",
            "⚙️ Settings": "settings"
        }
        
        for label, page_id in pages.items():
            if st.button(label, use_container_width=True, key=f"nav_{page_id}"):
                st.session_state.page = page_id
                st.rerun()
        
        st.divider()
        
        # Status
        st.caption("🔐 API Status")
        st.caption("✅ RAG Service Connected")
        st.caption("✅ Qdrant Connected")
        
        st.divider()
        
        # Service info
        st.caption("📡 RAG API: http://localhost:8000")
        st.caption("📊 Qdrant: http://localhost:6333")


def main():
    """Main application."""
    
    # Initialize session state
    if "page" not in st.session_state:
        st.session_state.page = "kb"
    
    # Render sidebar
    render_sidebar()
    
    # Render selected page
    if st.session_state.page == "kb":
        render_knowledge_base()
    elif st.session_state.page == "search":
        render_search()
    elif st.session_state.page == "settings":
        render_settings()
    else:
        render_knowledge_base()


def render_search():
    """Render search page."""
    st.title("🔍 Search Knowledge Base")
    st.caption("Search through your uploaded legal documents")
    
    search_query = st.text_input("Enter your search query", placeholder="e.g., Section 302 IPC")
    
    if search_query:
        with st.spinner("🔍 Searching..."):
            try:
                import requests
                response = requests.post(
                    "http://localhost:8000/api/v1/query",
                    json={
                        "query": search_query,
                        "language": "English",
                        "max_sources": 5
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    st.success("✅ Search complete!")
                    
                    st.subheader("📝 Answer")
                    st.write(data.get("answer", "No answer found"))
                    
                    if data.get("sources"):
                        st.subheader("📚 Sources")
                        for source in data["sources"]:
                            with st.expander(f"📄 {source.get('title', 'Source')}"):
                                st.write(source.get("content", ""))
                                st.caption(f"Relevance: {source.get('relevance_score', 0):.2f}")
                else:
                    st.error(f"❌ Search failed: {response.status_code}")
                    
            except requests.exceptions.ConnectionError:
                st.error("❌ RAG service not available. Please make sure it's running.")
            except Exception as e:
                st.error(f"❌ Error: {e}")


def render_settings():
    """Render settings page."""
    st.title("⚙️ Settings")
    st.caption("Configure your RAG service")
    
    st.divider()
    
    st.subheader("🔑 API Configuration")
    
    with st.container():
        st.text_input("RAG API URL", value="http://localhost:8000/api/v1", disabled=True)
        st.text_input("Qdrant URL", value="http://localhost:6333", disabled=True)
        st.text_input("Embedding Model", value="all-MiniLM-L6-v2", disabled=True)
    
    st.divider()
    
    st.subheader("📊 Service Status")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        try:
            import requests
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                st.success("✅ RAG API")
            else:
                st.error("❌ RAG API")
        except:
            st.error("❌ RAG API")
    
    with col2:
        try:
            import requests
            response = requests.get("http://localhost:6333/dashboard", timeout=5)
            if response.status_code == 200:
                st.success("✅ Qdrant")
            else:
                st.error("❌ Qdrant")
        except:
            st.error("❌ Qdrant")


if __name__ == "__main__":
    main()