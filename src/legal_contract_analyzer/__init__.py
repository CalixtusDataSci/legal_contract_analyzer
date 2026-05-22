"""
Legal Contract Analyzer - AI-Powered Legal Document Analysis

A production-ready Python application for extracting legal clauses,
analyzing contract risk, and generating compliance reports using NLP.

Author: Nwaeke Calixtus Ifeanyi, Esq.
"""

from .extractor import PDFExtractor
from .clause_classifier import ClauseClassifier
from .risk_analyzer import RiskAnalyzer
from .compliance_checker import ComplianceChecker
from .report_generator import ReportGenerator
from .config import CLAUSE_TYPES, RISK_WEIGHTS, COMPLIANCE_RULES


class ContractAnalyzer:
    """Main orchestrator class for contract analysis pipeline."""

    def __init__(self):
        self.extractor = PDFExtractor()
        self.classifier = ClauseClassifier()
        self.risk_analyzer = RiskAnalyzer()
        self.compliance = ComplianceChecker()
        self.reporter = ReportGenerator()

    def analyze(self, pdf_path: str, contract_type: str = "general") -> dict:
        """
        Run full contract analysis pipeline.

        Args:
            pdf_path: Path to contract PDF file
            contract_type: Type of contract (general, employment, nda, service)

        Returns:
            Complete analysis result dictionary
        """
        text = self.extractor.extract(pdf_path)
        clauses = self.classifier.extract_clauses(text)
        risk_assessment = self.risk_analyzer.assess(clauses)
        compliance_result = self.compliance.check(clauses, contract_type)

        return {
            "filename": pdf_path.split("/")[-1],
            "text_length": len(text),
            "clauses_found": len(clauses),
            "clauses": clauses,
            "risk_summary": risk_assessment,
            "compliance": compliance_result,
        }

    def generate_report(self, result: dict, output_path: str = "report.html") -> str:
        """Generate HTML report from analysis results."""
        return self.reporter.generate_html(result, output_path)


__version__ = "1.0.0"
__author__ = "Nwaeke Calixtus Ifeanyi, Esq."
__all__ = [
    "ContractAnalyzer",
    "PDFExtractor",
    "ClauseClassifier",
    "RiskAnalyzer",
    "ComplianceChecker",
    "ReportGenerator",
    "CLAUSE_TYPES",
    "RISK_WEIGHTS",
    "COMPLIANCE_RULES",
]
