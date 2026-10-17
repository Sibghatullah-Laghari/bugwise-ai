
from src.quality_assessment import FIELDS


def generate_improved_report(report):
    """Create a structured report without inventing details."""

    lines = ["# Improved Bug Report"]

    for key, label in FIELDS.items():
        value = str(report.get(key, "") or "").strip()

        lines.append(f"\n## {label}")
        lines.append(
            value if value else "Unknown — not provided."
        )

    return "\n".join(lines)
