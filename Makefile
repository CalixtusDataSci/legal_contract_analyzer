.PHONY: help install install-dev test lint format typecheck clean run streamlit

help:
	@echo "Legal Contract Analyzer - Available Commands"
	@echo "============================================"
	@echo "install      Install package with core dependencies"
	@echo "install-dev  Install with development dependencies"
	@echo "test         Run test suite with coverage"
	@echo "lint         Run flake8 linting"
	@echo "format       Format code with black"
	@echo "typecheck    Run mypy type checking"
	@echo "clean        Remove build artifacts"
	@echo "run          Run command-line analysis (specify PDF=path)"
	@echo "streamlit    Launch Streamlit web dashboard"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"
	pre-commit install

test:
	pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html

lint:
	flake8 src/ tests/ streamlit_app.py

format:
	black src/ tests/ streamlit_app.py

typecheck:
	mypy src/

clean:
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/ .coverage htmlcov/ __pycache__/ src/**/__pycache__ tests/__pycache__
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

run:
	@echo "Usage: python -c \"from legal_contract_analyzer import ContractAnalyzer; ...\""

streamlit:
	streamlit run streamlit_app.py
