"""
PDF Text Extraction Module

Extracts text from PDF legal documents with layout preservation
for accurate clause boundary detection.

Uses pdfplumber for robust PDF parsing with fallback to PyPDF2.
"""

import re
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class PDFExtractor:
    """Extract text from PDF contract documents."""

    def __init__(self, preserve_layout: bool = True):
        self.preserve_layout = preserve_layout

    def extract(self, pdf_path: str) -> str:
        """
        Extract text from a PDF file.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Extracted text as a single string

        Raises:
            FileNotFoundError: If PDF does not exist
            ValueError: If PDF is corrupted or unreadable
        """
        path = Path(pdf_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        # Try pdfplumber first (better layout preservation)
        try:
            import pdfplumber
            return self._extract_with_pdfplumber(pdf_path)
        except ImportError:
            logger.warning("pdfplumber not installed, falling back to PyPDF2")
            return self._extract_with_pypdf2(pdf_path)

    def _extract_with_pdfplumber(self, pdf_path: str) -> str:
        """Extract text using pdfplumber with layout preservation."""
        import pdfplumber

        text_parts = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)

        if not text_parts:
            raise ValueError(f"Could not extract text from {pdf_path}")

        full_text = "\n\n".join(text_parts)
        return self._clean_text(full_text)

    def _extract_with_pypdf2(self, pdf_path: str) -> str:
        """Fallback extraction using PyPDF2."""
        from PyPDF2 import PdfReader

        reader = PdfReader(pdf_path)
        text_parts = []

        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)

        if not text_parts:
            raise ValueError(f"Could not extract text from {pdf_path}")

        full_text = "\n\n".join(text_parts)
        return self._clean_text(full_text)

    def _clean_text(self, text: str) -> str:
        """
        Clean extracted text for downstream NLP processing.

        - Normalize whitespace
        - Remove excessive newlines
        - Fix common OCR/PDF extraction artifacts
        """
        # Normalize line endings
        text = text.replace("\r\n", "\n").replace("\r", "\n")

        # Remove excessive whitespace (more than 2 newlines)
        text = re.sub(r"\n{3,}", "\n\n", text)

        # Fix common PDF artifacts
        text = re.sub(r"\n+([a-z])", r" \1", text)  # Broken words across lines
        text = re.sub(r"\s+", " ", text)  # Multiple spaces
        text = re.sub(r" +\n", "\n", text)  # Trailing spaces
        text = re.sub(r"\n +", "\n", text)  # Leading spaces

        # Remove page numbers and headers/footers (common patterns)
        text = re.sub(r"\n\s*\d+\s*\n", "\n", text)  # Standalone numbers
        text = re.sub(r"Page \d+ of \d+", "", text, flags=re.IGNORECASE)

        return text.strip()

    def extract_metadata(self, pdf_path: str) -> dict:
        """Extract PDF metadata if available."""
        from PyPDF2 import PdfReader

        reader = PdfReader(pdf_path)
        info = reader.metadata

        if info:
            return {
                "title": info.get("/Title", ""),
                "author": info.get("/Author", ""),
                "subject": info.get("/Subject", ""),
                "creator": info.get("/Creator", ""),
                "producer": info.get("/Producer", ""),
                "pages": len(reader.pages),
            }
        return {"pages": len(reader.pages)}
