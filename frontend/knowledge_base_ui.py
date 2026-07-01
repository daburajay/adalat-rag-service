"""
frontend/knowledge_base_ui.py - Knowledge Base UI
"""

import streamlit as st
import requests
import json
from datetime import datetime
from typing import Dict, Any, List

# API URL
API_URL = "http://localhost:8000/api/v1"
QDRANT_URL = "http://localhost:6333"


def render_knowledge_base():
    """Render the Knowledge Base page."""
    
    st.title("📚 Knowledge Base Management")
    st.caption("Upload legal documents to build your knowledge base")
    
    # Show Qdrant stats at the top
    render_qdrant_stats()
    
    st.markdown("---")
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs([
        "📤 Upload PDF",
        "📋 Document List",
        "📊 Knowledge Base Stats"
    ])
    
    with tab1:
        render_upload_tab()
    
    with tab2:
        render_document_list()
    
    with tab3:
        render_stats_tab()


def render_qdrant_stats():
    """Show Qdrant collection stats."""
    try:
        response = requests.get(f"{QDRANT_URL}/collections/legal_knowledge", timeout=5)
        if response.status_code == 200:
            data = response.json()
            result = data.get("result", {})
            points = result.get("points_count", 0)
            status = result.get("status", "unknown")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📦 Total Chunks", points)
            with col2:
                st.metric("📄 Documents", "1" if points > 0 else "0")
            with col3:
                st.metric("⚡ Status", "🟢 Active" if status == "green" else "🟡 Unknown")
    except Exception as e:
        st.warning(f"⚠️ Qdrant not reachable: {e}")


def render_upload_tab():
    """Render the upload tab."""
    
    st.subheader("📤 Upload Legal Document")
    
    # Document details
    col1, col2 = st.columns(2)
    
    with col1:
        doc_type = st.selectbox(
            "Document Type",
            ["Bare Act", "Judgment", "Case Law", "Legal Article", "Court Order", "Other"],
            key="doc_type"
        )
    
    with col2:
        doc_name = st.text_input(
            "Document Name",
            placeholder="e.g., Indian Penal Code",
            key="doc_name"
        )
    
    doc_description = st.text_area(
        "Description (Optional)",
        placeholder="Brief description of this document...",
        height=80,
        key="doc_description"
    )
    
    tags = st.text_input(
        "Tags (comma separated)",
        placeholder="e.g., IPC, Criminal, Section 302",
        key="doc_tags"
    )
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose PDF file",
        type=["pdf"],
        help="Only PDF files are supported. Large files may take time to process.",
        key="pdf_uploader"
    )
    
    # Show file info
    if uploaded_file:
        file_size = len(uploaded_file.getvalue()) / (1024 * 1024)  # MB
        st.info(f"📄 File: {uploaded_file.name} ({file_size:.2f} MB)")
        if file_size > 5:
            st.warning(f"⚠️ Large file ({file_size:.1f} MB). Processing may take 2-5 minutes.")
    
    # Upload button
    if st.button("📤 Upload Document", type="primary", use_container_width=True):
        if not uploaded_file:
            st.error("❌ Please select a PDF file to upload")
            return
        
        if not doc_name:
            st.error("❌ Please enter a document name")
            return
        
        # Upload with progress
        with st.spinner(f"📤 Uploading and processing '{doc_name}'... This may take a few minutes."):
            result = upload_document(
                file=uploaded_file,
                doc_name=doc_name,
                doc_type=doc_type,
                description=doc_description,
                tags=tags
            )
            
            if result.get("success"):
                st.success(f"✅ Document '{doc_name}' uploaded successfully!")
                st.balloons()
                st.info(f"📊 Processed {result.get('pages', 0)} pages, {result.get('chunks', 0)} chunks")
                st.rerun()
            else:
                st.error(f"❌ Upload failed: {result.get('error', 'Unknown error')}")


def upload_document(
    file,
    doc_name: str,
    doc_type: str,
    description: str,
    tags: str
) -> Dict[str, Any]:
    """
    Upload document to the RAG service with longer timeout.
    """
    try:
        # Read file
        file_bytes = file.read()
        
        # Prepare files and data
        files = {
            "file": (file.name, file_bytes, "application/pdf")
        }
        
        data = {
            "document_type": doc_type,
            "name": doc_name,
            "description": description,
            "tags": tags
        }
        
        # Send request with 5 minute timeout
        response = requests.post(
            f"{API_URL}/documents/upload",
            files=files,
            data=data,
            timeout=300  # 5 minutes
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            try:
                error_data = response.json()
                return {"success": False, "error": error_data.get("detail", f"Server error: {response.status_code}")}
            except:
                return {"success": False, "error": f"Server error: {response.status_code}"}
            
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "RAG service not available. Please make sure it's running."}
    except requests.exceptions.Timeout:
        return {"success": False, "error": "Processing timeout. The file may be too large or the service is busy."}
    except Exception as e:
        return {"success": False, "error": str(e)}


def render_document_list():
    """Render the document list tab."""
    
    st.subheader("📋 Uploaded Documents")
    
    # First, get total points count
    try:
        collection_response = requests.get(f"{QDRANT_URL}/collections/legal_knowledge", timeout=5)
        if collection_response.status_code == 200:
            collection_data = collection_response.json()
            total_points = collection_data.get("result", {}).get("points_count", 0)
            
            if total_points == 0:
                st.info("📭 No documents uploaded yet. Upload your first document!")
                return
            
            st.caption(f"📊 Total chunks in knowledge base: {total_points}")
    
    except:
        pass
    
    # Get ALL documents by scrolling through all points
    try:
        all_points = []
        offset = None
        
        while True:
            # Build request payload
            payload = {
                "limit": 100,
                "with_payload": True,
                "with_vector": False
            }
            if offset:
                payload["offset"] = offset
            
            response = requests.post(
                f"{QDRANT_URL}/collections/legal_knowledge/points/scroll",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                result = data.get("result", {})
                points = result.get("points", [])
                all_points.extend(points)
                
                # Check if there are more points
                offset = result.get("next_page_offset", None)
                if not offset:
                    break
            else:
                break
        
        if all_points:
            # Extract unique documents from points
            documents = {}
            for point in all_points:
                payload = point.get("payload", {})
                doc_id = payload.get("document_id", "unknown")
                title = payload.get("title", "Unnamed")
                
                if doc_id not in documents:
                    documents[doc_id] = {
                        "document_id": doc_id,
                        "name": title,
                        "document_type": payload.get("document_type", "Unknown"),
                        "chunks": 0,
                        "filename": payload.get("filename", ""),
                        "uploaded_at": payload.get("uploaded_at", "N/A"),
                        "description": payload.get("description", ""),
                        "tags": payload.get("tags", [])
                    }
                documents[doc_id]["chunks"] += 1
            
            # Convert to list
            doc_list = list(documents.values())
            
            if doc_list:
                st.caption(f"Showing {len(doc_list)} document(s)")
                
                for doc in doc_list:
                    with st.container():
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown(f"**📄 {doc.get('name', 'Unnamed')}**")
                            st.caption(f"Type: {doc.get('document_type', 'Unknown')}")
                            st.caption(f"Chunks: {doc.get('chunks', 0)}")
                            st.caption(f"File: {doc.get('filename', 'N/A')}")
                            if doc.get('description'):
                                st.caption(f"Description: {doc.get('description')}")
                            if doc.get('tags'):
                                tags_str = ", ".join(doc.get('tags', []))
                                st.caption(f"Tags: {tags_str}")
                            st.caption(f"Uploaded: {doc.get('uploaded_at', 'N/A')}")
                        with col2:
                            if st.button("🗑️ Delete", key=f"del_{doc.get('document_id', '')}"):
                                st.warning("Delete feature coming soon")
                        st.divider()
            else:
                st.info("📭 No documents found in knowledge base")
        else:
            st.info("📭 No documents uploaded yet. Upload your first document!")
            
    except Exception as e:
        st.error(f"❌ Error fetching documents: {e}")
        st.info("📭 No documents uploaded yet. Upload your first document!")


def render_stats_tab():
    """Render the statistics tab."""
    
    st.subheader("📊 Knowledge Base Statistics")
    
    try:
        # Get Qdrant collection info
        response = requests.get(f"{QDRANT_URL}/collections/legal_knowledge", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            result = data.get("result", {})
            
            # Extract key stats
            points = result.get("points_count", 0)
            status = result.get("status", "unknown")
            segments = result.get("segments_count", 0)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("📦 Total Chunks", points)
            with col2:
                st.metric("📄 Documents", "1" if points > 0 else "0")
            with col3:
                st.metric("📊 Segments", segments)
            with col4:
                st.metric("⚡ Status", "🟢 Active" if status == "green" else "🟡 Unknown")
            
            st.divider()
            
            # Show collection info
            with st.expander("📋 Collection Details"):
                st.json(result)
            
        else:
            st.warning("⚠️ Could not fetch Qdrant stats")
            
    except requests.exceptions.ConnectionError:
        st.warning("⚠️ Qdrant not available")
    
    st.divider()
    
    # Recent uploads
    st.subheader("🕐 Recent Uploads")
    
    try:
        # Get points using scroll API
        response = requests.post(
            f"{QDRANT_URL}/collections/legal_knowledge/points/scroll",
            json={"limit": 10, "with_payload": True},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            points = data.get("result", {}).get("points", [])
            
            if points:
                # Extract unique documents
                doc_info = {}
                for point in points:
                    payload = point.get("payload", {})
                    title = payload.get("title", "")
                    uploaded_at = payload.get("uploaded_at", "N/A")
                    if title and title not in doc_info:
                        doc_info[title] = {
                            "name": title,
                            "chunks": 0,
                            "uploaded_at": uploaded_at
                        }
                    doc_info[title]["chunks"] += 1
                
                for name, info in doc_info.items():
                    chunks = info.get("chunks", 0)
                    uploaded_at = info.get("uploaded_at", "2026-06-25")
                    st.markdown(f"- **{name}** - {chunks} chunks - Uploaded: {uploaded_at}")
            else:
                st.info("No documents uploaded yet")
        else:
            st.info("No documents uploaded yet")
    except:
        st.info("No documents uploaded yet")