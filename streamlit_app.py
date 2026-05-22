"""
Streamlit Web Interface for Legal Contract Analyzer

Interactive dashboard for contract upload, analysis, and report generation.
No coding required - just upload a PDF and see results.

Run with: streamlit run streamlit_app.py
"""

import os
import sys
import tempfile
from pathlib import Path

import streamlit as st

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from legal_contract_analyzer import ContractAnalyzer


# Page configuration
st.set_page_config(
    page_title="Legal Contract Analyzer",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 36px !important;
        font-weight: bold;
        color: #1a365d;
        margin-bottom: 10px;
    }
    .sub-header {
        font-size: 18px;
        color: #666;
        margin-bottom: 30px;
    }
    .risk-critical { color: #B71C1C; font-weight: bold; }
    .risk-high { color: #F44336; font-weight: bold; }
    .risk-medium { color: #FF9800; font-weight: bold; }
    .risk-low { color: #4CAF50; font-weight: bold; }
    .metric-card {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #1a365d;
    }
    .disclaimer {
        background: #fff8e1;
        border-left: 4px solid #ffb74d;
        padding: 12px;
        font-size: 13px;
        color: #666;
        margin: 15px 0;
    }
    .clause-card {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
    }
    .stProgress > div > div > div > div {
        background-color: #1a365d;
    }
</style>
""", unsafe_allow_html=True)


def get_risk_color(level: str) -> str:
    colors = {
        "critical": "#B71C1C",
        "high": "#F44336",
        "medium": "#FF9800",
        "low": "#4CAF50",
    }
    return colors.get(level, "#888")


def get_risk_class(level: str) -> str:
    return f"risk-{level}"


@st.cache_resource
def get_analyzer():
    """Cache the analyzer instance."""
    return ContractAnalyzer()


def main():
    # Header
    st.markdown('<div class="main-header">Legal Contract Analyzer</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">AI-Powered Contract Analysis | Risk Detection | Compliance Checking</div>',
        unsafe_allow_html=True
    )

    # Sidebar
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/scales.png", width=80)
        st.markdown("### About")
        st.markdown("""
        **Legal Contract Analyzer** uses Natural Language Processing
        to extract clauses, assess risk, and check compliance in
        legal contracts.
        
        **Built by:**
        Nwaeke Calixtus Ifeanyi, Esq.
        Legal Practitioner | AI & Data Scientist
        """)
        st.markdown("---")
        st.markdown("### How It Works")
        st.markdown("""
        1. Upload a contract PDF
        2. Select contract type
        3. AI extracts & analyzes clauses
        4. View risk assessment & compliance report
        5. Download the full report
        """)
        st.markdown("---")
        st.markdown("**Version:** 1.0.0")

    # Disclaimer
    st.markdown(
        '<div class="disclaimer">'
        '<strong>Legal Disclaimer:</strong> This tool is for informational and educational '
        'purposes only. It does not constitute legal advice. Always consult a qualified '
        'attorney before making legal decisions.'
        '</div>',
        unsafe_allow_html=True
    )

    # Upload section
    st.markdown("### Upload Contract")
    col1, col2 = st.columns([2, 1])

    with col1:
        uploaded_file = st.file_uploader(
            "Choose a contract PDF file",
            type=["pdf"],
            help="Upload a legal contract in PDF format for analysis",
        )

    with col2:
        contract_type = st.selectbox(
            "Contract Type",
            options=["general", "employment", "nda", "service"],
            format_func=lambda x: {
                "general": "General Commercial",
                "employment": "Employment Agreement",
                "nda": "Non-Disclosure Agreement",
                "service": "Service Agreement / SLA",
            }.get(x, x),
            help="Select the type of contract for targeted compliance checking",
        )

    if uploaded_file is not None:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = tmp.name

        try:
            with st.spinner("Analyzing contract... This may take a moment."):
                analyzer = get_analyzer()
                result = analyzer.analyze(tmp_path, contract_type)

            # Display results
            display_results(result)

            # Download options
            st.markdown("---")
            st.markdown("### Download Report")

            col_dl1, col_dl2 = st.columns(2)

            with col_dl1:
                # Generate and offer HTML download
                report_path = tmp_path.replace(".pdf", "_report.html")
                analyzer.generate_report(result, report_path)
                with open(report_path, "r", encoding="utf-8") as f:
                    html_content = f.read()
                st.download_button(
                    label="Download HTML Report",
                    data=html_content,
                    file_name=f"{result['filename']}_analysis.html",
                    mime="text/html",
                )

            with col_dl2:
                # Generate and offer Markdown download
                md_content = analyzer.reporter.generate_markdown(result)
                st.download_button(
                    label="Download Markdown Report",
                    data=md_content,
                    file_name=f"{result['filename']}_analysis.md",
                    mime="text/markdown",
                )

        finally:
            # Cleanup
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)


def display_results(result: dict):
    """Display analysis results in the Streamlit interface."""
    risk = result.get("risk_summary", {})
    compliance = result.get("compliance", {})
    clauses = result.get("clauses", [])

    # Top metrics row
    st.markdown("---")
    st.markdown("### Analysis Results")

    mcol1, mcol2, mcol3, mcol4 = st.columns(4)

    with mcol1:
        score = risk.get("overall_score", 0)
        level = risk.get("risk_level", "low")
        color = get_risk_color(level)
        st.markdown(
            f'<div class="metric-card">'
            f'<div style="font-size:12px;color:#888;">OVERALL RISK</div>'
            f'<div style="font-size:32px;font-weight:bold;color:{color};">{score:.1f}</div>'
            f'<div style="font-size:14px;color:{color};text-transform:uppercase;">{level}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    with mcol2:
        st.markdown(
            f'<div class="metric-card">'
            f'<div style="font-size:12px;color:#888;">CLAUSES FOUND</div>'
            f'<div style="font-size:32px;font-weight:bold;color:#1a365d;">{len(clauses)}</div>'
            f'<div style="font-size:14px;color:#666;">of 15 types checked</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    with mcol3:
        comp_score = compliance.get("compliance_score", 0)
        st.markdown(
            f'<div class="metric-card">'
            f'<div style="font-size:12px;color:#888;">COMPLIANCE</div>'
            f'<div style="font-size:32px;font-weight:bold;color:#1a365d;">{comp_score:.0f}%</div>'
            f'<div style="font-size:14px;color:#666;">score</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    with mcol4:
        high_risk = risk.get("high_risk_clauses", 0) + risk.get("critical_risk_clauses", 0)
        risk_color = "#F44336" if high_risk > 0 else "#4CAF50"
        st.markdown(
            f'<div class="metric-card">'
            f'<div style="font-size:12px;color:#888;">HIGH RISK CLAUSES</div>'
            f'<div style="font-size:32px;font-weight:bold;color:{risk_color};">{high_risk}</div>'
            f'<div style="font-size:14px;color:#666;">require attention</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    # Risk Distribution
    st.markdown("---")
    st.markdown("#### Risk Distribution")
    rcol1, rcol2, rcol3, rcol4 = st.columns(4)
    dist = risk.get("risk_distribution", {})
    with rcol1:
        st.metric("Low Risk", dist.get("low", 0), delta=None)
    with rcol2:
        st.metric("Medium Risk", dist.get("medium", 0), delta=None)
    with rcol3:
        st.metric("High Risk", dist.get("high", 0), delta=None)
    with rcol4:
        st.metric("Critical Risk", dist.get("critical", 0), delta=None)

    # Recommendations
    if risk.get("recommendations"):
        st.markdown("---")
        st.markdown("### Key Recommendations")
        for rec in risk["recommendations"]:
            if "CRITICAL" in rec or "URGENT" in rec:
                st.error(rec)
            elif "HIGH" in rec or "LIABILITY" in rec or "IMBALANCE" in rec:
                st.warning(rec)
            else:
                st.info(rec)

    # Compliance Section
    st.markdown("---")
    st.markdown("### Compliance Check")
    st.markdown(
        f"**Contract Type:** {compliance.get('contract_type_name', 'Unknown')} | "
        f"**Score:** {compliance.get('compliance_score', 0)}% | "
        f"**Status:** {compliance.get('compliance_level', 'Unknown')}"
    )

    req = compliance.get("required_clauses", {})
    rec = compliance.get("recommended_clauses", {})

    ccol1, ccol2 = st.columns(2)
    with ccol1:
        st.markdown("**Required Clauses**")
        st.progress(req.get("present", 0) / max(req.get("total", 1), 1))
        st.caption(f"{req.get('present', 0)} of {req.get('total', 0)} present")

    with ccol2:
        st.markdown("**Recommended Clauses**")
        st.progress(rec.get("present", 0) / max(rec.get("total", 1), 1))
        st.caption(f"{rec.get('present', 0)} of {rec.get('total', 0)} present")

    # Missing clauses table
    if compliance.get("missing_clauses"):
        st.markdown("#### Missing Clauses")
        missing_data = []
        for m in compliance["missing_clauses"]:
            missing_data.append({
                "Clause": m["clause_name"],
                "Importance": m["importance"],
                "Risk of Absence": m["risk_of_absence"],
                "Recommendation": m["recommendation"],
            })
        st.dataframe(missing_data, use_container_width=True)

    # Extracted Clauses
    st.markdown("---")
    st.markdown(f"### Extracted Clauses ({len(clauses)} found)")

    # Filter by clause type
    if clauses:
        clause_types = sorted(set(c["type_name"] for c in clauses))
        selected_types = st.multiselect(
            "Filter by clause type",
            options=clause_types,
            default=clause_types,
        )

        filtered_clauses = [c for c in clauses if c["type_name"] in selected_types]

        for clause in filtered_clauses:
            with st.container():
                confidence = clause.get("confidence", 0) * 100
                conf_color = "#4CAF50" if confidence > 70 else "#FF9800" if confidence > 40 else "#F44336"

                st.markdown(
                    f'<div class="clause-card">'
                    f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">'
                    f'<strong style="color:#1a365d;font-size:16px;">{clause["type_name"]}</strong>'
                    f'<span style="background:{conf_color};color:white;padding:4px 10px;border-radius:12px;font-size:12px;">'
                    f'{confidence:.0f}% confidence</span>'
                    f'</div>'
                    f'<div style="font-size:13px;color:#555;margin:8px 0;padding:10px;background:#f8f9fa;border-radius:4px;">'
                    f'"{clause["extracted_text"][:300]}..."'
                    f'</div>',
                    unsafe_allow_html=True
                )

                # Risk factors
                if clause.get("risk_factors"):
                    st.markdown("<div style='font-size:12px;color:#888;margin-top:5px;'>Risk Factors:</div>", unsafe_allow_html=True)
                    for rf in clause["risk_factors"]:
                        st.markdown(
                            f"<div style='font-size:12px;color:#F44336;margin-left:15px;'>"
                            f"&#9888; {rf.get('description', '')}</div>",
                            unsafe_allow_html=True
                        )

                st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
