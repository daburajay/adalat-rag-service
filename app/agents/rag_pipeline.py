"""
app/agents/rag_pipeline.py - RAG Pipeline (Main Orchestrator)
"""

import time
from typing import Dict, Any, List, Optional
from app.agents.query_classifier import QueryClassifier
from app.agents.legal_researcher import LegalResearcher
from app.agents.case_context_provider import CaseContextProvider
from app.agents.response_generator import ResponseGenerator
from app.core.logging import get_logger

logger = get_logger(__name__)


class RAGPipeline:
    """
    Main RAG pipeline that orchestrates the entire flow.
    
    Flow:
    1. Classify the query
    2. Retrieve relevant context
    3. Generate response
    """
    
    def __init__(self):
        self.classifier = QueryClassifier()
        self.researcher = LegalResearcher()
        self.context_provider = CaseContextProvider()
        self.generator = ResponseGenerator()
    
    def _get_document_filter(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Create filter conditions based on query.
        This helps prioritize specific documents.
        
        Args:
            query: User's question
        
        Returns:
            Filter conditions for Qdrant search
        """
        query_lower = query.lower()
        
        # BNS (Bharatiya Nyaya Sanhita) keywords
        bns_keywords = ['bns', 'bharatiya nyaya sanhita', 'nyaya sanhita']
        if any(kw in query_lower for kw in bns_keywords):
            logger.info("🔍 Detected BNS query - filtering by BNS document")
            return {
                "must": [
                    {"key": "document_type", "match": {"value": "Bare Act"}},
                    {"key": "title", "match": {"value": "The Bharatiya Nyaya Sanhita, 2023"}}
                ]
            }
        
        # IPC (Indian Penal Code) keywords
        ipc_keywords = ['ipc', 'indian penal code', 'penal code']
        if any(kw in query_lower for kw in ipc_keywords):
            logger.info("🔍 Detected IPC query - filtering by IPC document")
            return {
                "must": [
                    {"key": "document_type", "match": {"value": "Bare Act"}},
                    {"key": "title", "match": {"value": "Indian Penal Code"}}
                ]
            }
        
        # CrPC keywords
        crpc_keywords = ['crpc', 'criminal procedure code', 'code of criminal procedure']
        if any(kw in query_lower for kw in crpc_keywords):
            logger.info("🔍 Detected CrPC query - filtering by CrPC document")
            return {
                "must": [
                    {"key": "document_type", "match": {"value": "Bare Act"}},
                    {"key": "title", "match": {"value": "Code of Criminal Procedure"}}
                ]
            }
        
        # If section number is mentioned, try to detect which act
        import re
        section_match = re.search(r'section\s*(\d+)', query_lower)
        if section_match:
            section_num = section_match.group(1)
            # Check if BNS keywords are present
            if any(kw in query_lower for kw in ['bns', 'nyaya']):
                return {
                    "must": [
                        {"key": "document_type", "match": {"value": "Bare Act"}},
                        {"key": "title", "match": {"value": "The Bharatiya Nyaya Sanhita, 2023"}}
                    ]
                }
        
        return None
    
    async def process(
        self,
        query: str,
        case_context: Optional[Dict[str, Any]] = None,
        language: str = "English",
        max_sources: int = 5
    ) -> Dict[str, Any]:
        """
        Process a query through the RAG pipeline.
        
        Args:
            query: User's question
            case_context: Optional case context
            language: Response language
            max_sources: Maximum number of sources
        
        Returns:
            Dictionary with answer, sources, and metadata
        """
        start_time = time.time()
        
        logger.info(f"🚀 Processing query: {query[:100]}...")
        
        # Step 1: Classify the query
        has_case_context = bool(case_context and case_context.get("cnr"))
        query_type, confidence = self.classifier.classify(query, has_case_context)
        logger.info(f"📊 Query type: {query_type} (confidence: {confidence:.2f})")
        
        # Step 2: Get document filter based on query
        doc_filter = self._get_document_filter(query)
        if doc_filter:
            logger.info(f"🔍 Using document filter: {doc_filter}")
        
        # Step 3: Build context
        context_parts = []
        sources = []
        
        # Case context (if available)
        if case_context:
            case_str = self.context_provider.get_context(case_context)
            if case_str:
                context_parts.append(f"--- Case Context ---\n{case_str}")
        
        # Legal knowledge (if legal or hybrid question)
        if query_type in ["legal", "case"]:
            # If filter is provided, use it
            if doc_filter:
                filter_conditions = doc_filter.get("must", [])
            else:
                filter_conditions = None
            
            search_results = self.researcher.search(
                query=query,
                limit=max_sources,
                score_threshold=0.3,  # Lower threshold to get more results
                filter_conditions=filter_conditions
            )
            
            # If no results with filter, try without filter
            if not search_results and doc_filter:
                logger.info("⚠️ No results with filter, trying without filter")
                search_results = self.researcher.search(
                    query=query,
                    limit=max_sources,
                    score_threshold=0.3,
                    filter_conditions=None
                )
            
            if search_results:
                # Format results for context
                formatted_results = self.researcher.format_results(search_results)
                context = self.researcher.get_context(search_results)
                if context:
                    context_parts.append(f"--- Legal Knowledge ---\n{context}")
                
                # Store sources
                for fr in formatted_results:
                    sources.append({
                        "title": fr.get("title", "Document"),
                        "content": fr.get("content", "")[:200],
                        "relevance_score": fr.get("relevance_score", 0.0),
                        "metadata": fr.get("metadata", {})
                    })
        
        # Step 4: Generate response
        combined_context = "\n\n".join(context_parts)
        provider = "Unknown"
        answer = ""
        
        # Build system prompt for BNS context
        system_prompt = None
        if "bns" in query.lower() or "bharatiya nyaya" in query.lower():
            system_prompt = """You are a legal assistant specializing in the Bharatiya Nyaya Sanhita (BNS), 2023.
Always provide accurate information about BNS when asked.
If the question asks about BNS, refer to BNS, not IPC or other laws.
If you are unsure, say so clearly.
Respond in simple, clear language."""
        
        if query_type == "case" and case_context:
            # Case-specific query
            result = self.generator.generate_with_sources(
                query=query,
                context=combined_context,
                sources=sources,
                language=language,
                query_type="case"
            )
            answer = result.get("response", "")
            provider = result.get("provider", "Unknown")
        elif query_type == "legal":
            # Legal query
            result = self.generator.generate_with_sources(
                query=query,
                context=combined_context,
                sources=sources,
                language=language,
                query_type="legal"
            )
            answer = result.get("response", "")
            provider = result.get("provider", "Unknown")
        else:
            # General query
            result = self.generator.generate(
                query=query,
                context=combined_context,
                language=language,
                query_type="general"
            )
            answer = result.get("response", "")
            provider = result.get("provider", "Unknown")
        
        # Step 5: Add source attribution
        if sources and answer:
            # Make sure sources are mentioned
            source_text = "\n\n📚 **Sources:**\n"
            for i, source in enumerate(sources[:3], 1):
                title = source.get("title", "Document")
                score = source.get("relevance_score", 0)
                source_text += f"{i}. {title} (Relevance: {score:.2f})\n"
            
            # Only add if not already in answer
            if "Sources:" not in answer:
                answer = answer + source_text
        
        # Log completion
        processing_time = time.time() - start_time
        logger.info(f"✅ Query processed in {processing_time:.2f}s")
        
        return {
            "answer": answer,
            "sources": sources,
            "provider": provider,
            "query_type": query_type,
            "processing_time": processing_time
        }
    
    async def process_case_query(
        self,
        query: str,
        case_data: Dict[str, Any],
        language: str = "English"
    ) -> Dict[str, Any]:
        """
        Process a case-specific query.
        
        Args:
            query: User's question
            case_data: Case data
            language: Response language
        
        Returns:
            Dictionary with answer and sources
        """
        return await self.process(
            query=query,
            case_context=case_data,
            language=language
        )
    
    async def process_legal_query(
        self,
        query: str,
        language: str = "English"
    ) -> Dict[str, Any]:
        """
        Process a legal knowledge query.
        
        Args:
            query: User's question
            language: Response language
        
        Returns:
            Dictionary with answer and sources
        """
        return await self.process(
            query=query,
            case_context=None,
            language=language
        )