
import re

FIELDS = {
    "title": "Bug title",
    "description": "Bug description",
    "steps": "Steps to reproduce",
    "expected": "Expected behavior",
    "actual": "Actual behavior",
    "environment": "Environment details",
}

PLACEHOLDER_VALUES = {
    "n/a",
    "na",
    "none",
    "unknown",
    "no idea",
    "not sure",
    "don't know",
    "dont know",
    "tbd",
    "-",
    "null",
    "nil",
    "n.a.",
    "not available",
}

GENERIC_TITLE_VALUES = {
    "bug",
    "issue",
    "error",
    "problem",
    "not working",
    "it does not work",
    "it doesn't work",
    "does not work",
    "doesn't work",
    "something is wrong",
    "system is not working",
}

GENERIC_DESCRIPTION_VALUES = {
    "it does not work",
    "it doesn't work",
    "does not work",
    "doesn't work",
    "not working",
    "broken",
    "something is wrong",
    "bug",
    "issue",
    "problem",
}

GENERIC_BEHAVIOR_VALUES = {
    "normal",
    "broken",
    "works",
    "fine",
    "okay",
    "it fails",
    "it works",
    "doesn't work",
    "does not work",
    "not working",
    "expected",
    "error",
}

GENERIC_ENVIRONMENT_VALUES = {
    "browser",
    "version",
    "app",
    "application",
    "platform",
    "device",
    "os",
    "environment",
    "computer",
}

ACTION_KEYWORDS = (
    "open",
    "click",
    "tap",
    "press",
    "select",
    "enter",
    "navigate",
    "launch",
    "submit",
    "type",
    "choose",
    "load",
    "visit",
    "scroll",
    "login",
    "sign in",
    "save",
    "delete",
    "upload",
    "download",
)

ENVIRONMENT_KEYWORDS = (
    "windows",
    "linux",
    "macos",
    "mac os",
    "ubuntu",
    "android",
    "ios",
    "browser",
    "chrome",
    "firefox",
    "safari",
    "edge",
    "version",
    "build",
    "release",
)

STATUS_SCORE = {
    "adequate": 100,
    "unclear": 60,
    "insufficient": 35,
    "missing": 0,
}


def normalize_text(value):
    if value is None:
        return ""
    text = str(value).strip()
    return " ".join(text.split())


def canonical_placeholder(value):
    text = normalize_text(value).lower()
    text = text.strip(" .!?;:-")
    return text in PLACEHOLDER_VALUES or text.replace(".", "") in PLACEHOLDER_VALUES


def is_missing_or_placeholder(value):
    text = normalize_text(value)
    return not text or canonical_placeholder(text)


def _word_count(value):
    return len(re.findall(r"\b[\w/.-]+\b", normalize_text(value)))


def has_meaningful_content(value, field_key=None):
    text = normalize_text(value)
    if not text or canonical_placeholder(text):
        return False

    lower = text.lower()
    if lower in GENERIC_TITLE_VALUES or lower in GENERIC_DESCRIPTION_VALUES or lower in GENERIC_BEHAVIOR_VALUES:
        return False

    if field_key == "environment" and lower in GENERIC_ENVIRONMENT_VALUES:
        return False

    if field_key == "title" and _word_count(text) <= 1:
        return False

    words = re.findall(r"\b[\w'-]+\b", text)
    if not words:
        return False

    if len(words) == 1 and lower not in {"windows", "linux", "macos", "ios", "android", "chrome", "firefox", "safari", "edge", "browser"}:
        return False

    return True


def _excerpt(value):
    text = normalize_text(value)
    if not text:
        return ""
    return text[:180]


def _determine_status_and_reason(field_key, value):
    text = normalize_text(value)
    if not text:
        return (
            "missing",
            "No useful information was supplied for this field.",
            "Field is empty.",
            "Add the missing details so the report is actionable.",
            [],
            False,
        )

    if canonical_placeholder(text):
        return (
            "missing",
            "The field contains only placeholder text and does not provide useful information.",
            "Placeholder or unknown value only.",
            "Replace placeholder text with actual details when available.",
            ["Placeholder value detected"],
            False,
        )

    lower = text.lower()
    issues = []

    if field_key == "title":
        if lower in GENERIC_TITLE_VALUES:
            issues.append("Title is too vague to identify the affected feature or symptom.")
            return (
                "insufficient",
                "The title is too generic to help identify the bug clearly.",
                "Title is too vague.",
                "Use a concise title that names the affected feature and the problem.",
                issues,
                False,
            )

        if _word_count(text) <= 2:
            issues.append("Title is too brief to identify the affected component or failure clearly.")
            return (
                "insufficient",
                "The title is very brief and may not communicate the affected feature or outcome clearly.",
                "Title is under-specified.",
                "Add the affected feature and the observed failure in a short, specific title.",
                issues,
                False,
            )

        return (
            "adequate",
            "The title identifies the affected component and the observed problem in a concise way.",
            "Title gives enough context.",
            "Keep the title brief and specific.",
            [],
            True,
        )

    if field_key == "description":
        if lower in GENERIC_DESCRIPTION_VALUES or any(pattern in lower for pattern in ("it does not work", "it doesn't work", "something is wrong")):
            issues.append("Description is too generic to explain the problem or affected feature.")
            return (
                "insufficient",
                "The description does not explain the feature, the symptom, or any relevant context.",
                "Description is vague.",
                "Describe the affected functionality and the observed problem with enough detail for a teammate to understand it.",
                issues,
                False,
            )

        if _word_count(text) <= 5:
            issues.append("Description is very brief and may not include enough context.")
            return (
                "insufficient",
                "The description is present but still too brief to explain the issue clearly.",
                "Description is sparse.",
                "Add the affected feature, symptom, location, or any visible error.",
                issues,
                False,
            )

        return (
            "adequate",
            "The description provides meaningful context about the affected feature and the observed problem.",
            "Description is informative.",
            "Keep the relevant technical details and user impact in the description.",
            [],
            True,
        )

    if field_key == "steps":
        has_action = any(keyword in lower for keyword in ACTION_KEYWORDS)
        has_sequence = bool(re.search(r"\b(?:1\.|2\.|first|then|next|after|finally)\b", lower))

        if re.search(r"\b(?:do something|do stuff|click around|mess around|use the app|use the application|figure it out)\b", lower):
            issues.append("The reproduction steps are too vague because they instruct the user to do something generic instead of concrete actions.")
            return (
                "insufficient",
                "The steps do not specify a concrete reproduction sequence.",
                "Steps are too vague.",
                "List the exact page, control, and action for each step in order.",
                issues,
                False,
            )

        if not has_action and not has_sequence:
            issues.append("The reproduction steps do not clearly describe ordered, actionable actions.")
            return (
                "insufficient",
                "The steps are too vague to reproduce the issue reliably.",
                "Steps are not sufficiently actionable.",
                "List the exact actions, in order, including the page or control involved.",
                issues,
                False,
            )

        if has_action or has_sequence:
            return (
                "adequate",
                "The steps describe concrete, ordered actions that can be followed to reproduce the issue.",
                "Steps are actionable.",
                "Keep the sequence precise and avoid generalized instructions.",
                [],
                True,
            )

    if field_key == "expected":
        if lower in GENERIC_BEHAVIOR_VALUES or lower in {"works", "fine", "okay", "normal"}:
            issues.append("Expected behavior is too generic to describe the intended outcome.")
            return (
                "insufficient",
                "The expected behavior is too vague to describe what should happen.",
                "Expected behavior is under-specified.",
                "Describe the intended result, the screen or state expected, and the user-visible outcome.",
                issues,
                False,
            )

        if _word_count(text) <= 3:
            issues.append("The expected result is too brief to be actionable.")
            return (
                "insufficient",
                "The expected behavior is present but does not clearly describe the intended outcome.",
                "Expected behavior is too brief.",
                "Explain what should happen after the reproduction steps are followed.",
                issues,
                False,
            )

        return (
            "adequate",
            "The expected behavior clearly states the intended outcome.",
            "Expected behavior is clear.",
            "Keep the intended result specific and observable.",
            [],
            True,
        )

    if field_key == "actual":
        if lower in GENERIC_BEHAVIOR_VALUES or lower in {"broken", "fails", "error", "not working"}:
            issues.append("Actual behavior is too generic to explain what happened instead.")
            return (
                "insufficient",
                "The actual behavior does not explain the observed result in enough detail to diagnose the issue.",
                "Actual behavior is vague.",
                "Describe the visible result, error message, or incorrect state that occurs after the steps.",
                issues,
                False,
            )

        if _word_count(text) <= 3:
            issues.append("The observed outcome is too brief to be informative.")
            return (
                "insufficient",
                "The actual behavior is present but too terse to explain what happened.",
                "Actual behavior is too brief.",
                "State the observed outcome, such as an error, incomplete state, or wrong UI behavior.",
                issues,
                False,
            )

        return (
            "adequate",
            "The actual behavior clearly describes the observed result.",
            "Actual behavior is clear.",
            "Include the relevant error text or incorrect state when available.",
            [],
            True,
        )

    if field_key == "environment":
        if lower in GENERIC_ENVIRONMENT_VALUES or lower == "browser":
            issues.append("The environment details are too generic to identify the system or app version.")
            return (
                "insufficient",
                "The environment information is too vague to be useful for reproduction or diagnosis.",
                "Environment details are generic.",
                "Specify the OS, browser, and app version or build relevant to the issue.",
                issues,
                False,
            )

        if not any(keyword in lower for keyword in ENVIRONMENT_KEYWORDS):
            issues.append("The environment field does not contain relevant system or version details.")
            return (
                "insufficient",
                "The environment does not identify the relevant system details.",
                "Environment is missing relevant details.",
                "Add the operating system, browser, device, and application version or build when known.",
                issues,
                False,
            )

        if not any(keyword in lower for keyword in ("windows", "linux", "macos", "android", "ios")):
            issues.append("The environment may be missing the operating system or platform details.")
            return (
                "unclear",
                "The environment includes some information, but it does not clearly identify the operating system or platform.",
                "Environment details are incomplete.",
                "Specify the platform or OS and the app version/build to help reproduce the issue.",
                issues,
                False,
            )

        if not any(keyword in lower for keyword in ("chrome", "firefox", "safari", "edge", "browser", "version", "build")):
            issues.append("The environment may be missing the relevant browser or version details.")
            return (
                "unclear",
                "The environment gives some system context, but it may be missing the browser or application version.",
                "Version information is incomplete.",
                "If relevant, include the browser and app version or build used during the issue.",
                issues,
                False,
            )

        return (
            "adequate",
            "The environment includes enough system, browser, and version context to be useful.",
            "Environment details are sufficient.",
            "Keep the relevant environment details current and specific to the reported bug.",
            [],
            True,
        )

    return (
        "insufficient",
        "The field is present but not yet informative enough.",
        "Field needs more detail.",
        "Add more concrete details to make this field actionable.",
        ["The field contains limited detail"],
        False,
    )


def assess_bug_report(report):
    if not isinstance(report, dict):
        report = {}

    normalized = {key: normalize_text(report.get(key, "")) for key in FIELDS}
    field_results = {}
    missing_information = []
    warnings = []

    meaningful_fields = 0

    for key, label in FIELDS.items():
        value = normalized[key]
        status, reason, evidence, suggestion, issues, meaningful = _determine_status_and_reason(key, value)
    
        if status == "missing":
            missing_information.append(label)
        elif status != "adequate":
            missing_information.append(label)

        if meaningful:
            meaningful_fields += 1

        valid = status == "adequate"
        field_result = {
            "field": key,
            "label": label,
            "status": status,
            "provided": bool(value),
            "meaningful": meaningful,
            "valid": valid,
            "reason": reason,
            "evidence": _excerpt(value),
            "suggestion": suggestion,
            "issues": issues,
        }
        field_results[key] = field_result

        if not valid:
            warnings.append(f"{label}: {reason}")
            for issue in issues:
                warnings.append(f"{label}: {issue}")

    field_completeness = round((meaningful_fields / len(FIELDS)) * 100)
    report_quality = round(
        sum(STATUS_SCORE[field_results[key]["status"]] for key in FIELDS) / len(FIELDS)
    )

    return {
        "completeness_indicator": field_completeness,
        "field_completeness": field_completeness,
        "completed_fields": meaningful_fields,
        "total_fields": len(FIELDS),
        "missing_information": missing_information,
        "field_results": field_results,
        "warnings": warnings,
        "warning_count": len(warnings),
        "report_quality": report_quality,
    }
