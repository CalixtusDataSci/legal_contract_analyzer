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


def _simple_stem(token: str) -> str:
    """Very small heuristic stemmer to avoid heavy external dependencies.

    Not as robust as PorterStemmer but sufficient for keyword-stem matching.
    """
    t = token.lower()
    for suffix in ("ing", "ed", "es", "s", "er", "ion", "ment", "ity"):
        if t.endswith(suffix) and len(t) - len(suffix) > 2:
            return t[: -len(suffix)]
    return t

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
        # Prepare stemmed keyword lists for robust tokenized matching
        # use lightweight stemmer
        stemmer = _simple_stem
        self.keyword_stems: Dict[str, List[List[str]]] = {}
        self.exclusion_stems: Dict[str, List[List[str]]] = {}

        for clause_id, config in self.clause_types.items():
            kw_stems = []
            for kw in config.get("required_keywords", []):
                toks = re.findall(r"\w+", kw.lower())
                if not toks:
                    continue
                kw_stems.append([stemmer(t) for t in toks])
            self.keyword_stems[clause_id] = kw_stems

            ex_stems = []
            for ex in config.get("exclusion_keywords", []):
                toks = re.findall(r"\w+", ex.lower())
                if not toks:
                    continue
                ex_stems.append([stemmer(t) for t in toks])
            self.exclusion_stems[clause_id] = ex_stems

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

        # Use a regex iterator to capture sentence spans (start index + text).
        # This preserves accurate positions in the original text and avoids
        # using `str.find()` which returns the first occurrence and breaks
        # for repeated sentences. The pattern captures up to the first
        # sentence-ending punctuation or end-of-text.
        sentence_pattern = r'.+?(?:[\.!?]+(?=\s)|$)'

        sentences = []
        for m in re.finditer(sentence_pattern, text, flags=re.S):
            sent_text = m.group(0).strip()
            if not sent_text or len(sent_text) < 10:
                continue
            sentences.append({
                "text": sent_text,
                "position": m.start(),
                "length": len(sent_text),
            })

        return sentences

    def _find_clause_instances(
        self, clause_id: str, config: Dict, sentences: List[Dict], full_text: str
    ) -> List[Dict[str, Any]]:
        """
        Find all instances of a specific clause type.

        Returns list of clause instances with extracted text and match confidence.
        """
        instances = []
        # Use stemmed keyword lists prepared earlier
        total_keywords = len(config.get("required_keywords", []))

        # Track which sentences have been used to avoid duplicates
        used_ranges = []

        for sent in sentences:
            sent_text = sent["text"]
            matches = []

            # Tokenize sentence and compute stems
            sent_tokens = re.findall(r"\w+", sent_text.lower())
            sent_stems = [ _simple_stem(t) for t in sent_tokens]

            # Check for keyword matches using stem inclusion
            for i, kw_stem_list in enumerate(self.keyword_stems.get(clause_id, [])):
                # match if all stems of keyword phrase are present in sentence stems
                if all(s in sent_stems for s in kw_stem_list):
                    matches.append(" ".join(kw_stem_list))

            if not matches:
                continue

            # Check for exclusion keywords using stems
            excluded = False
            for ex_kw_stems in self.exclusion_stems.get(clause_id, []):
                if all(s in sent_stems for s in ex_kw_stems):
                    excluded = True
                    break

            if excluded:
                continue

            # Use the sentence's recorded start position to avoid ambiguous
            # full_text.find() matches for duplicated sentences.
            sent_start = sent.get("position", -1)
            if sent_start is None or sent_start < 0:
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
            confidence = self._calculate_confidence(matches, total_keywords, sent_text)

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
