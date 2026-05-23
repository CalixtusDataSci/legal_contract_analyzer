# Legal Contract Analyzer

> AI-Powered Legal Document Analysis for Risk Detection and Clause Extraction

**Author:** Nwaeke Calixtus Ifeanyi, Esq. | Legal Practitioner & AI Data Scientist

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://github.com/CalixtusDataSci/legal-contract-analyzer/actions/workflows/tests.yml/badge.svg)](.github/workflows/tests.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Coverage](https://img.shields.io/badge/coverage-%E2%89%A580%25-green.svg)]()

---

## Recent Changes (May 2026)

- Restored educational notebooks under `notebooks/` (previously removed). Notebook outputs were stripped to keep repository size small and avoid large diffs.
- Replaced deprecated `PyPDF2` with `pypdf` throughout the codebase and dependency manifests (`requirements.txt`, `pyproject.toml`). The extractor now prefers `pdfplumber` and falls back to `pypdf`.
- Cleaned repository clutter: removed duplicate virtualenv `.venv-1` and test caches.
- Test status: all tests pass locally (46 passed).

## Brutal Audit Summary (short)

- **Tests & Stability:** Tests are solid and pass — good engineering signal. Maintain the test coverage as features grow.
- **Technical Debt:** Rule-based detection is serviceable for education but will miss non-standard drafting. Plan for a transformer-based classifier for production-quality recall/precision.
- **Performance Risks:** Ensure spaCy model is loaded only once; avoid repeated model loads in long-running processes. PDF parsing is I/O bound—benchmark with large contract sets.
- **Security/Privacy:** Processing is local — OK. Add guidance for handling PII and client documents in multitenant or CI environments.
- **Repo Hygiene:** Keep a single `.venv`. Use `nbstripout` pre-commit to avoid notebook noise.

If you want a full exported audit (`docs/AUDIT.md`) with file-specific notes and remediation steps, say "export audit" and I will produce it.
## Overview

Legal Contract Analyzer is a production-ready Python application that uses **Natural Language Processing (NLP)** and **legal domain expertise** to automatically analyze legal contracts, extract critical clauses, assess risk levels, and generate comprehensive compliance reports.

Built by a qualified legal practitioner with AI/ML expertise, this tool bridges the gap between **legal domain knowledge** and **machine learning engineering** -- directly addressing the needs of LegalTech, RegTech, and compliance teams worldwide.

### Key Capabilities

- **PDF Contract Ingestion** -- Extract text from PDF legal documents
- **Intelligent Clause Extraction** -- Identify 15+ critical legal clauses using NLP + legal keyword taxonomy
- **Risk Scoring Engine** -- Quantitative risk assessment per clause and overall contract
- **Compliance Gap Analysis** -- Flag missing essential clauses
- **Interactive Streamlit Dashboard** -- Visual contract analysis with downloadable reports
- **Production-Ready Architecture** -- Modular, tested, CI/CD pipeline

### Target Use Cases

- Contract review automation for law firms and legal departments
- Regulatory compliance monitoring for financial institutions
- Due diligence acceleration for M&A transactions
- Risk assessment for insurance and banking compliance teams
- LegalTech startup MVP for AI-powered contract intelligence

---

## Technical Architecture

```
legal-contract-analyzer/
|-- src/legal_contract_analyzer/
|   |-- __init__.py              # Package initialization
|   |-- extractor.py            # PDF text extraction engine
|   |-- clause_classifier.py     # NLP clause identification
|   |-- risk_analyzer.py         # Risk scoring algorithms
|   |-- compliance_checker.py    # Regulatory compliance validation
|   |-- report_generator.py      # HTML/Markdown report generation
|   |-- config.py               # Configuration and constants
|-- streamlit_app.py             # Interactive web dashboard
|-- tests/                       # Comprehensive test suite
|-- notebooks/                   # NOTE: example notebooks have been removed from the repository
|-- docs/                        # Documentation
|-- data/sample_contracts/       # Sample contracts for testing
```

---

## Installation

### Prerequisites

- Python 3.9 or higher
- pip package manager
- Virtual environment (recommended)

### Quick Setup

```bash
# Clone repository
git clone https://github.com/CalixtusDataSci/legal-contract-analyzer.git
cd legal-contract-analyzer

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Install package with all dependencies
pip install -e .

# Install development dependencies (for running tests)
pip install -e ".[dev]"

# If you plan to use the spaCy-powered clause matcher, download the English model:
python -m spacy download en_core_web_sm
```

### Verify Installation

```bash
# Run test suite
pytest tests/ -v --cov=src --cov-report=term-missing
```

---

## Quick Start

### Option 1: Command Line

```python
from legal_contract_analyzer import ContractAnalyzer

# Initialize analyzer
analyzer = ContractAnalyzer()

# Analyze a contract PDF
result = analyzer.analyze("data/sample_contracts/sample_employment.pdf")

# Print risk summary
print(result["risk_summary"])

# Generate HTML report
analyzer.generate_report(result, output_path="report.html")
```

### Option 2: Streamlit Web Interface

```bash
# Launch the interactive dashboard
streamlit run streamlit_app.py
```

The dashboard will open at `http://localhost:8501`. Upload any contract PDF to see:
- Extracted clauses with risk scores
- Visual risk distribution charts
- Missing clauses compliance check
- Downloadable analysis report

---

## How It Works

### Step 1: Document Ingestion
PDF text is extracted using `pdfplumber` with layout preservation for better clause boundary detection.

### Step 2: Clause Extraction
A hybrid approach combining:
- **Regex patterns** tuned for legal document structure
- **Keyword taxonomy** built from legal domain expertise (15+ clause types)
- **Sentence segmentation** with legal-aware boundary detection

Supported clause types:
| Clause Category | Description |
|-----------------|-------------|
| Termination | Notice periods, grounds for termination |
| Confidentiality | NDA obligations, information protection |
| Indemnification | Liability transfer, hold harmless provisions |
| Governing Law | Jurisdiction, dispute resolution venue |
| Liability Cap | Maximum liability limits, exclusions |
| Payment Terms | Fee structure, invoicing, late penalties |
| Intellectual Property | Ownership, licensing, assignment |
| Force Majeure | Unforeseeable circumstance provisions |
| Non-Compete | Restriction on competing activities |
| Data Protection | GDPR/privacy compliance clauses |
| Assignment | Transfer of contractual rights |
| Warranties | Guarantees, representations |
| Limitation of Liability | Damages caps, consequential damages |
| Dispute Resolution | Arbitration, mediation, litigation |
| Amendment | Change procedures, written notice |

### Step 3: Risk Analysis
Each clause is scored across three dimensions:
- **Severity (1-5):** Legal risk if clause is enforced against you
- **Ambiguity (1-5):** How unclear or open to interpretation
- **Burden (1-5):** Operational burden of compliance

**Overall Risk Score = weighted average with severity weighted at 50%**

### Step 4: Compliance Check
Validates presence of legally essential clauses and flags gaps based on contract type.

### Step 5: Report Generation
Produces professional HTML/Markdown reports suitable for legal review workflows.

---

## Project Structure

```
legal-contract-analyzer/
|-- .github/
|   |-- workflows/
|   |   |-- tests.yml            # CI: automated testing
|   |   |-- lint.yml             # CI: code quality checks
|-- data/
|   |-- sample_contracts/        # Demo PDF contracts
|-- docs/
|   |-- LEGAL.md                 # Legal disclaimers & compliance
|   |-- METHODOLOGY.md           # Technical methodology
|-- notebooks/                   # previously used for examples; removed to keep repo lean
|-- src/
|   |-- legal_contract_analyzer/
|   |   |-- __init__.py
|   |   |-- config.py            # Clause definitions & constants
|   |   |-- extractor.py         # PDF text extraction
|   |   |-- clause_classifier.py # Clause identification
|   |   |-- risk_analyzer.py     # Risk scoring engine
|   |   |-- compliance_checker.py # Compliance validation
|   |   |-- report_generator.py  # Report generation
|-- tests/
|   |-- __init__.py
|   |-- test_extractor.py
|   |-- test_classifier.py
|   |-- test_risk_analyzer.py
|   |-- test_compliance.py
|   |-- test_integration.py
|-- .flake8
|-- .gitignore
|-- CONTRIBUTING.md
|-- LICENSE
|-- Makefile
|-- README.md
|-- setup.py
|-- pyproject.toml
|-- requirements.txt
|-- streamlit_app.py
```

---

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ -v --cov=src --cov-report=html

# Run specific test module
pytest tests/test_classifier.py -v

# Run with linting
make test
```

---

## Development

```bash
# Install pre-commit hooks
pre-commit install

# Run linting
make lint

# Run type checking
make typecheck

# Format code
make format
```

---

## Roadmap

- [x] Core clause extraction engine
- [x] Risk scoring algorithm
- [x] Streamlit dashboard
- [x] Compliance gap checker
- [x] CI/CD pipeline
- [ ] Transformer-based clause classification (BERT/RoBERTa)
- [ ] Multi-language contract support
- [ ] Contract comparison/diff engine
- [ ] API server (FastAPI)
- [ ] Integration with document management systems

---

## Documentation

- [Legal & Compliance Framework](docs/LEGAL.md) -- Disclaimers, regulatory notes, ethical AI usage
- [Technical Methodology](docs/METHODOLOGY.md) -- Algorithm details, NLP architecture, scoring rationale
- [Contributing Guide](CONTRIBUTING.md) -- Development standards, PR guidelines

---

## License

MIT License -- see [LICENSE](LICENSE) for details.

**IMPORTANT LEGAL DISCLAIMER:** This tool is for **educational and research purposes** and **assistance to qualified legal professionals** only. It can be partly used for legal advice. Always consult a qualified attorney for full legal decisions and advice. See [docs/LEGAL.md](docs/LEGAL.md) for full disclaimers.

---

## About the Author

**Nwaeke Calixtus Ifeanyi, Esq.** -- Legal Practitioner | Compliance Lawyer | AI & Data Scientist | NLP Specialist | LegalTech

- LL.B (Hons), Imo State University, 2023
- Call to Bar, Nigerian Law School, 2025
- Python Programming Certified (HackerRank)
- Machine Learning & NLP (Kaggle)
- Targeting: LegalTech, RegTech, Compliance AI, NLP for Legal Applications

Connect: [LinkedIn](https://linkedin.com/in/calixtus-nwaeke-esq-b826bb1aa) | calixtusnwaeke@gmail.com

---

## Acknowledgments

Built with open-source tools: spaCy, scikit-learn, pdfplumber, Streamlit, pytest.
This project demonstrates the practical application of NLP in legal technology -- a growing field at the intersection of law, compliance, and artificial intelligence.
