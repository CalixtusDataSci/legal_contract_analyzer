"""
Integration tests for the complete ContractAnalyzer pipeline.

Tests the full workflow from text extraction through report generation.
"""

import tempfile
import os

import pytest

from legal_contract_analyzer import ContractAnalyzer


class TestContractAnalyzerIntegration:
    """Integration tests for the complete analysis pipeline."""

    def setup_method(self):
        self.analyzer = ContractAnalyzer()

    def test_analyze_sample_text(self):
        """Test full analysis pipeline with sample contract text."""
        # Create a sample contract as a text file (PDF requires actual PDF)
        sample_text = """
        MASTER SERVICE AGREEMENT

        This Master Service Agreement ("Agreement") is entered into as of January 1, 2026.

        1. TERM AND TERMINATION
        This Agreement shall commence on the Effective Date and continue for a period of twelve (12) months.
        Either party may terminate this Agreement upon ninety (90) days prior written notice.
        The Company may terminate this Agreement immediately for material breach.

        2. CONFIDENTIALITY
        Each party agrees to maintain the confidentiality of all proprietary information disclosed.
        All confidential information shall remain the property of the disclosing party.
        This obligation shall survive termination for a period of five (5) years.

        3. LIMITATION OF LIABILITY
        IN NO EVENT SHALL EITHER PARTY BE LIABLE FOR ANY INDIRECT, INCIDENTAL, CONSEQUENTIAL,
        OR SPECIAL DAMAGES. The total liability of either party shall not exceed the total amount
        paid by Customer under this Agreement in the twelve (12) months preceding the claim.

        4. GOVERNING LAW
        This Agreement shall be governed by and construed in accordance with the laws of the
        State of New York, without regard to conflict of law principles.

        5. INTELLECTUAL PROPERTY
        All intellectual property rights in the Services shall remain with Company.
        Customer is granted a limited, non-exclusive license to use the deliverables.
        Customer hereby assigns all rights in any feedback provided to Company.

        6. INDEMNIFICATION
        Customer shall indemnify and hold harmless Company from any claims arising from
        Customer's use of the Services in violation of this Agreement.

        7. FORCE MAJEURE
        Neither party shall be liable for any failure to perform due to causes beyond its
        reasonable control, including acts of God, natural disasters, pandemic, or government action.

        8. PAYMENT TERMS
        Customer shall pay all fees within thirty (30) days of invoice date.
        Late payments subject to 1.5% monthly service charge.
        All fees are non-refundable.

        9. ENTIRE AGREEMENT
        This Agreement constitutes the entire agreement between the parties and supersedes
        all prior agreements, whether written or oral.

        10. DISPUTE RESOLUTION
        Any dispute shall first be submitted to mediation. If mediation fails, the dispute
        shall be resolved by binding arbitration in accordance with ICC rules.

        11. ASSIGNMENT
        Neither party may assign this Agreement without the prior written consent of the other party.

        12. AMENDMENT
        This Agreement may only be amended by a written instrument signed by both parties.
        """

        # Write sample text to a file and test individual components
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write(sample_text)
            tmp_path = f.name

        try:
            # Test the classifier directly since we have text
            from legal_contract_analyzer.clause_classifier import ClauseClassifier
            classifier = ClauseClassifier()
            clauses = classifier.extract_clauses(sample_text)

            # Should find multiple clauses
            assert len(clauses) >= 5

            # Check key clause types found
            clause_types = [c["type"] for c in clauses]
            assert "termination" in clause_types
            assert "confidentiality" in clause_types
            assert "governing_law" in clause_types

            # Test risk analysis
            from legal_contract_analyzer.risk_analyzer import RiskAnalyzer
            risk = RiskAnalyzer()
            risk_result = risk.assess(clauses)

            assert risk_result["total_clauses"] == len(clauses)
            assert risk_result["overall_score"] > 0
            assert risk_result["risk_level"] in ["low", "medium", "high", "critical"]

            # Test compliance checking
            from legal_contract_analyzer.compliance_checker import ComplianceChecker
            compliance = ComplianceChecker()
            comp_result = compliance.check(clauses, "service")

            assert comp_result["compliance_score"] > 0
            assert comp_result["contract_type"] == "service"

        finally:
            os.unlink(tmp_path)

    def test_end_to_end_components(self):
        """Test that all components integrate correctly."""
        sample_text = (
            "This Agreement shall be governed by the laws of Nigeria. "
            "Either party may terminate this agreement with thirty days notice. "
            "All confidential information shall be protected. "
            "Company shall not be liable for indirect damages exceeding fees paid. "
        )

        from legal_contract_analyzer.clause_classifier import ClauseClassifier
        from legal_contract_analyzer.risk_analyzer import RiskAnalyzer
        from legal_contract_analyzer.compliance_checker import ComplianceChecker
        from legal_contract_analyzer.report_generator import ReportGenerator

        # Extract
        classifier = ClauseClassifier()
        clauses = classifier.extract_clauses(sample_text)
        assert len(clauses) >= 3

        # Risk assess
        risk_analyzer = RiskAnalyzer()
        risk = risk_analyzer.assess(clauses)
        assert "overall_score" in risk

        # Compliance check
        checker = ComplianceChecker()
        compliance = checker.check(clauses, "general")
        assert "compliance_score" in compliance

        # Report generation
        reporter = ReportGenerator()
        result = {
            "filename": "test_contract.pdf",
            "text_length": len(sample_text),
            "clauses_found": len(clauses),
            "clauses": clauses,
            "risk_summary": risk,
            "compliance": compliance,
        }

        md_report = reporter.generate_markdown(result)
        assert "Contract Analysis Report" in md_report
        assert "Risk Assessment" in md_report

    def test_report_generation(self):
        """Test report generation produces valid output."""
        from legal_contract_analyzer.report_generator import ReportGenerator

        reporter = ReportGenerator()

        mock_result = {
            "filename": "test.pdf",
            "text_length": 1000,
            "clauses_found": 3,
            "clauses": [
                {
                    "id": "term_1",
                    "type": "termination",
                    "type_name": "Termination Clause",
                    "extracted_text": "Test termination text",
                    "context": "Context",
                    "position": 0,
                    "confidence": 0.8,
                    "risk_factors": [],
                }
            ],
            "risk_summary": {
                "overall_score": 2.5,
                "risk_level": "medium",
                "total_clauses": 1,
                "high_risk_clauses": 0,
                "critical_risk_clauses": 0,
                "clause_assessments": [],
                "risk_distribution": {"low": 0, "medium": 1, "high": 0, "critical": 0},
                "recommendations": ["Standard review recommended."],
            },
            "compliance": {
                "contract_type": "general",
                "compliance_score": 50.0,
                "compliance_level": "PARTIAL",
                "required_clauses": {"total": 5, "present": 2, "missing": 3},
                "recommended_clauses": {"total": 5, "present": 1, "missing": 4},
                "missing_clauses": [],
                "recommendations": ["Missing required clauses."],
            },
        }

        # Test markdown generation
        md = reporter.generate_markdown(mock_result)
        assert len(md) > 0
        assert "test.pdf" in md

        # Test HTML generation
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
            html_path = f.name
        try:
            path = reporter.generate_html(mock_result, html_path)
            assert os.path.exists(path)
            with open(path, "r") as f:
                content = f.read()
            assert "<html" in content
            assert "Contract Analysis Report" in content
        finally:
            os.unlink(html_path)
