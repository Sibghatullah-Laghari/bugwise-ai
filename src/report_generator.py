
from src.quality_assessment import FIELDS, assess_bug_report, canonical_placeholder, normalize_text


def generate_improved_report(report):
    """Create a structured report without inventing details."""

    assessment = assess_bug_report(report)
    lines = [
        "# Improved Bug Report",
        "",
        "This version keeps the reporter's known facts and makes missing information explicit without inventing details.",
        "",
    ]

    for key, label in FIELDS.items():
        value = normalize_text(report.get(key, "")) if isinstance(report, dict) else ""

        if not value or canonical_placeholder(value):
            body = "Missing — not provided."
        else:
            body = value

        lines.extend([
            f"## {label}",
            "",
            body,
            "",
        ])

    information_needed = [
        label for label in [item["label"] for item in assessment["field_results"].values()]
        if assessment["field_results"][next(key for key, value in FIELDS.items() if value == label)]["status"] != "adequate"
    ]

    lines.append("## Information still needed")
    lines.append("")
    if information_needed:
        for label in information_needed:
            lines.append(f"- {label}: more detail is needed for a complete report.")
    else:
        lines.append("No obvious missing information was identified in the current report.")

    lines.append("")
    lines.append("## Improvement notes")
    lines.append("")

    notes = []
    for key, result in assessment["field_results"].items():
        if result["status"] == "adequate":
            continue
        notes.append(f"- {result['label']}: {result['suggestion']}")

    if notes:
        lines.extend(notes)
    else:
        lines.append("No specific improvement notes are needed based on the supplied information.")

    return "\n".join(lines)
