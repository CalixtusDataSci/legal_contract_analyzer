"""Setup configuration for Legal Contract Analyzer."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="legal-contract-analyzer",
    version="1.0.0",
    author="Nwaeke Calixtus Ifeanyi, Esq.",
    author_email="calixtusnwaeke@gmail.com",
    description="AI-Powered Legal Document Analysis for Risk Detection and Clause Extraction",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/CalixtusDataSci/legal-contract-analyzer",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Legal Industry",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Office/Business :: Legal",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=[
        "pdfplumber>=0.10.0",
        "PyPDF2>=3.0.0",
        "streamlit>=1.28.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.1.0",
            "mypy>=1.5.0",
            "pre-commit>=3.4.0",
        ],
        "notebook": [
            "jupyter>=1.0.0",
            "matplotlib>=3.7.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "legal-analyze=legal_contract_analyzer.__main__:main",
        ],
    },
    keywords="legal nlp contract analysis risk compliance legaltech regtech ai",
    project_urls={
        "Bug Reports": "https://github.com/CalixtusDataSci/legal-contract-analyzer/issues",
        "Source": "https://github.com/CalixtusDataSci/legal-contract-analyzer",
        "LinkedIn": "https://linkedin.com/in/calixtus-nwaeke-esq-b826bb1aa",
    },
)
