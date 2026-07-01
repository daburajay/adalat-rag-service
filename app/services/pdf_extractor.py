"""
app/services/pdf_extractor.py - PDF Text Extraction Service
"""

import io
from typing import List, Dict, Any, Optional
from PyPDF2 import PdfReader
import pdfplumber
from app.core.logging import get_logger
from app.core.exceptions import PDFExtractionError

logger = get_logger(__name__)


class PDFExtractor:
    """
    Service for extracting text from PDF files.
    Supports multiple PDF parsing libraries.
    """
    
    def __init__(self):
        self.supported_extensions = ['.pdf']
    
    def extract_text(self, pdf_bytes: bytes) -> Dict[str, Any]:
        """
        Extract text from PDF bytes.
        
        Args:
            pdf_bytes: PDF file as bytes
        
        Returns:
            Dictionary with extracted text and metadata
        """
        try:
            # Try pdfplumber first (better for tables)
            text = self._extract_with_pdfplumber(pdf_bytes)
            if text and len(text.strip()) > 100:
                logger.info(f"✅ Extracted {len(text)} characters using pdfplumber")
                return {
                    "success": True,
                    "text": text,
                    "method": "pdfplumber",
                    "characters": len(text)
                }
            
            # Fallback to PyPDF2
            text = self._extract_with_pypdf2(pdf_bytes)
            if text and len(text.strip()) > 50:
                logger.info(f"✅ Extracted {len(text)} characters using PyPDF2")
                return {
                    "success": True,
                    "text": text,
                    "method": "PyPDF2",
                    "characters": len(text)
                }
            
            # If both fail, try to extract at least some text
            if text:
                return {
                    "success": True,
                    "text": text,
                    "method": "partial",
                    "characters": len(text),
                    "warning": "Limited text extracted"
                }
            
            raise PDFExtractionError("No text could be extracted from PDF")
            
        except Exception as e:
            logger.error(f"❌ PDF extraction failed: {e}")
            raise PDFExtractionError(str(e))
    
    def _extract_with_pdfplumber(self, pdf_bytes: bytes) -> str:
        """Extract text using pdfplumber."""
        try:
            text = ""
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text
        except Exception as e:
            logger.warning(f"pdfplumber extraction failed: {e}")
            return ""
    
    def _extract_with_pypdf2(self, pdf_bytes: bytes) -> str:
        """Extract text using PyPDF2."""
        try:
            text = ""
            reader = PdfReader(io.BytesIO(pdf_bytes))
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            return text
        except Exception as e:
            logger.warning(f"PyPDF2 extraction failed: {e}")
            return ""
    
    def get_page_count(self, pdf_bytes: bytes) -> int:
        """Get the number of pages in the PDF."""
        try:
            reader = PdfReader(io.BytesIO(pdf_bytes))
            return len(reader.pages)
        except Exception as e:
            logger.warning(f"Failed to get page count: {e}")
            return 0
    
    def extract_metadata(self, pdf_bytes: bytes) -> Dict[str, Any]:
        """Extract metadata from PDF."""
        try:
            reader = PdfReader(io.BytesIO(pdf_bytes))
            metadata = reader.metadata
            if metadata:
                return {
                    "title": metadata.get('/Title', ''),
                    "author": metadata.get('/Author', ''),
                    "subject": metadata.get('/Subject', ''),
                    "creator": metadata.get('/Creator', ''),
                    "producer": metadata.get('/Producer', ''),
                    "creation_date": metadata.get('/CreationDate', ''),
                }
            return {}
        except Exception as e:
            logger.warning(f"Failed to extract metadata: {e}")
            return {}