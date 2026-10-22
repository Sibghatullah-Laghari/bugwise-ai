
import pytest

from src.agent import get_clarification_questions
from src.quality_assessment import assess_bug_report, FIELDS
from src.report_generator import generate_improved_report


def _empty_report():
    return {
        "title": "",
        "description": "",
        "steps": "",
        "expected": "",
        "actual": "",
        "environment": "",
    }


def _complete_report():
    return {
        "title": "Login fails after entering valid credentials",
        "description": "When a user enters a valid username and password, the login button does nothing and the page remains on the sign-in form.",
        "steps": "1. Open the sign-in page.\n2. Enter a valid username and password.\n3. Click the Sign in button.\n4. Observe the page remains unchanged.",
        "expected": "The user should be redirected to the dashboard and the session should start.",
        "actual": "The page stays on the sign-in screen and no error message is shown.",
        "environment": "Windows 11, Chrome 128, app version 2.4.1",
    }


def test_empty_and_placeholder_fields_are_missing():
    report = {
        "title": "   ",
        "description": "None",
        "steps": "n/a",
        "expected": "unknown",
        "actual": "tbd",
        "environment": "    ",
    }
    result = assess_bug_report(report)
    assert result["completeness_indicator"] == 0
    assert result["completed_fields"] == 0
    assert result["total_fields"] == 6
    assert all(
        result["field_results"][key]["status"] == "missing"
        for key in FIELDS
    )


def test_complete_report_is_adequate():
    report = _complete_report()
    result = assess_bug_report(report)
    assert result["completeness_indicator"] == 100
    assert result["completed_fields"] == 6
    statuses = {key: value["status"] for key, value in result["field_results"].items()}
    assert all(status == "adequate" for status in statuses.values())


def test_title_vagueness_is_flagged():
    report = _empty_report()
    report["title"] = "Bug"
    report["description"] = "This does not work."
    report["steps"] = "Open app and click around."
    report["expected"] = "The feature should work."
    report["actual"] = "It fails."
    report["environment"] = "Windows 11, Chrome 128"

    result = assess_bug_report(report)
    assert result["field_results"]["title"]["status"] in {"insufficient", "unclear"}
    assert any("vague" in issue.lower() or "feature" in issue.lower() for issue in result["field_results"]["title"]["issues"])


def test_short_but_informative_title_is_accepted():
    report = _complete_report()
    report["title"] = "PDF export crashes on images"
    result = assess_bug_report(report)
    assert result["field_results"]["title"]["status"] == "adequate"


def test_natural_language_steps_are_allowed_without_numbering():
    report = _complete_report()
    report["steps"] = "Open the sign-in page, enter a valid account, press Sign in, and watch the form stay open."
    result = assess_bug_report(report)
    assert result["field_results"]["steps"]["status"] == "adequate"


def test_generic_expected_and_actual_behavior_is_not_accepted():
    report = {
        "title": "Checkout page issue",
        "description": "A checkout problem occurs.",
        "steps": "Open the checkout page and click Pay.",
        "expected": "normal",
        "actual": "broken",
        "environment": "macOS 14, Safari 17, app version 3.2.0",
    }
    result = assess_bug_report(report)
    assert result["field_results"]["expected"]["status"] in {"insufficient", "unclear"}
    assert result["field_results"]["actual"]["status"] in {"insufficient", "unclear"}


def test_missing_only_steps_and_missing_only_environment_are_detected():
    report = _complete_report()
    report["steps"] = ""
    result = assess_bug_report(report)
    assert result["field_results"]["steps"]["status"] == "missing"

    report = _complete_report()
    report["environment"] = "browser"
    result = assess_bug_report(report)
    assert result["field_results"]["environment"]["status"] in {"insufficient", "unclear"}


def test_whitespace_and_unicode_are_normalized():
    report = {
        "title": "\n  Login fails for UTF-8 filenames  →  ",
        "description": "User uploads café report and sees an error.",
        "steps": "1. Open file upload.\n2. Choose café.csv.\n3. Submit.",
        "expected": "The file should upload successfully.",
        "actual": "The upload fails with a validation error.",
        "environment": "Linux 6.8, Firefox ESR 115, build 7.9",
    }
    result = assess_bug_report(report)
    assert result["field_results"]["title"]["status"] == "adequate"
    assert result["field_results"]["description"]["status"] == "adequate"


def test_clarification_questions_are_targeted_and_non_redundant():
    report = {
        "title": "Login fails after entering valid credentials",
        "description": "",
        "steps": "",
        "expected": "The user should be redirected to the dashboard.",
        "actual": "The app shows an error.",
        "environment": "Windows 11, Chrome 128",
    }
    questions = get_clarification_questions(report)
    assert len(questions) == 2
    assert all("description" in q.lower() or "reproduce" in q.lower() for q in questions)
    assert len(set(questions)) == len(questions)


def test_report_generation_preserves_known_facts_and_marks_missing_fields():
    report = {
        "title": "Export fails",
        "description": "",
        "steps": "1. Open export dialog.\n2. Click Export.",
        "expected": "The file should download.",
        "actual": "",
        "environment": "",
    }
    improved = generate_improved_report(report)
    assert "## Bug title" in improved
    assert "Export fails" in improved
    assert "## Bug description" in improved
    assert "Missing" in improved
    assert "## Actual behavior" in improved
    assert "## Environment details" in improved
    assert "Information still needed" in improved


def test_blank_submission_is_handled_gracefully():
    result = assess_bug_report(_empty_report())
    assert 0 <= result["completeness_indicator"] <= 100
    assert result["warning_count"] >= 0
    assert result["missing_information"]


def test_public_api_is_stable():
    assert callable(assess_bug_report)
    assert callable(get_clarification_questions)
    assert callable(generate_improved_report)
    assert set(FIELDS) == {"title", "description", "steps", "expected", "actual", "environment"}


def test_integration_result_schema_is_consistent():
    result = assess_bug_report(_complete_report())
    assert set(result.keys()) >= {
        "completeness_indicator",
        "completed_fields",
        "total_fields",
        "missing_information",
        "field_results",
        "warnings",
    }
    assert result["total_fields"] == 6
    assert result["completed_fields"] <= result["total_fields"]
    assert result["field_results"]["title"]["label"] == "Bug title"


@pytest.mark.parametrize(
    "field,text,status",
    [
        ("title", "Bug", "insufficient"),
        ("description", "It does not work", "insufficient"),
        ("steps", "Open the app and do something", "insufficient"),
        ("expected", "normal", "insufficient"),
        ("actual", "broken", "insufficient"),
        ("environment", "browser", "insufficient"),
    ],
)
def test_vague_values_are_not_accepted(field, text, status):
    report = _complete_report()
    report[field] = text
    result = assess_bug_report(report)
    assert result["field_results"][field]["status"] in {status, "unclear"}


def test_report_quality_percentages_are_not_required_for_explainability():
    report = _complete_report()
    result = assess_bug_report(report)
    assert "field_completeness" in result
    assert "report_quality" in result
    assert 0 <= result["field_completeness"] <= 100
    assert 0 <= result["report_quality"] <= 100
