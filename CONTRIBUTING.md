# Contributing to Legal Contract Analyzer

Thank you for your interest in contributing to Legal Contract Analyzer! This project welcomes contributions from legal professionals, data scientists, and developers.

## About the Project

This project was built by **Nwaeke Calixtus Ifeanyi, Esq.** -- a qualified Nigerian lawyer and AI Data Scientist -- to demonstrate the practical application of NLP in legal technology. It bridges legal domain expertise with machine learning engineering.

## How to Contribute

### Reporting Issues

- Check if the issue already exists
- Provide clear reproduction steps
- Include sample contract text (anonymized) if relevant
- Specify Python version and OS

### Suggesting Enhancements

- Open an issue describing the enhancement
- Explain the legal or technical use case
- Reference relevant legal standards or precedents if applicable

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Make your changes
4. Run tests: `make test`
5. Run linting: `make lint`
6. Commit with descriptive messages
7. Push and create a Pull Request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/legal-contract-analyzer.git
cd legal-contract-analyzer

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install development dependencies
make install-dev
```

## Code Standards

### Python Style
- Follow PEP 8
- Use `black` for formatting (`make format`)
- Maximum line length: 88 characters
- Use type hints where appropriate

### Testing
- Write tests for new features
- Maintain 80%+ code coverage
- Use pytest for all tests
- Follow AAA pattern: Arrange, Act, Assert

### Documentation
- Update README.md for user-facing changes
- Update METHODOLOGY.md for algorithm changes
- Add docstrings to public functions
- Include legal disclaimers for new features

## Legal Considerations

- This project involves legal document processing
- All contributions must include appropriate disclaimers
- Do not commit real client contracts or confidential documents
- Respect attorney-client privilege in all examples

## Areas Needing Contribution

- **Transformer Models:** Fine-tune BERT/RoBERTa on legal text for clause classification
- **Multi-Jurisdiction:** Support for civil law and non-English contracts
- **Industry Templates:** Specialized clause detection for specific industries
- **API Development:** FastAPI REST endpoints
- **Documentation:** Legal use case documentation and tutorials

## Code of Conduct

- Be respectful and professional
- Welcome newcomers
- Focus on constructive feedback
- Respect different legal traditions and jurisdictions

## Questions?

Contact: calixtusnwaeke@gmail.com

LinkedIn: https://linkedin.com/in/calixtus-nwaeke-esq-b826bb1aa

---

*Contributions are subject to MIT License terms*
