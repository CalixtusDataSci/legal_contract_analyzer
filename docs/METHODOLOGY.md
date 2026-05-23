# Technical Methodology

## Architecture Overview

Legal Contract Analyzer uses a **hybrid NLP approach** combining legal domain expertise with computational linguistics. The architecture follows a modular pipeline design:

```
PDF Input -> Text Extraction -> Clause Classification -> Risk Analysis -> Compliance Check -> Report
```

## 1. Text Extraction

### PDF Parsing Strategy
- **Primary:** `pdfplumber` -- preserves layout for accurate text flow
- **Fallback:** `pypdf` (modern replacement for deprecated `PyPDF2`) -- reliable extraction for standard PDFs
- **Post-processing:** Text normalization pipeline to handle:
  - Broken words across line breaks
  - Excessive whitespace normalization
  - Page number / header removal
  - Line-ending standardization

## 2. Clause Classification

### Hybrid Detection Approach
The classifier uses a **three-layer detection system**:

#### Layer 1: Keyword Taxonomy
- 15 clause types with domain-specific keyword lists
- Keywords curated from legal domain expertise
- Case-insensitive matching with word boundaries

#### Layer 2: Sentence Segmentation
- Legal-aware boundary detection
- Handles abbreviations (Dr., Corp., Inc., Ltd., etc.)
- Preserves section numbering patterns (1.1, (a), etc.)

#### Layer 3: Confidence Scoring
```
confidence = (coverage * 0.5) + (length_score * 0.3) + (diversity * 0.2)
```
- Coverage: ratio of matched keywords to total keywords
- Length: text length normalized to 500 characters
- Diversity: ratio of unique matched keywords to total matches
- Bonus for 3+ keyword matches

### Clause Types Detected

| Category | Detection Method | Keywords |
|----------|-----------------|----------|
| Termination | Presence | terminate, cancel, material breach, notice period |
| Confidentiality | Presence | confidential, non-disclosure, proprietary, trade secret |
| Indemnification | Presence | indemnify, hold harmless, defend, claims arising |
| Governing Law | Presence | governed by, jurisdiction, venue, applicable law |
| Liability Cap | Presence/Absence | cap on liability, maximum liability, NOT present = high risk |
| Payment Terms | Presence | payment, fee, invoice, compensation, late payment |
| Intellectual Property | Presence | intellectual property, license, copyright, patent |
| Force Majeure | Presence/Absence | force majeure, act of god, beyond control |
| Non-Compete | Presence | non-compete, exclusivity, refrain from competing |
| Data Protection | Presence/Absence | GDPR, personal data, data processing, consent |
| Assignment | Presence | assignment, delegate, transfer, successors |
| Warranties | Presence | warrant, represent, guarantee, covenant |
| Dispute Resolution | Presence | arbitration, mediation, litigation, dispute |
| Amendment | Presence | amendment, modification, written amendment |
| Entire Agreement | Presence/Absence | entire agreement, supersedes, complete agreement |

## 3. Risk Analysis

### Three-Dimensional Scoring

Each clause is scored on three dimensions (1-5 scale):

#### Severity (weight: 50%)
Measures legal risk if the clause is enforced against you.

Detected through:
- Risk factor keyword patterns (e.g., "sole discretion", "without limitation")
- Absence checks (e.g., no liability cap detected)
- Severity ratings: 1 (minimal) to 5 (critical)

#### Ambiguity (weight: 30%)
Measures how unclear the clause language is.

Detected through:
- Vague language indicators: "reasonable", "appropriate", "material", "substantial"
- Subjective standards: "best efforts", "good faith", "industry standard"
- Open-ended language: "including but not limited to", "without limitation", "etc."

Scoring:
- 1 indicator = score 2
- 2 indicators = score 2
- 3-4 indicators = score 3
- 5-6 indicators = score 4
- 7+ indicators = score 5

#### Burden (weight: 20%)
Measures operational compliance burden.

Detected through:
- Keywords implying ongoing obligations: "monitor", "report", "document", "audit"
- Number of risk factors requiring active compliance

### Aggregation Formula

```
Overall = (severity * 0.50) + (ambiguity * 0.30) + (burden * 0.20)
```

Aggregate score across all clauses uses weighted average emphasizing highest-risk clauses:
- Top 4 clauses weighted at [30%, 20%, 15%, 10%]
- Remaining clauses share remaining 25%

### Risk Level Thresholds

| Level | Score Range | Action Required |
|-------|-------------|-----------------|
| Low | < 1.5 | Standard review |
| Medium | 1.5 - 2.5 | Enhanced review |
| High | 2.5 - 3.5 | Legal counsel advised |
| Critical | > 3.5 | Do not sign without attorney review |

## 4. Compliance Checking

### Rule-Based Validation

Compliance rules are defined per contract type:

#### General Commercial Agreement
- **Required:** termination, governing_law, liability_cap, dispute_resolution, entire_agreement
- **Recommended:** confidentiality, force_majeure, assignment, amendment, warranties

#### Employment Agreement
- **Required:** termination, confidentiality, intellectual_property, governing_law, data_protection
- **Recommended:** non_compete, dispute_resolution, liability_cap, force_majeure, amendment

#### NDA
- **Required:** confidentiality, term, governing_law, return_of_information, remedies
- **Recommended:** termination, dispute_resolution, data_protection

#### Service Agreement
- **Required:** payment_terms, termination, liability_cap, intellectual_property, governing_law, warranties
- **Recommended:** confidentiality, force_majeure, dispute_resolution, data_protection, service_levels

### Scoring
```
compliance_score = (required_ratio * 0.70) + (recommended_ratio * 0.30)
```

## 5. Report Generation

### HTML Report
- Professional styling with inline CSS
- Responsive layout for mobile/desktop
- Color-coded risk indicators
- Download-ready format

### Markdown Report
- Plain-text compatible
- GitHub-flavored markdown
- Suitable for email and document embedding

## Known Limitations

1. **Keyword Dependency:** Detection relies on keyword presence. Creative drafting or unusual phrasing may be missed.

2. **No ML Classification:** Current version uses rule-based detection. Transformer-based models (BERT/RoBERTa fine-tuned on legal text) would improve accuracy.

3. **English Only:** Only processes English-language contracts.

4. **PDF Only:** Supports PDF input. Word documents require conversion.

5. **Context Blindness:** Does not understand the broader business context or relationship between parties.

## Future Enhancements

- [ ] Fine-tuned BERT model for clause classification
- [ ] Named Entity Recognition for party identification
- [ ] Contract comparison/diff engine
- [ ] Multi-language support
- [ ] Integration with document management systems
- [ ] FastAPI REST service
- [ ] Batch processing for contract portfolios

---

*Methodology Version 1.0 | May 2026*
