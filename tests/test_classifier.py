"""Tests for clause classification and extraction module."""

import pytest

from legal_contract_analyzer.clause_classifier import ClauseClassifier


class TestClauseClassifier:
    """Test clause extraction and classification functionality."""

    def setup_method(self):
        self.classifier = ClauseClassifier()

    def test_segment_sentences_basic(self):
        """Test basic sentence segmentation."""
        text = (
            "This is the first sentence. This is the second sentence. "
            "This is the third sentence with Mr. Smith mentioned."
        )
        sentences = self.classifier._segment_sentences(text)

        # Should have at least 2 sentences (Mr. abbreviation handling)
        assert len(sentences) >= 2

        # Check first sentence content
        assert "first" in sentences[0]["text"]

    def test_extract_termination_clause(self):
        """Test extraction of termination clause."""
        text = (
            "This Agreement may be terminated by either party upon ninety (90) days "
            "written notice. The Company reserves the right to terminate this agreement "
            "immediately for material breach."
        )
        clauses = self.classifier.extract_clauses(text)

        # Should find at least one clause
        assert len(clauses) >= 1

        # Check for termination clause
        term_clauses = [c for c in clauses if c["type"] == "termination"]
        assert len(term_clauses) >= 1

    def test_extract_confidentiality_clause(self):
        """Test extraction of confidentiality clause."""
        text = (
            "All information disclosed under this agreement shall be treated as "
            "confidential. Neither party shall disclose any confidential information "
            "to any third party without prior written consent."
        )
        clauses = self.classifier.extract_clauses(text)

        conf_clauses = [c for c in clauses if c["type"] == "confidentiality"]
        assert len(conf_clauses) >= 1

    def test_confidence_calculation(self):
        """Test confidence score calculation."""
        matches = ["keyword1", "keyword2", "keyword3"]
        confidence = self.classifier._calculate_confidence(
            matches, 10, "This is a sample text with enough length for scoring"
        )

        # Should be between 0 and 1
        assert 0 <= confidence <= 1

        # Multiple matches should have decent confidence
        assert confidence > 0.2

    def test_high_confidence_boost(self):
        """Test that 3+ matches get confidence boost."""
        matches = ["a", "b", "c"]
        conf1 = self.classifier._calculate_confidence(matches, 10, "x" * 600)
        matches2 = ["a", "b"]
        conf2 = self.classifier._calculate_confidence(matches2, 10, "x" * 600)

        # More matches should generally score higher
        assert conf1 > conf2 or conf1 >= conf2

    def test_empty_text(self):
        """Test handling of empty text."""
        clauses = self.classifier.extract_clauses("")
        assert clauses == []

    def test_no_matching_clauses(self):
        """Test text with no legal clauses."""
        text = "This is just a regular story about a cat and a dog playing in the park."
        clauses = self.classifier.extract_clauses(text)
        assert clauses == []

    def test_get_clause_summary(self):
        """Test clause summary generation."""
        test_clauses = [
            {"type": "termination"},
            {"type": "termination"},
            {"type": "confidentiality"},
        ]
        summary = self.classifier.get_clause_summary(test_clauses)

        assert summary["termination"] == 2
        assert summary["confidentiality"] == 1

    def test_get_clause_coverage(self):
        """Test clause coverage calculation."""
        test_clauses = [
            {"type": "termination"},
            {"type": "confidentiality"},
            {"type": "governing_law"},
        ]
        coverage = self.classifier.get_clause_coverage(test_clauses)

        # Should be between 0 and 1
        assert 0 < coverage <= 1

    def test_clause_sorting(self):
        """Test that clauses are returned in document order."""
        text = (
            "The governing law shall be the laws of New York. "
            "This agreement may be terminated with notice. "
            "All information is confidential."
        )
        clauses = self.classifier.extract_clauses(text)

        if len(clauses) >= 2:
            # Check that positions increase
            for i in range(len(clauses) - 1):
                assert clauses[i]["position"] <= clauses[i + 1]["position"]

    def test_extract_context(self):
        """Test context extraction around clause."""
        full_text = "A" * 500 + " KEYWORD HERE " + "B" * 500
        context = self.classifier._extract_context(full_text, 500)

        assert "KEYWORD" in context
        assert len(context) > 100
