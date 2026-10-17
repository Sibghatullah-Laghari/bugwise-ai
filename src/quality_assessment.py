
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
}


def assess_bug_report(report):
    normalized = {
        key: str(report.get(key, "") or "").strip()
        for key in FIELDS
    }

    field_results = {}
    missing_information = []
    warnings = []

    for key, label in FIELDS.items():
        value = normalized[key]
        problems = []

        if not value:
            problems.append("Field is empty.")
        elif value.lower().strip(" .!?") in PLACEHOLDER_VALUES:
            problems.append("Answer is a placeholder, not useful information.")
        elif len(value) < 8:
            problems.append("Answer may be too short to be useful.")

        if key == "title" and value:
            vague_titles = {
                "bug", "error", "issue", "not working",
                "system is not working", "it doesn't work",
                "doesn't work", "does not work",
            }
            if value.lower().strip(" .!?") in vague_titles:
                problems.append("Title is too vague; identify the affected feature.")

        if key == "steps" and value:
            lower_value = value.lower()
            if not problems and not any(
                word in lower_value
                for word in (
                    "1.", "1)", "first", "then", "next",
                    "open", "click", "tap", "press",
                    "select", "enter", "navigate", "launch",
                )
            ):
                problems.append(
                    "Steps may not describe actionable reproduction actions."
                )

        if key == "environment" and value:
            lower_value = value.lower()
            if not any(
                term in lower_value
                for term in (
                    "android", "ios", "windows", "linux", "macos",
                    "mac os", "ubuntu", "browser", "chrome", "firefox",
                    "version", "build",
                )
            ):
                problems.append(
                    "Specify the operating system and relevant version."
                )
            elif lower_value in {"android", "ios", "windows", "linux"}:
                problems.append(
                    "Add the OS version and application version if known."
                )

        valid = len(problems) == 0

        field_results[key] = {
            "label": label,
            "provided": bool(value),
            "valid": valid,
            "problems": problems,
        }

        if not valid:
            missing_information.append(label)
            for problem in problems:
                warnings.append(f"{label}: {problem}")

    valid_count = sum(
        result["valid"] for result in field_results.values()
    )

    return {
        "completeness_indicator": round(
            100 * valid_count / len(FIELDS)
        ),
        "completed_fields": valid_count,
        "total_fields": len(FIELDS),
        "missing_information": missing_information,
        "field_results": field_results,
        "warnings": warnings,
    }
