
import streamlit as st

from src.quality_assessment import assess_bug_report
from src.agent import get_clarification_questions
from src.report_generator import generate_improved_report

st.set_page_config(
    page_title="BugWise AI",
    page_icon="🐞",
    layout="wide",
)

st.title("🐞 BugWise AI")
st.subheader("Bug Report Quality & Clarification Agent")
st.write(
    "Improve bug reports by identifying missing information "
    "and generating targeted clarification questions."
)

with st.form("bug_report_form"):
    title = st.text_input("Bug title")
    description = st.text_area("Bug description")
    steps = st.text_area("Steps to reproduce")
    expected = st.text_area("Expected behavior")
    actual = st.text_area("Actual behavior")
    environment = st.text_input(
        "Environment (OS, browser, application version)"
    )

    submitted = st.form_submit_button("Assess bug report")

if submitted:
    report = {
        "title": title,
        "description": description,
        "steps": steps,
        "expected": expected,
        "actual": actual,
        "environment": environment,
    }

    result = assess_bug_report(report)
    questions = get_clarification_questions(report)
    improved_report = generate_improved_report(report)

    st.divider()
    st.header("Assessment results")

    st.metric(
        "Completeness indicator",
        f'{result["completeness_indicator"]}%',
    )

    st.progress(result["completeness_indicator"] / 100)

    st.subheader("Missing information")
    if result["missing_information"]:
        for item in result["missing_information"]:
            st.write(f"- {item}")
    else:
        st.success("All six fields have been provided.")

    st.subheader("Clarification questions")
    if questions:
        for question in questions:
            st.write(f"- {question}")
    else:
        st.success("No missing fields require clarification.")

    st.subheader("Improved bug report")
    st.markdown(improved_report)

    st.download_button(
        "Download improved report",
        data=improved_report,
        file_name="improved_bug_report.md",
        mime="text/markdown",
    )
