
from src.quality_assessment import assess_bug_report

QUESTION_TEMPLATES = {
    "title": {
        "missing": "Can you provide a more specific title that identifies the affected feature and the failure?",
        "insufficient": "Which feature is affected, and what is the user seeing when the problem occurs?",
        "unclear": "Can you tighten the title so it names the affected component and the observed issue more clearly?",
    },
    "description": {
        "missing": "Can you provide a clearer description of which feature is affected and what problem the user encounters?",
        "insufficient": "Can you describe the affected functionality and the user-visible symptom in more detail?",
        "unclear": "What is the actual symptom or error that makes this bug report hard to understand?",
    },
    "steps": {
        "missing": "What exact actions should the user perform to reproduce the issue?",
        "insufficient": "Which page or control should the user open, and what should they click, enter, or select?",
        "unclear": "Can you make the reproduction steps more concrete and ordered, so another user can follow them reliably?",
    },
    "expected": {
        "missing": "What should happen after these steps?",
        "insufficient": "What is the correct result or expected user-visible outcome?",
        "unclear": "Can you describe the intended behavior more precisely than a general expectation?",
    },
    "actual": {
        "missing": "What happens instead? Please describe the observed result or error message.",
        "insufficient": "What did the user actually see, receive, or experience when the issue occurred?",
        "unclear": "Can you describe the visible failure, error, or incorrect state more clearly?",
    },
    "environment": {
        "missing": "Which operating system, browser, and application version or build are involved?",
        "insufficient": "What operating system, browser, and relevant version/build should we know about?",
        "unclear": "Please add the relevant platform details and version information for the affected environment.",
    },
}


def get_clarification_questions(report):
    result = assess_bug_report(report)
    field_results = result["field_results"]
    questions = []
    seen = set()

    for key in ["title", "description", "steps", "expected", "actual", "environment"]:
        status = field_results[key]["status"]
        if status == "adequate":
            continue

        question = QUESTION_TEMPLATES[key].get(status, QUESTION_TEMPLATES[key]["missing"])
        normalized = " ".join(question.lower().split())
        if normalized not in seen:
            questions.append(question)
            seen.add(normalized)

    return questions
