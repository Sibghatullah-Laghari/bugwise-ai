
from src.quality_assessment import assess_bug_report
from src.agent import get_clarification_questions
from src.report_generator import generate_improved_report


def test_incomplete_report():
    report = {
        "title": "Login is broken",
        "description": "Login fails.",
        "steps": "",
        "expected": "User logs in.",
        "actual": "Login fails.",
        "environment": "",
    }

    result = assess_bug_report(report)

    assert result["completeness_indicator"] == 67
    assert len(result["missing_information"]) == 2
    assert len(get_clarification_questions(report)) == 2

    improved = generate_improved_report(report)
    assert "Unknown" in improved
