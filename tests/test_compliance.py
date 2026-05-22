"""Tests for compliance checking module."""

import pytest

from legal_contract_analyzer.compliance_checker import ComplianceChecker


class TestComplianceChecker:
    """Test compliance checking functionality."""

    def setup_method(self):
        self.checker = ComplianceChecker()

    def test_empty_contract(self):
        """Test compliance check with no clauses."""
        result = self.checker.check([], "general")

        assert result["compliance_score"] < 100
        assert len(result["missing_clauses"]) > 0
        assert result["required_clauses"]["missing"] > 0

    def test_fully_compliant_contract(self):
        """Test with all required clauses present."""
        clauses = [
            {"type": "termination"},
            {"type": "governing_law"},
            {"type": "liability_cap"},
            {"type": "dispute_resolution"},
            {"type": "entire_agreement"},
        ]
        result = self.checker.check(clauses, "general")

        assert result["compliance_score"] >= 70
        assert result["required_clauses"]["missing"] == 0

    def test_employment_contract_compliance(self):
        """Test employment-specific compliance rules."""
        clauses = [
            {"type": "termination"},
            {"type": "confidentiality"},
            {"type": "intellectual_property"},
            {"type": "governing_law"},
            {"type": "data_protection"},
        ]
        result = self.checker.check(clauses, "employment")

        assert result["contract_type"] == "employment"
        assert result["required_clauses"]["missing"] == 0
        assert result["compliance_score"] >= 70

    def test_compliance_level_calculation(self):
        """Test compliance level determination."""
        assert "FULLY" in self.checker._get_compliance_level(0.95, 0)
        assert "PARTIAL" in self.checker._get_compliance_level(0.6, 1)
        assert "NON-COMPLIANT" in self.checker._get_compliance_level(0.3, 3)

    def test_absence_risk_mapping(self):
        """Test that all clause types have absence risk descriptions."""
        from legal_contract_analyzer.config import CLAUSE_TYPES

        for clause_type in CLAUSE_TYPES:
            risk = self.checker._get_absence_risk(clause_type)
            assert len(risk) > 0
            assert ":" in risk  # Should have severity prefix

    def test_recommendation_mapping(self):
        """Test that recommendations exist for key clauses."""
        rec = self.checker._get_recommendation("termination")
        assert "notice" in rec.lower()

        rec = self.checker._get_recommendation("liability_cap")
        assert "cap" in rec.lower()

    def test_list_contract_types(self):
        """Test contract type listing."""
        types = self.checker.list_contract_types()

        assert "general" in types
        assert "employment" in types
        assert "nda" in types
        assert "service" in types

    def test_missing_clause_details(self):
        """Test missing clause information is complete."""
        clauses = [{"type": "termination"}]  # Only one clause, many missing
        result = self.checker.check(clauses, "general")

        for missing in result["missing_clauses"]:
            assert "clause_name" in missing
            assert "importance" in missing
            assert "risk_of_absence" in missing
            assert "recommendation" in missing

    def test_partial_compliance(self):
        """Test contract with some but not all required clauses."""
        clauses = [
            {"type": "termination"},
            {"type": "governing_law"},
        ]
        result = self.checker.check(clauses, "general")

        assert result["required_clauses"]["present"] == 2
        assert result["required_clauses"]["missing"] > 0
        assert 0 < result["compliance_score"] < 100

    def test_unknown_contract_type(self):
        """Test fallback to general for unknown contract type."""
        result = self.checker.check([], "unknown_type")

        assert result["contract_type"] == "unknown_type"
        assert result["contract_type_name"] == "General Commercial Agreement"
