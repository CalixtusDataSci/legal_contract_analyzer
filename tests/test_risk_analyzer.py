"""Tests for risk analysis engine."""

import pytest

from legal_contract_analyzer.risk_analyzer import RiskAnalyzer


class TestRiskAnalyzer:
    """Test risk analysis functionality."""

    def setup_method(self):
        self.analyzer = RiskAnalyzer()

    def test_empty_clauses(self):
        """Test risk assessment with no clauses."""
        result = self.analyzer.assess([])

        assert result["overall_score"] == 0.0
        assert result["risk_level"] == "low"
        assert result["total_clauses"] == 0

    def test_severity_calculation(self):
        """Test severity score calculation."""
        risks = [
            {"severity": 3, "description": "Risk 1"},
            {"severity": 4, "description": "Risk 2"},
        ]
        severity = self.analyzer._calculate_severity(risks, {})

        # Average of 3 and 4 = 3.5, no boost
        assert 3.0 <= severity <= 4.0

    def test_severity_with_multiple_risks(self):
        """Test severity with 3+ risks gets boost."""
        risks = [
            {"severity": 3, "description": "Risk 1"},
            {"severity": 3, "description": "Risk 2"},
            {"severity": 3, "description": "Risk 3"},
        ]
        severity = self.analyzer._calculate_severity(risks, {})

        # Should be boosted above 3
        assert severity > 3.0

    def test_severity_no_risks(self):
        """Test severity with no risks returns default."""
        severity = self.analyzer._calculate_severity([], {})
        assert severity == 1.5

    def test_ambiguity_calculation(self):
        """Test ambiguity scoring."""
        text = "The party shall use reasonable efforts to comply."
        ambiguity = self.analyzer._calculate_ambiguity([], text)

        # Contains "reasonable"
        assert ambiguity >= 2.0

    def test_ambiguity_high(self):
        """Test high ambiguity text."""
        text = (
            "The party shall use reasonable best efforts to the extent commercially "
            "reasonable in good faith including but not limited to other appropriate "
            "materially satisfactory actions."
        )
        ambiguity = self.analyzer._calculate_ambiguity([], text)

        # Multiple ambiguity indicators
        assert ambiguity >= 3.0

    def test_ambiguity_none(self):
        """Test text with no ambiguity."""
        text = "Payment of $10,000 is due on January 1, 2026."
        ambiguity = self.analyzer._calculate_ambiguity([], text)

        assert ambiguity == 1.0

    def test_risk_level_thresholds(self):
        """Test risk level categorization."""
        assert self.analyzer._get_risk_level(1.0) == "low"
        assert self.analyzer._get_risk_level(2.0) == "medium"
        assert self.analyzer._get_risk_level(3.0) == "high"
        assert self.analyzer._get_risk_level(4.5) == "critical"

    def test_detect_risk_factor_presence(self):
        """Test risk factor detection."""
        config = {
            "patterns": ["sole discretion", "at will"],
            "severity": 4,
            "description": "Test",
        }
        result = self.analyzer._detect_risk_factor(config, "employer may terminate at will")

        assert result is not None

    def test_detect_risk_factor_absence(self):
        """Test absence-based risk factor detection."""
        config = {
            "patterns": ["notice period", "days notice"],
            "severity": 5,
            "description": "No notice period",
            "absence_check": True,
        }
        # Text does NOT contain the patterns, so absence risk detected
        result = self.analyzer._detect_risk_factor(config, "this is some random text")
        assert result == "absence"

        # Text DOES contain patterns, so no absence risk
        result2 = self.analyzer._detect_risk_factor(config, "ninety days notice required")
        assert result2 is None

    def test_generate_recommendations(self):
        """Test recommendation generation."""
        assessments = [
            {
                "clause_type": "liability_cap",
                "clause_name": "Limitation of Liability",
                "risk_level": "critical",
                "detected_risks": [
                    {"name": "no_cap", "description": "No liability cap"}
                ],
            }
        ]
        risk_counts = {"low": 0, "medium": 0, "high": 0, "critical": 1}

        recs = self.analyzer._generate_recommendations(assessments, risk_counts)

        assert len(recs) > 0
        assert any("LIABILITY" in r for r in recs)

    def test_overall_score_calculation(self):
        """Test overall risk score aggregation."""
        assessments = [
            {"overall_score": 3.0},
            {"overall_score": 4.0},
            {"overall_score": 2.0},
        ]
        score = self.analyzer._calculate_overall_score(assessments)

        # Should be weighted toward higher scores
        assert score > 2.0
        assert score < 4.0

    def test_clauses_with_risk_factors(self):
        """Test full assessment with realistic clause data."""
        test_clauses = [
            {
                "id": "termination_1",
                "type": "termination",
                "type_name": "Termination Clause",
                "extracted_text": "The employer may terminate this agreement at will with sole discretion effective immediately without cause",
                "confidence": 0.85,
                "risk_factors": [],
            },
            {
                "id": "confidentiality_1",
                "type": "confidentiality",
                "type_name": "Confidentiality / NDA",
                "extracted_text": "All information is confidential for an indefinite period with liquidated damages for breach",
                "confidence": 0.80,
                "risk_factors": [],
            },
        ]

        result = self.analyzer.assess(test_clauses)

        assert result["total_clauses"] == 2
        assert result["overall_score"] > 0
        assert result["risk_level"] in ["low", "medium", "high", "critical"]
        assert len(result["clause_assessments"]) == 2

    def test_burden_calculation(self):
        """Test compliance burden calculation."""
        risks = [
            {"description": "requires monitoring and reporting"},
            {"description": "requires documentation and audit"},
        ]
        burden = self.analyzer._calculate_burden(risks, {})

        # Multiple burden indicators
        assert burden > 1.5

    def test_one_sided_detection(self):
        """Test detection of one-sided clauses."""
        assessments = [
            {
                "clause_type": "termination",
                "detected_risks": [
                    {"name": "one_sided_termination", "description": "One-sided termination"}
                ],
            }
        ]
        recs = self.analyzer._generate_recommendations(assessments, {"low": 0, "medium": 0, "high": 0, "critical": 0})

        assert any("IMBALANCE" in r for r in recs)
