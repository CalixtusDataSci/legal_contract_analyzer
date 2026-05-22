"""
Compliance Checking Module

Validates presence of legally essential clauses based on contract type.
Flags missing clauses that create regulatory or legal exposure.

Supports contract types: general, employment, nda, service
"""

from typing import List, Dict, Any

from .config import COMPLIANCE_RULES, CLAUSE_TYPES


class ComplianceChecker:
    """
    Check contract compliance against regulatory requirements.

    Ensures essential clauses are present based on contract type
    and flags gaps that could create legal exposure.
    """

    def __init__(self):
        self.rules = COMPLIANCE_RULES

    def check(
        self, clauses: List[Dict[str, Any]], contract_type: str = "general"
    ) -> Dict[str, Any]:
        """
        Run compliance check against contract type requirements.

        Args:
            clauses: Extracted clauses
            contract_type: Type of contract for rule matching

        Returns:
            Compliance report with gaps, coverage score, recommendations
        """
        rules = self.rules.get(contract_type, self.rules["general"])

        # Find which clauses are present
        found_types = set(c["type"] for c in clauses)

        # Check required clauses
        required_missing = []
        required_present = []
        for req in rules["required_clauses"]:
            if req in found_types:
                required_present.append(req)
            else:
                clause_info = CLAUSE_TYPES.get(req, {})
                required_missing.append({
                    "clause_type": req,
                    "clause_name": clause_info.get("name", req),
                    "importance": "REQUIRED",
                    "risk_of_absence": self._get_absence_risk(req),
                    "recommendation": self._get_recommendation(req),
                })

        # Check recommended clauses
        recommended_missing = []
        recommended_present = []
        for rec in rules["recommended_clauses"]:
            if rec in found_types:
                recommended_present.append(rec)
            else:
                clause_info = CLAUSE_TYPES.get(rec, {})
                recommended_missing.append({
                    "clause_type": rec,
                    "clause_name": clause_info.get("name", rec),
                    "importance": "RECOMMENDED",
                    "risk_of_absence": self._get_absence_risk(rec),
                    "recommendation": self._get_recommendation(rec),
                })

        # Calculate compliance score
        total_required = len(rules["required_clauses"])
        total_recommended = len(rules["recommended_clauses"])

        if total_required > 0:
            required_score = len(required_present) / total_required
        else:
            required_score = 1.0

        if total_recommended > 0:
            recommended_score = len(recommended_present) / total_recommended
        else:
            recommended_score = 1.0

        # Weighted: required is 70%, recommended is 30%
        overall_score = (required_score * 0.7) + (recommended_score * 0.3)

        # Compliance level
        compliance_level = self._get_compliance_level(
            overall_score, len(required_missing)
        )

        all_missing = required_missing + recommended_missing

        return {
            "contract_type": contract_type,
            "contract_type_name": rules["name"],
            "compliance_score": round(overall_score * 100, 1),
            "compliance_level": compliance_level,
            "required_clauses": {
                "total": total_required,
                "present": len(required_present),
                "missing": len(required_missing),
            },
            "recommended_clauses": {
                "total": total_recommended,
                "present": len(recommended_present),
                "missing": len(recommended_missing),
            },
            "missing_clauses": all_missing,
            "present_clauses": required_present + recommended_present,
            "recommendations": self._generate_compliance_recommendations(
                required_missing, recommended_missing, overall_score
            ),
        }

    def _get_absence_risk(self, clause_type: str) -> str:
        """Get risk description for missing clause type."""
        risk_map = {
            "termination": "HIGH: Contract may be difficult to exit without clear termination provisions",
            "governing_law": "HIGH: Disputes may be subject to unpredictable jurisdiction",
            "liability_cap": "CRITICAL: Unlimited financial exposure for breaches",
            "confidentiality": "HIGH: No protection for sensitive information shared",
            "intellectual_property": "HIGH: IP ownership disputes likely without clear assignment",
            "data_protection": "HIGH: Potential GDPR/regulatory violations without privacy provisions",
            "non_compete": "MEDIUM: No post-employment restrictions (or excessive ones)",
            "force_majeure": "MEDIUM: No relief for unforeseeable circumstances",
            "dispute_resolution": "HIGH: Costly litigation without ADR alternatives",
            "payment_terms": "HIGH: Payment disputes likely without clear terms",
            "amendment": "MEDIUM: Contract can be changed without formal process",
            "warranties": "MEDIUM: No guarantees about quality or performance",
            "assignment": "MEDIUM: Rights may be transferred without consent",
            "entire_agreement": "LOW-MEDIUM: Prior agreements may still be enforceable",
            "indemnification": "HIGH: No protection against third-party claims",
        }
        return risk_map.get(clause_type, "MEDIUM: Missing clause creates potential legal gap")

    def _get_recommendation(self, clause_type: str) -> str:
        """Get specific recommendation for adding a missing clause."""
        rec_map = {
            "termination": "Add termination clause with mutual notice period (typically 30-90 days)",
            "governing_law": "Specify governing law and jurisdiction (e.g., 'Laws of Nigeria')",
            "liability_cap": "Negotiate liability cap at 12 months of fees paid or specific amount",
            "confidentiality": "Include mutual confidentiality obligations with 2-5 year duration",
            "intellectual_property": "Clarify IP ownership: background IP stays with creator, foreground IP assigns to client",
            "data_protection": "Add GDPR-compliant data processing clause with security measures",
            "non_compete": "If included, limit to 6-12 months and specific geographic scope",
            "force_majeure": "Include standard force majeure with pandemic, natural disaster, government action",
            "dispute_resolution": "Add mediation followed by arbitration clause",
            "payment_terms": "Specify fee amount, invoicing schedule, due dates, and late payment interest",
            "amendment": "Require written amendment signed by both parties",
            "warranties": "Include reasonable warranties with explicit disclaimers for implied warranties",
            "assignment": "Require mutual consent for assignment except to affiliates",
            "entire_agreement": "Add merger clause superseding all prior agreements",
            "indemnification": "Include mutual indemnification with carve-outs for gross negligence",
        }
        return rec_map.get(clause_type, f"Add standard {clause_type} clause per industry practice")

    def _get_compliance_level(
        self, score: float, required_missing: int
    ) -> str:
        """Determine compliance level from score."""
        if required_missing > 0:
            if score >= 0.6:
                return "PARTIAL (Required clauses missing)"
            elif score >= 0.4:
                return "INSUFFICIENT (Multiple required clauses missing)"
            else:
                return "NON-COMPLIANT (Critical clauses absent)"

        if score >= 0.9:
            return "FULLY COMPLIANT"
        elif score >= 0.75:
            return "COMPLIANT (Minor recommended clauses missing)"
        elif score >= 0.6:
            return "ACCEPTABLE (Several recommended clauses missing)"
        else:
            return "PARTIAL (Many recommended clauses missing)"

    def _generate_compliance_recommendations(
        self,
        required_missing: List[Dict],
        recommended_missing: List[Dict],
        score: float,
    ) -> List[str]:
        """Generate compliance-focused recommendations."""
        recommendations = []

        if required_missing:
            clause_names = ", ".join(
                c["clause_name"] for c in required_missing[:3]
            )
            recommendations.append(
                f"COMPLIANCE: {len(required_missing)} required clause(s) missing: "
                f"{clause_names}. These must be added before signing."
            )

        if recommended_missing and len(recommended_missing) > 3:
            recommendations.append(
                f"RECOMMENDED: {len(recommended_missing)} recommended clauses missing. "
                "Consider adding for stronger legal protection."
            )

        if score < 0.5:
            recommendations.append(
                "CRITICAL: Contract has significant compliance gaps. "
                "Legal review strongly advised before execution."
            )

        if not recommendations:
            recommendations.append(
                "Contract meets compliance requirements for its type."
            )

        return recommendations

    def list_contract_types(self) -> Dict[str, str]:
        """Return available contract types and their descriptions."""
        return {
            key: rules["name"]
            for key, rules in self.rules.items()
        }
