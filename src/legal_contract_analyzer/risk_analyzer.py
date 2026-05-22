"""
Risk Analysis Engine

Quantitative risk assessment for legal contract clauses.

Each clause is scored across three dimensions:
- Severity (1-5): Legal risk if enforced against you
- Ambiguity (1-5): How unclear or open to interpretation
- Burden (1-5): Operational burden of compliance

Overall score uses weighted combination with severity at 50%.
"""

import re
import logging
from typing import List, Dict, Any

from .config import CLAUSE_TYPES, RISK_WEIGHTS, RISK_THRESHOLDS, SEVERITY_LABELS

logger = logging.getLogger(__name__)


class RiskAnalyzer:
    """
    Analyze risk levels of extracted contract clauses.

    Combines rule-based risk factor detection with configurable
    scoring weights to produce quantitative risk assessments.
    """

    def __init__(self):
        self.risk_weights = RISK_WEIGHTS
        self.thresholds = RISK_THRESHOLDS
        self.severity_labels = SEVERITY_LABELS

    def assess(self, clauses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Perform full risk assessment on all extracted clauses.

        Args:
            clauses: List of extracted clause dictionaries

        Returns:
            Complete risk assessment with per-clause and aggregate scores
        """
        if not clauses:
            return {
                "overall_score": 0.0,
                "risk_level": "low",
                "total_clauses": 0,
                "high_risk_clauses": 0,
                "critical_risk_clauses": 0,
                "clause_assessments": [],
                "risk_distribution": {},
                "recommendations": ["No clauses detected for risk analysis"],
            }

        clause_assessments = []
        risk_counts = {"low": 0, "medium": 0, "high": 0, "critical": 0}

        for clause in clauses:
            assessment = self._assess_clause(clause)
            clause_assessments.append(assessment)
            risk_counts[assessment["risk_level"]] += 1

        overall_score = self._calculate_overall_score(clause_assessments)
        risk_level = self._get_risk_level(overall_score)

        high_risk = risk_counts["high"] + risk_counts["critical"]
        critical_risk = risk_counts["critical"]

        recommendations = self._generate_recommendations(
            clause_assessments, risk_counts
        )

        return {
            "overall_score": round(overall_score, 2),
            "risk_level": risk_level,
            "risk_level_label": self.severity_labels.get(
                int(overall_score), "Unknown"
            ),
            "total_clauses": len(clauses),
            "high_risk_clauses": high_risk,
            "critical_risk_clauses": critical_risk,
            "clause_assessments": clause_assessments,
            "risk_distribution": risk_counts,
            "recommendations": recommendations,
        }

    def _assess_clause(self, clause: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess risk for a single clause.

        Detects risk factors, scores each dimension, and produces
        overall clause risk score.
        """
        clause_type = clause["type"]
        clause_text = clause["extracted_text"].lower()
        config = CLAUSE_TYPES.get(clause_type, {})
        risk_factors_config = config.get("risk_factors", {})

        detected_risks = []

        for risk_name, risk_config in risk_factors_config.items():
            detected = self._detect_risk_factor(risk_config, clause_text)
            if detected:
                detected_risks.append({
                    "name": risk_name,
                    "description": risk_config["description"],
                    "severity": risk_config["severity"],
                    "matched_pattern": detected,
                })

        # Calculate dimension scores
        severity = self._calculate_severity(detected_risks, config)
        ambiguity = self._calculate_ambiguity(detected_risks, clause_text)
        burden = self._calculate_burden(detected_risks, config)

        # Weighted overall score
        overall = (
            severity * self.risk_weights["severity"]
            + ambiguity * self.risk_weights["ambiguity"]
            + burden * self.risk_weights["burden"]
        )

        risk_level = self._get_risk_level(overall)

        return {
            "clause_id": clause["id"],
            "clause_type": clause_type,
            "clause_name": clause["type_name"],
            "extracted_text_preview": clause["extracted_text"][:300],
            "severity": round(severity, 2),
            "ambiguity": round(ambiguity, 2),
            "burden": round(burden, 2),
            "overall_score": round(overall, 2),
            "risk_level": risk_level,
            "detected_risks": detected_risks,
            "num_risk_factors": len(detected_risks),
        }

    def _detect_risk_factor(
        self, risk_config: Dict[str, Any], clause_text: str
    ) -> Any:
        """
        Detect if a risk factor is present in clause text.

        Returns the matched pattern if found, None otherwise.
        """
        if risk_config.get("absence_check", False):
            # For absence checks, risk is present if pattern is NOT found
            patterns = risk_config.get("patterns", [])
            if not patterns:
                return None
            found_any = False
            for pattern in patterns:
                if re.search(r'\b' + re.escape(pattern.lower()) + r'\b', clause_text):
                    found_any = True
                    break
            return "absence" if not found_any else None

        # Standard presence check
        for pattern in risk_config.get("patterns", []):
            if re.search(r'\b' + re.escape(pattern.lower()) + r'\b', clause_text):
                return pattern

        return None

    def _calculate_severity(
        self, detected_risks: List[Dict], config: Dict
    ) -> float:
        """Calculate severity score (1-5) based on detected risk factors."""
        if not detected_risks:
            return 1.5  # Default low-medium

        # Average severity of detected risks, weighted by severity
        total_severity = sum(r["severity"] for r in detected_risks)
        avg = total_severity / len(detected_risks)

        # Boost if multiple severe risks
        if len(detected_risks) >= 3:
            avg = min(5.0, avg + 0.5)

        return round(min(5.0, max(1.0, avg)), 2)

    def _calculate_ambiguity(
        self, detected_risks: List[Dict], clause_text: str
    ) -> float:
        """
        Calculate ambiguity score (1-5).

        Based on:
        - Vague language indicators
        - Undefined terms
        - Subjective standards
        """
        ambiguity_indicators = [
            r'\breasonable\b', r'\bappropriate\b', r'\bmaterial\b',
            r'\bsubstantial\b', r'\bto the extent\b', r'\bas determined',
            r'\bin the discretion\b', r'\bsatisfactory\b',
            r'\bgood faith\b', r'\bbest efforts\b',
            r'\bcommercially reasonable\b', r'\bindustry standard\b',
            r'\betc\b', r'\bincluding but not limited to\b',
            r'\bwithout limitation\b', r'\bother\b',
        ]

        ambiguity_count = 0
        for indicator in ambiguity_indicators:
            if re.search(indicator, clause_text, re.IGNORECASE):
                ambiguity_count += 1

        # Scale: 0 indicators = 1, 1-2 = 2, 3-4 = 3, 5-6 = 4, 7+ = 5
        if ambiguity_count == 0:
            return 1.0
        elif ambiguity_count <= 2:
            return 2.0
        elif ambiguity_count <= 4:
            return 3.0
        elif ambiguity_count <= 6:
            return 4.0
        else:
            return 5.0

    def _calculate_burden(self, detected_risks: List[Dict], config: Dict) -> float:
        """
        Calculate compliance burden score (1-5).

        Based on operational requirements implied by the clause.
        """
        # Count risk factors that imply operational burden
        burden_keywords = [
            "monitor", "report", "notify", "maintain",
            "document", "track", "audit", "comply",
            "filing", "registration", "training",
        ]

        burden_count = 0
        for risk in detected_risks:
            desc = risk.get("description", "").lower()
            for kw in burden_keywords:
                if kw in desc:
                    burden_count += 1

        # More risk factors = higher burden
        if burden_count == 0:
            return 1.5
        elif burden_count <= 2:
            return 2.5
        elif burden_count <= 4:
            return 3.5
        elif burden_count <= 6:
            return 4.5
        else:
            return 5.0

    def _calculate_overall_score(
        self, assessments: List[Dict[str, Any]]
    ) -> float:
        """
        Calculate aggregate risk score across all clauses.

        Weighted average with emphasis on highest-risk clauses.
        """
        if not assessments:
            return 0.0

        scores = [a["overall_score"] for a in assessments]

        # Weight highest-risk clauses more heavily
        scores.sort(reverse=True)
        weights = [0.3, 0.2, 0.15, 0.1] + [0.25 / max(1, len(scores) - 4)] * max(
            0, len(scores) - 4
        )

        # Normalize weights
        weights = weights[: len(scores)]
        total_weight = sum(weights)
        weights = [w / total_weight for w in weights]

        return sum(s * w for s, w in zip(scores, weights))

    def _get_risk_level(self, score: float) -> str:
        """Convert numeric score to risk level category."""
        if score >= self.thresholds["critical"]:
            return "critical"
        elif score >= self.thresholds["high"]:
            return "high"
        elif score >= self.thresholds["medium"]:
            return "medium"
        else:
            return "low"

    def _generate_recommendations(
        self,
        assessments: List[Dict[str, Any]],
        risk_counts: Dict[str, int],
    ) -> List[str]:
        """Generate actionable recommendations based on risk assessment."""
        recommendations = []

        critical_clauses = [a for a in assessments if a.get("risk_level") == "critical"]
        high_clauses = [a for a in assessments if a.get("risk_level") == "high"]

        if critical_clauses:
            clause_names = ", ".join(
                set(c.get("clause_name", c.get("clause_type", "unknown")) for c in critical_clauses[:3])
            )
            recommendations.append(
                f"URGENT: {len(critical_clauses)} critical risk clause(s) detected. "
                f"Priority review needed for: {clause_names}. "
                "Consider legal counsel before signing."
            )

        if high_clauses:
            clause_names = ", ".join(
                set(c.get("clause_name", c.get("clause_type", "unknown")) for c in high_clauses[:3])
            )
            recommendations.append(
                f"HIGH: {len(high_clauses)} high-risk clause(s) found in: "
                f"{clause_names}. Negotiate modifications or additional protections."
            )

        # Check for common patterns
        has_no_liability_cap = any(
            a["clause_type"] == "liability_cap"
            and any(
                r["name"] == "no_cap" for r in a.get("detected_risks", [])
            )
            for a in assessments
        )

        if has_no_liability_cap:
            recommendations.append(
                "LIABILITY: No liability cap detected. Unlimited exposure risk. "
                "Negotiate a maximum liability cap tied to contract value."
            )

        one_sided = [
            a for a in assessments
            if any(
                r["name"] in ["one_sided_termination", "unilateral_assignment",
                               "unilateral_amendment"]
                for r in a.get("detected_risks", [])
            )
        ]
        if one_sided:
            recommendations.append(
                "IMBALANCE: One-sided clauses detected favoring the counterparty. "
                "Seek mutual language to balance rights and obligations."
            )

        if not recommendations:
            recommendations.append(
                "Contract risk profile is acceptable. Standard legal review recommended."
            )

        return recommendations
