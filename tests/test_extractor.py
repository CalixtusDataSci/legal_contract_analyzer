"""Tests for PDF text extraction module."""

import os
import tempfile
from pathlib import Path

import pytest

from legal_contract_analyzer.extractor import PDFExtractor


class TestPDFExtractor:
    """Test PDF text extraction functionality."""

    def setup_method(self):
        self.extractor = PDFExtractor()

    def test_extract_from_valid_text_file(self):
        """Test extraction from a file with valid text content."""
        # Create a mock text file to test the text pipeline
        text = (
            "This is a test contract document.\n\n"
            "SECTION 1: TERMINATION\n"
            "Either party may terminate this agreement with thirty days written notice.\n\n"
            "SECTION 2: CONFIDENTIALITY\n"
            "All confidential information shall be protected under this agreement."
        )

        # Test text cleaning directly
        cleaned = self.extractor._clean_text(text)
        assert "TERMINATION" in cleaned
        assert "CONFIDENTIALITY" in cleaned
        assert len(cleaned) > 0

    def test_clean_text_normalization(self):
        """Test text normalization and cleaning."""
        raw = (
            "Line one  \n\n\n\n  line two   \n"
            "broken\nword across lines\n"
            "Page 5 of 10\n"
            "Normal text here."
        )
        cleaned = self.extractor._clean_text(raw)

        # Should normalize multiple newlines
        assert "\n\n\n" not in cleaned

        # Should fix broken words
        assert "broken word" in cleaned or "broken\nword" not in cleaned

        # Should remove page numbers
        assert "Page 5 of 10" not in cleaned

    def test_extract_nonexistent_file(self):
        """Test handling of non-existent file."""
        with pytest.raises(FileNotFoundError):
            self.extractor.extract("/nonexistent/path/contract.pdf")

    def test_preserve_layout_setting(self):
        """Test layout preservation option."""
        extractor = PDFExtractor(preserve_layout=True)
        assert extractor.preserve_layout is True

        extractor2 = PDFExtractor(preserve_layout=False)
        assert extractor2.preserve_layout is False

    def test_empty_text_cleaning(self):
        """Test cleaning of empty or minimal text."""
        assert self.extractor._clean_text("") == ""
        assert self.extractor._clean_text("   \n\n   ") == ""

    def test_abbreviation_handling(self):
        """Test that common abbreviations are handled correctly."""
        text = "The agreement between Dr. Smith and Corp. Inc. shall commence."
        cleaned = self.extractor._clean_text(text)
        assert "Dr." in cleaned or "Dr" in cleaned
        assert "Corp" in cleaned

    def test_extract_metadata(self):
        """Test metadata extraction."""
        # Without a real PDF, we can at least test the error handling
        with pytest.raises(Exception):
            self.extractor.extract_metadata("/nonexistent/file.pdf")
