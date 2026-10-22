
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
    "Improve bug reports by identifying missing information, "
    "flagging vague details, and generating targeted clarification questions."
)

with st.form("bug_report_form"):
    title = st.text_input(
        "Bug title",
        placeholder="Example: Login fails after entering valid credentials",
    )
    description = st.text_area(
        "Bug description",
        placeholder="Describe the affected feature and the user-visible problem.",
    )
    steps = st.text_area(
        "Steps to reproduce",
        placeholder="1. Open the sign-in page\n2. Enter valid credentials\n3. Click Sign in",
    )
    expected = st.text_area(
        "Expected behavior",
        placeholder="Describe the intended outcome after the steps are followed.",
    )
    actual = st.text_area(
        "Actual behavior",
        placeholder="Describe the observed result, error, or incorrect state.",
    )
    environment = st.text_input(
        "Environment details (OS, browser, version/build)",
        placeholder="Example: Windows 11, Chrome 128, app version 2.4.1",
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
        "Field completeness",
        f"{result['field_completeness']}%",
        delta=f"{result['completed_fields']}/{result['total_fields']} meaningful fields",
    )
    st.progress(result["field_completeness"] / 100)

    st.subheader("Missing or weak information")
    if result["missing_information"]:
        for item in result["missing_information"]:
            st.write(f"- {item}")
    else:
        st.success("No major gaps were identified in the current draft.")

    st.subheader("Field-by-field assessment")
    for key, field_result in result["field_results"].items():
        status_text = field_result["status"].replace("_", " ").title()
        st.markdown(f"**{field_result['label']}** — {status_text}")
        st.caption(field_result["reason"])
        if field_result["evidence"]:
            st.write(f"Evidence: {field_result['evidence']}")
        if field_result["issues"]:
            st.write("Issues:")
            for issue in field_result["issues"]:
                st.write(f"- {issue}")
        st.write(f"Recommendation: {field_result['suggestion']}")
        st.write("---")

    st.subheader("Clarification questions")
    if questions:
        for question in questions:
            st.write(f"- {question}")
    else:
        st.success("No additional clarification is needed based on the current report.")

    st.subheader("Improved bug report")
    st.markdown(improved_report)

    st.download_button(
        "Download improved report",
        data=improved_report,
        file_name="improved_bug_report.md",
        mime="text/markdown",
    )
