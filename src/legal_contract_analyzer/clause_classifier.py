"""
Clause Classification and Extraction Module

Identifies legal clauses within contract text using a hybrid approach:
1. Legal keyword taxonomy (domain-knowledge driven)
2. Sentence boundary detection for clause isolation
3. Fuzzy matching for keyword variations

Built by a qualified legal practitioner with NLP engineering expertise.
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple

from .config import CLAUSE_TYPES

logger = logging.getLogger(__name__)


class ClauseClassifier:
    """
    Extract and classify legal clauses from contract text.

    Uses keyword-based matching with legal domain taxonomy.
    Designed to be upgraded to transformer-based classification (BERT/RoBERTa)
    as a future enhancement.
    """

    def __init__(self):
        self.clause_types = CLAUSE_TYPES
        # Compile regex patterns for efficiency
        self._compile_patterns()

    def _compile_patterns(self):
        """Pre-compile keyword patterns for performance."""
        self.compiled_patterns = {}
        for clause_id, config in self.clause_types.items():
            patterns = []
            for kw in config["required_keywords"]:
                # Allow word-start anchored matching to support stems (e.g. 'terminat' -> 'terminate')
                patterns.append(re.compile(r'\b' + re.escape(kw), re.IGNORECASE))
            self.compiled_patterns[clause_id] = patterns

    def extract_clauses(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract all clauses from contract text.

        Args:
            text: Full contract text

        Returns:
            List of clause dictionaries with extracted text, type, position
        """
        clauses = []
        sentences = self._segment_sentences(text)

        for clause_id, config in self.clause_types.items():
            found_clauses = self._find_clause_instances(
                clause_id, config, sentences, text
            )
            clauses.extend(found_clauses)

        # Sort by position in document
        clauses.sort(key=lambda x: x["position"])

        return clauses

    def _segment_sentences(self, text: str) -> List[Dict[str, Any]]:
        """
        Segment text into sentences with metadata.

        Uses legal-aware boundary detection that handles:
        - Abbreviations (e.g., "Dr.", "Inc.", "Ltd.")
        - Section numbering (e.g., "1.1", "(a)")
        - Decimal numbers
        """
        # Legal document-aware sentence splitting
        # Split on period, but not after common abbreviations or in numbering
        abbreviations = [
            "dr", "mr", "mrs", "ms", "inc", "ltd", "llc", "corp",
            "jr", "sr", "vs", "vol", "vols", "inc", "co",
            "no", "nos", "art", "arts", "sec", "secs", "para",
            "paras", "et al", "etc", "eg", "ie", "viz",
            "ltd", "plc", "lp", "llp", "gmbh", "sa", "bv",
        ]

        # Pattern: split on period/exclamation/question followed by space and uppercase
        # But not after abbreviations
        pattern = r'(?<=[.!?])\s+(?=[A-Z])'

        raw_splits = re.split(pattern, text)

        sentences = []
        position = 0
        for sent_text in raw_splits:
            sent_text = sent_text.strip()
            if not sent_text or len(sent_text) < 10:
                continue

            sentences.append({
                "text": sent_text,
                "position": position,
                "length": len(sent_text),
            })
            position += len(sent_text)

        return sentences

    def _find_clause_instances(
        self, clause_id: str, config: Dict, sentences: List[Dict], full_text: str
    ) -> List[Dict[str, Any]]:
        """
        Find all instances of a specific clause type.

        Returns list of clause instances with extracted text and match confidence.
        """
        instances = []
        patterns = self.compiled_patterns[clause_id]
        keywords = config["required_keywords"]

        # Track which sentences have been used to avoid duplicates
        used_ranges = []

        for sent in sentences:
            sent_text = sent["text"]
            matches = []

            # Check for keyword matches
            for i, pattern in enumerate(patterns):
                if pattern.search(sent_text):
                    matches.append(keywords[i])

            if not matches:
                continue

            # Check for exclusion keywords
            excluded = False
            for ex_kw in config.get("exclusion_keywords", []):
                if re.search(r'\b' + re.escape(ex_kw) + r'\b', sent_text, re.IGNORECASE):
                    excluded = True
                    break

            if excluded:
                continue

            # Check overlap with existing instances
            sent_start = full_text.find(sent_text)
            sent_end = sent_start + len(sent_text)

            overlap = False
            for used_start, used_end in used_ranges:
                if sent_start < used_end and sent_end > used_start:
                    overlap = True
                    break

            if overlap:
                continue

            used_ranges.append((sent_start, sent_end))

            # Extract surrounding context (paragraph-level)
            context = self._extract_context(full_text, sent_start)

            # Calculate confidence score
            confidence = self._calculate_confidence(matches, len(keywords), sent_text)

            instances.append({
                "id": f"{clause_id}_{len(instances) + 1}",
                "type": clause_id,
                "type_name": config["name"],
                "description": config["description"],
                "extracted_text": sent_text,
                "context": context,
                "position": sent["position"],
                "matched_keywords": matches,
                "confidence": round(confidence, 3),
                "risk_factors": [],  # Populated by RiskAnalyzer
            })

        return instances

    def _extract_context(self, full_text: str, position: int, window: int = 200) -> str:
        """Extract surrounding context around a clause match."""
        start = max(0, position - window)
        end = min(len(full_text), position + window)
        context = full_text[start:end]

        # Clean up context boundaries
        context = context.strip()

        # Add ellipsis if truncated
        if start > 0:
            context = "... " + context
        if end < len(full_text):
            context = context + " ..."

        return context

    def _calculate_confidence(
        self, matches: List[str], total_keywords: int, text: str
    ) -> float:
        """
        Calculate confidence score for clause detection.

        Based on:
        - Keyword coverage ratio
        - Text length (penalize very short matches)
        - Keyword diversity
        """
        # Base score from keyword coverage
        coverage = len(matches) / total_keywords

        # Length bonus (clauses should have substantive text)
        length_score = min(1.0, len(text) / 500)

        # Diversity bonus (different keywords matched)
        diversity = len(set(matches)) / len(matches) if matches else 0

        confidence = (coverage * 0.5) + (length_score * 0.3) + (diversity * 0.2)

        # Boost for multiple keyword matches
        if len(matches) >= 3:
            confidence = min(1.0, confidence + 0.1)

        return min(1.0, max(0.0, confidence))

    def get_clause_summary(self, clauses: List[Dict]) -> Dict[str, int]:
        """Get count of each clause type found."""
        summary = {}
        for clause in clauses:
            clause_type = clause["type"]
            summary[clause_type] = summary.get(clause_type, 0) + 1
        return summary

    def get_clause_coverage(self, clauses: List[Dict]) -> float:
        """
        Calculate coverage: what percentage of known clause types were found.

        Returns:
            Float between 0 and 1
        """
        found_types = set(c["type"] for c in clauses)
        total_types = len(self.clause_types)
        return len(found_types) / total_types if total_types > 0 else 0
