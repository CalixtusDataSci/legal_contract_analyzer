"""
Configuration module for Legal Contract Analyzer.

Defines clause types, risk weights, compliance rules, and legal keyword taxonomies.

This taxonomy is built from legal domain expertise combined with NLP best practices
for legal document processing.
"""

from typing import Dict, List, Any


# ============================================================
# CLAUSE TYPE DEFINITIONS
# Each clause has: name, description, keywords, risk factors
# ============================================================

CLAUSE_TYPES: Dict[str, Dict[str, Any]] = {
    "termination": {
        "name": "Termination Clause",
        "description": "Conditions under which the contract may be terminated",
        "required_keywords": [
            "terminat", "cancel", "end this agreement", "breach",
            "notice period", "without cause", "for cause",
            "effective date of termination", "material breach",
            "convenience", "survive termination",
        ],
        "exclusion_keywords": [
            "non-terminat", "interminable",
        ],
        "risk_factors": {
            "one_sided_termination": {
                "patterns": [
                    "sole discretion", "at will", "immediately",
                    "without cause", "without reason",
                ],
                "severity": 4,
                "description": "One party can terminate without mutual consent",
            },
            "no_notice_period": {
                "patterns": [
                    "effective immediately", "no notice",
                ],
                "severity": 5,
                "description": "No advance notice required for termination",
            },
            "short_notice": {
                "patterns": [
                    "seven days", "7 days", "14 days", "fourteen days",
                ],
                "severity": 3,
                "description": "Very short notice period",
            },
        },
        "severity_weight": 0.5,
        "ambiguity_weight": 0.3,
        "burden_weight": 0.2,
    },
    "confidentiality": {
        "name": "Confidentiality / NDA",
        "description": "Obligations to protect confidential information",
        "required_keywords": [
            "confidential", "non-disclosure", "proprietary",
            "trade secret", " sensitive information", "disclose",
            "third party", "unauthorized disclosure",
        ],
        "exclusion_keywords": [],
        "risk_factors": {
            "broad_definition": {
                "patterns": [
                    "all information", "any information", "whatsoever",
                    "directly or indirectly", "in any form",
                ],
                "severity": 3,
                "description": "Overly broad definition of confidential information",
            },
            "no_time_limit": {
                "patterns": [
                    "indefinite", "perpetual confidentiality",
                    "forever", "unlimited period",
                ],
                "severity": 4,
                "description": "Confidentiality obligation has no expiration",
            },
            "onerous_penalties": {
                "patterns": [
                    "liquidated damages", "injunctive relief",
                    "irreparable harm", "without limitation",
                ],
                "severity": 4,
                "description": "Severe penalties for breach",
            },
        },
        "severity_weight": 0.5,
        "ambiguity_weight": 0.25,
        "burden_weight": 0.25,
    },
    "indemnification": {
        "name": "Indemnification Clause",
        "description": "One party agrees to compensate the other for losses",
        "required_keywords": [
            "indemnif", "hold harmless", "defend",
            "liability arising from", "claims arising",
            "reimburse", "compensate for losses",
        ],
        "exclusion_keywords": [],
        "risk_factors": {
            "unlimited_indemnity": {
                "patterns": [
                    "all claims", "any and all", "without limitation",
                    "direct and indirect", "consequential",
                ],
                "severity": 5,
                "description": "No cap on indemnification exposure",
            },
            "broad_scope": {
                "patterns": [
                    "any third party claim", "all losses",
                    "regardless of cause", "even if",
                ],
                "severity": 4,
                "description": "Indemnity covers excessively broad claims",
            },
            "no_mitigation": {
                "patterns": [
                    "without duty to mitigate",
                ],
                "severity": 3,
                "description": "No obligation to minimize losses",
            },
        },
        "severity_weight": 0.55,
        "ambiguity_weight": 0.25,
        "burden_weight": 0.2,
    },
    "governing_law": {
        "name": "Governing Law & Jurisdiction",
        "description": "Which law governs the contract and dispute venue",
        "required_keywords": [
            "governed by", "governing law", "subject to the laws",
            "jurisdiction", "venue", "courts of",
            "dispute resolution", "applicable law",
        ],
        "exclusion_keywords": [],
        "risk_factors": {
            "unfavorable_jurisdiction": {
                "patterns": [
                    "delaware", "new york", "california",
                ],
                "severity": 2,
                "description": "Jurisdiction may favor the counterparty",
            },
            "no_arbitration_option": {
                "patterns": [],
                "severity": 2,
                "description": "No alternative dispute resolution mechanism",
                "absence_check": True,
            },
        },
        "severity_weight": 0.4,
        "ambiguity_weight": 0.3,
        "burden_weight": 0.3,
    },
    "liability_cap": {
        "name": "Limitation of Liability",
        "description": "Maximum financial exposure under the contract",
        "required_keywords": [
            "limitation of liability", "cap on liability",
            "maximum liability", "aggregate liability",
            "not exceed", "limited to", "liability shall not",
        ],
        "exclusion_keywords": [],
        "risk_factors": {
            "no_cap": {
                "patterns": [],
                "severity": 5,
                "description": "No liability cap specified",
                "absence_check": True,
            },
            "unlimited_indirect": {
                "patterns": [
                    "indirect damages", "consequential damages",
                    "loss of profits", "loss of revenue",
                ],
                "severity": 4,
                "description": "Unlimited liability for consequential damages",
            },
            "high_cap_amount": {
                "patterns": [
                    "fees paid", "amount paid", "annual fees",
                ],
                "severity": 2,
                "description": "Liability capped at fees paid (potentially low)",
            },
        },
        "severity_weight": 0.5,
        "ambiguity_weight": 0.2,
        "burden_weight": 0.3,
    },
    "payment_terms": {
        "name": "Payment Terms",
        "description": "Fee structure, invoicing, and payment obligations",
        "required_keywords": [
            "payment", "fee", "invoice", "compensation",
            "price", "cost", "amount payable", "due date",
            "late payment", "interest", "refund",
        ],
        "exclusion_keywords": [],
        "risk_factors": {
            "auto_renewal_payment": {
                "patterns": [
                    "automatic renewal", "auto-renew", "recurring",
                    "until cancelled",
                ],
                "severity": 3,
                "description": "Automatic payment renewal without explicit consent",
            },
            "late_penalties": {
                "patterns": [
                    "late fee", "interest rate", "penalty",
                    "service charge", "collection costs",
                ],
                "severity": 3,
                "description": "Penalties for late payment",
            },
            "upfront_payment": {
                "patterns": [
                    "payment in advance", "prepayment",
                    "before delivery", "upfront",
                ],
                "severity": 2,
                "description": "Full payment required before service delivery",
            },
        },
        "severity_weight": 0.4,
        "ambiguity_weight": 0.3,
        "burden_weight": 0.3,
    },
    "intellectual_property": {
        "name": "Intellectual Property",
        "description": "Ownership and licensing of IP created or used",
        "required_keywords": [
            "intellectual property", "ip rights", "ownership",
            "license", "patent", "copyright", "trademark",
            "work product", "derivative works", "moral rights",
        ],
        "exclusion_keywords": [],
        "risk_factors": {
            "ip_assignment": {
                "patterns": [
                    "assign all rights", "hereby assigns",
                    "transfer all", "exclusive ownership",
                ],
                "severity": 4,
                "description": "Creator must assign all IP rights",
            },
            "broad_license_grant": {
                "patterns": [
                    "perpetual license", "irrevocable",
                    "worldwide", "sublicense", "transferable",
                ],
                "severity": 3,
                "description": "Broad, irrevocable license granted",
            },
            "no_background_ip_protection": {
                "patterns": [
                    "background ip", "pre-existing",
                ],
                "severity": 3,
                "description": "Background/pre-existing IP may be captured",
            },
        },
        "severity_weight": 0.5,
        "ambiguity_weight": 0.25,
        "burden_weight": 0.25,
    },
    "force_majeure": {
        "name": "Force Majeure",
        "description": "Excuse from performance due to unforeseeable events",
        "required_keywords": [
            "force majeure", "act of god", "beyond control",
            "unforeseeable", "pandemic", "natural disaster",
            "government action", "excuse performance",
        ],
        "exclusion_keywords": [],
        "risk_factors": {
            "narrow_definition": {
                "patterns": [],
                "severity": 3,
                "description": "Force majeure clause has narrow or missing definition",
                "absence_check": True,
            },
            "no_relief_obligation": {
                "patterns": [],
                "severity": 2,
                "description": "No obligation to resume after force majeure ends",
                "absence_check": True,
            },
        },
        "severity_weight": 0.35,
        "ambiguity_weight": 0.35,
        "burden_weight": 0.3,
    },
    "non_compete": {
        "name": "Non-Compete / Exclusivity",
        "description": "Restrictions on competing activities",
        "required_keywords": [
            "non-compete", "non compete", "compete with",
            "exclusivity", "exclusive arrangement",
            "refrain from", "not engage",
        ],
        "exclusion_keywords": [],
        "risk_factors": {
            "broad_geographic_scope": {
                "patterns": [
                    "any jurisdiction", "worldwide", "any territory",
                    "throughout the world",
                ],
                "severity": 4,
                "description": "Non-compete applies globally",
            },
            "long_duration": {
                "patterns": [
                    "twelve months", "24 months", "two years",
                    "thirty-six months",
                ],
                "severity": 4,
                "description": "Extended non-compete period",
            },
            "broad_activity_scope": {
                "patterns": [
                    "any business", "similar business",
                    "related activities", "directly or indirectly",
                ],
                "severity": 4,
                "description": "Vague definition of competing activities",
            },
        },
        "severity_weight": 0.5,
        "ambiguity_weight": 0.25,
        "burden_weight": 0.25,
    },
    "data_protection": {
        "name": "Data Protection & Privacy",
        "description": "GDPR, data handling, and privacy compliance",
        "required_keywords": [
            "data protection", "gdpr", "personal data",
            "privacy", "data processing", "data controller",
            "data subject", "consent", "lawful basis",
            "data breach notification",
        ],
        "exclusion_keywords": [],
        "risk_factors": {
            "no_gdpr_compliance": {
                "patterns": [],
                "severity": 4,
                "description": "No GDPR compliance mechanism for EU data subjects",
                "absence_check": True,
            },
            "unlimited_data_use": {
                "patterns": [
                    "any purpose", "commercial purposes",
                    "marketing", "share with affiliates",
                ],
                "severity": 4,
                "description": "Broad rights to use personal data",
            },
            "weak_security": {
                "patterns": [],
                "severity": 3,
                "description": "No specified data security measures",
                "absence_check": True,
            },
        },
        "severity_weight": 0.5,
        "ambiguity_weight": 0.25,
        "burden_weight": 0.25,
    },
    "assignment": {
        "name": "Assignment & Delegation",
        "description": "Transfer of contractual rights to third parties",
        "required_keywords": [
            "assignment", "assign this agreement",
            "delegate", "transfer", "novation",
            "successors and assigns",
        ],
        "exclusion_keywords": [],
        "risk_factors": {
            "unilateral_assignment": {
                "patterns": [
                    "may assign", "sole discretion",
                ],
                "severity": 3,
                "description": "Counterparty can assign without consent",
            },
            "no_assignment_rights": {
                "patterns": [
                    "may not assign", "shall not transfer",
                ],
                "severity": 2,
                "description": "You cannot assign the contract",
            },
        },
        "severity_weight": 0.4,
        "ambiguity_weight": 0.3,
        "burden_weight": 0.3,
    },
    "warranties": {
        "name": "Warranties & Representations",
        "description": "Guarantees about facts, conditions, or performance",
        "required_keywords": [
            "warrant", "represent", "guarantee",
            "covenant", "assure", "promise",
            "materially comply", "fit for purpose",
        ],
        "exclusion_keywords": [],
        "risk_factors": {
            "broad_warranties": {
                "patterns": [
                    "all applicable laws", "industry standard",
                    "best practices", "highest quality",
                ],
                "severity": 3,
                "description": "Overly broad warranty obligations",
            },
            "no_warranty_disclaimer": {
                "patterns": [],
                "severity": 2,
                "description": "No limitation on implied warranties",
                "absence_check": True,
            },
        },
        "severity_weight": 0.4,
        "ambiguity_weight": 0.3,
        "burden_weight": 0.3,
    },
    "dispute_resolution": {
        "name": "Dispute Resolution",
        "description": "How conflicts will be resolved (arbitration, mediation, litigation)",
        "required_keywords": [
            "arbitration", "mediate", "dispute resolution",
            "good faith negotiation", "expert determination",
            "litigation", "court proceedings",
        ],
        "exclusion_keywords": [],
        "risk_factors": {
            "mandatory_arbitration": {
                "patterns": [
                    "binding arbitration", "waive right to jury",
                    "waive class action",
                ],
                "severity": 3,
                "description": "Mandatory arbitration waives court rights",
            },
            "unfavorable_venue": {
                "patterns": [
                    "venue shall be", "exclusive jurisdiction",
                ],
                "severity": 2,
                "description": "Disputes must be resolved in counterparty's jurisdiction",
            },
            "high_arbitration_costs": {
                "patterns": [
                    "icc rules", "lcia", "party shall bear",
                ],
                "severity": 3,
                "description": "Arbitration may be expensive",
            },
        },
        "severity_weight": 0.4,
        "ambiguity_weight": 0.3,
        "burden_weight": 0.3,
    },
    "amendment": {
        "name": "Amendment Clause",
        "description": "How the contract can be modified",
        "required_keywords": [
            "amendment", "modif", "written amendment",
            "change", "variation", "no oral modification",
        ],
        "exclusion_keywords": [],
        "risk_factors": {
            "unilateral_amendment": {
                "patterns": [
                    "we may update", "subject to change",
                    "from time to time", "post notice",
                ],
                "severity": 4,
                "description": "One party can amend without mutual consent",
            },
            "no_notification_requirement": {
                "patterns": [],
                "severity": 3,
                "description": "No requirement to notify of amendments",
                "absence_check": True,
            },
        },
        "severity_weight": 0.45,
        "ambiguity_weight": 0.25,
        "burden_weight": 0.3,
    },
    "entire_agreement": {
        "name": "Entire Agreement / Merger Clause",
        "description": "States this contract supersedes all prior agreements",
        "required_keywords": [
            "entire agreement", "merger clause", "supersedes",
            "complete agreement", "entire understanding",
            "prior agreements", "written or oral",
        ],
        "exclusion_keywords": [],
        "risk_factors": {
            "no_clause": {
                "patterns": [],
                "severity": 2,
                "description": "No entire agreement clause",
                "absence_check": True,
            },
        },
        "severity_weight": 0.3,
        "ambiguity_weight": 0.35,
        "burden_weight": 0.35,
    },
}

# ============================================================
# RISK SCORING WEIGHTS
# ============================================================

RISK_WEIGHTS = {
    "severity": 0.50,   # Legal risk if enforced against you
    "ambiguity": 0.30,  # How unclear/open to interpretation
    "burden": 0.20,     # Operational burden of compliance
}

# Risk level thresholds
RISK_THRESHOLDS = {
    "low": 1.5,
    "medium": 2.0,
    "high": 3.0,
    "critical": 4.5,
}

# ============================================================
# COMPLIANCE RULES BY CONTRACT TYPE
# ============================================================

COMPLIANCE_RULES: Dict[str, Dict[str, Any]] = {
    "general": {
        "name": "General Commercial Agreement",
        "required_clauses": [
            "termination", "governing_law", "liability_cap",
            "dispute_resolution", "entire_agreement",
        ],
        "recommended_clauses": [
            "confidentiality", "force_majeure", "assignment",
            "amendment", "warranties",
        ],
    },
    "employment": {
        "name": "Employment Agreement",
        "required_clauses": [
            "termination", "confidentiality", "intellectual_property",
            "governing_law", "data_protection",
        ],
        "recommended_clauses": [
            "non_compete", "dispute_resolution", "liability_cap",
            "force_majeure", "amendment",
        ],
    },
    "nda": {
        "name": "Non-Disclosure Agreement",
        "required_clauses": [
            "confidentiality", "term", "governing_law",
            "return_of_information", "remedies",
        ],
        "recommended_clauses": [
            "termination", "dispute_resolution", "data_protection",
        ],
    },
    "service": {
        "name": "Service Agreement / SLA",
        "required_clauses": [
            "payment_terms", "termination", "liability_cap",
            "intellectual_property", "governing_law", "warranties",
        ],
        "recommended_clauses": [
            "confidentiality", "force_majeure", "dispute_resolution",
            "data_protection", "service_levels",
        ],
    },
}

# ============================================================
# REPORTING CONFIGURATION
# ============================================================

REPORT_COLORS = {
    "low": "#4CAF50",      # Green
    "medium": "#FF9800",   # Orange
    "high": "#F44336",     # Red
    "critical": "#B71C1C", # Dark Red
    "missing": "#9E9E9E",  # Gray
    "info": "#2196F3",     # Blue
}

SEVERITY_LABELS = {
    1: "Minimal",
    2: "Low",
    3: "Moderate",
    4: "High",
    5: "Critical",
}
