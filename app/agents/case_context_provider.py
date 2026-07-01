"""
app/agents/case_context_provider.py - Case Context Provider Agent
"""

from typing import Dict, Any, Optional
from app.services.bharat_api_client import BharatAPIClient
from app.core.logging import get_logger

logger = get_logger(__name__)


class CaseContextProvider:
    """
    Provides case context from Bharat Courts API.
    """
    
    def __init__(self):
        self.bharat_client = BharatAPIClient()
    
    def get_context(self, case_data: Dict[str, Any]) -> str:
        """
        Format case data as context string.
        
        Args:
            case_data: Case data dictionary
        
        Returns:
            Formatted case context
        """
        if not case_data:
            return ""
        
        context_parts = [
            f"Case Number: {case_data.get('case_number', 'N/A')}",
            f"Case Type: {case_data.get('case_type', 'N/A')}",
            f"CNR: {case_data.get('cnr_number', 'N/A')}",
            f"Petitioner: {case_data.get('petitioner', 'N/A')}",
            f"Respondent: {case_data.get('respondent', 'N/A')}",
            f"Status: {case_data.get('status', 'N/A')}",
            f"Next Hearing: {case_data.get('next_hearing', 'Not scheduled')}",
        ]
        
        if case_data.get('court'):
            context_parts.insert(0, f"Court: {case_data.get('court', 'N/A')}")
        
        return "\n".join(context_parts)
    
    def get_basic_context(self, cnr: str) -> str:
        """
        Get context for a case by CNR.
        
        Args:
            cnr: CNR number
        
        Returns:
            Formatted case context
        """
        if not cnr:
            return ""
        
        try:
            result = self.bharat_client.search_by_cnr(cnr)
            if result.get("success"):
                return self.get_context(result.get("data", {}))
            else:
                logger.warning(f"Failed to fetch case data for CNR: {cnr}")
                return f"CNR: {cnr} (Case data not available)"
        except Exception as e:
            logger.error(f"Error fetching case data: {e}")
            return f"CNR: {cnr} (Error fetching case data)"
    
    def extract_case_info(self, text: str) -> Dict[str, Any]:
        """
        Extract case information from text.
        
        Args:
            text: Text containing case information
        
        Returns:
            Extracted case information
        """
        import re
        
        case_info = {}
        
        # Extract case number
        match = re.search(r'case\s*[#:]?\s*(\d+/\d{4})', text, re.IGNORECASE)
        if match:
            case_info["case_number"] = match.group(1)
        
        # Extract CNR
        match = re.search(r'\b([A-Z]{2}[0-9]{2}[0-9]{2}[0-9]{6}[0-9]{4})\b', text)
        if match:
            case_info["cnr"] = match.group(1)
        
        # Extract court
        courts = ["Delhi High Court", "Supreme Court", "Bombay High Court", "Madras High Court"]
        for court in courts:
            if court.lower() in text.lower():
                case_info["court"] = court
                break
        
        return case_info