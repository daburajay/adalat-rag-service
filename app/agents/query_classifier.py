"""
app/agents/query_classifier.py - Query Classifier Agent
"""

import re
from typing import Dict, Any, Tuple
from app.core.logging import get_logger

logger = get_logger(__name__)


class QueryClassifier:
    """
    Classifies user questions into:
    - case: Related to a specific case (status, next hearing, etc.)
    - legal: Legal knowledge question (sections, acts, etc.)
    - general: Non-legal question
    """
    
    # Legal keywords
    LEGAL_KEYWORDS = [
        "section", "act", "ipc", "crpc", "constitution",
        "punishment", "sentence", "bail", "fir", "crime",
        "law", "legal", "court", "judge", "provision",
        "offence", "offense", "penalty", "code", "statute",
        "amendment", "article", "clause", "sub-section",
        "civil", "criminal", "appeal", "petition", "writ"
    ]
    
    # Case-related keywords
    CASE_KEYWORDS = [
        "my case", "this case", "next hearing", "case status",
        "hearing date", "case number", "cnr", "petitioner",
        "respondent", "case details", "case history",
        "order", "judgment", "my hearing", "case progress"
    ]
    
    def classify(self, query: str, has_case_context: bool = False) -> Tuple[str, float]:
        """
        Classify the query type.
        
        Args:
            query: User's question
            has_case_context: Whether case context is available
        
        Returns:
            Tuple of (query_type, confidence_score)
        """
        query_lower = query.lower()
        
        # Check case-related (if context available)
        if has_case_context:
            case_score = sum(1 for kw in self.CASE_KEYWORDS if kw in query_lower)
            if case_score > 0:
                confidence = min(case_score / 3, 1.0)
                logger.debug(f"🔍 Classified as CASE with confidence {confidence:.2f}")
                return "case", confidence
        
        # Check legal
        legal_score = sum(1 for kw in self.LEGAL_KEYWORDS if kw in query_lower)
        if legal_score > 0:
            confidence = min(legal_score / 3, 1.0)
            logger.debug(f"🔍 Classified as LEGAL with confidence {confidence:.2f}")
            return "legal", confidence
        
        # Default to general
        logger.debug("🔍 Classified as GENERAL")
        return "general", 0.5
    
    def get_confidence_scores(self, query: str) -> Dict[str, float]:
        """
        Get confidence scores for all types.
        
        Args:
            query: User's question
        
        Returns:
            Dictionary with confidence scores
        """
        query_lower = query.lower()
        
        legal_score = sum(1 for kw in self.LEGAL_KEYWORDS if kw in query_lower)
        case_score = sum(1 for kw in self.CASE_KEYWORDS if kw in query_lower)
        
        total = legal_score + case_score
        if total == 0:
            return {"legal": 0.0, "case": 0.0, "general": 0.9}
        
        return {
            "legal": min(legal_score / 3, 1.0),
            "case": min(case_score / 3, 1.0),
            "general": max(0.0, 1.0 - (total / 6))
        }
    
    def extract_keywords(self, query: str) -> list:
        """
        Extract keywords from the query.
        
        Args:
            query: User's question
        
        Returns:
            List of keywords
        """
        # Remove stop words and clean
        stop_words = {'what', 'is', 'are', 'the', 'of', 'to', 'for', 'in', 'on', 'at'}
        words = re.findall(r'\b[a-zA-Z]{3,}\b', query.lower())
        return [w for w in words if w not in stop_words]
    
    def extract_case_number(self, query: str) -> str:
        """
        Try to extract a case number from the query.
        
        Args:
            query: User's question
        
        Returns:
            Extracted case number or empty string
        """
        # Pattern: 355/2024, W.P.(C)-123/2024, etc.
        patterns = [
            r'(\d+/\d{4})',  # 355/2024
            r'([A-Z.()]+-\d+/\d{4})',  # W.P.(C)-123/2024
            r'([A-Z.()]+\s*\d+/\d{4})',  # W.P.(C) 123/2024
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return ""
    
    def extract_cnr(self, query: str) -> str:
        """
        Try to extract a CNR number from the query.
        
        Args:
            query: User's question
        
        Returns:
            Extracted CNR or empty string
        """
        # CNR pattern: 2 letters + 2 digits + 2 digits + 6 digits + 4 digits
        pattern = r'\b([A-Z]{2}[0-9]{2}[0-9]{2}[0-9]{6}[0-9]{4})\b'
        match = re.search(pattern, query, re.IGNORECASE)
        if match:
            return match.group(1)
        return ""