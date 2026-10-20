
from src.quality_assessment import assess_bug_report
#.

QUESTIONS = {
    "title": "Can you provide a specific title identifying the affected feature and the failure?",
    "description": "What exactly happens, and what error message appears, if any?",
    "steps": "Please list the exact actions needed to reproduce the issue, in order.",
    "expected": "What should happen after performing those steps?",
    "actual": "What happens instead? Please describe the observed failure.",
    "environment": "Which operating system version and application version are you using?",
}


def get_clarification_questions(report):
    result = assess_bug_report(report)
    field_results = result["field_results"]

    questions = []

    for key, question in QUESTIONS.items():``
        if not field_results[key]["valid"]:
            questions.append(question)

    return questions
