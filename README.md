
# BugWise AI

BugWise AI is a rule-based Streamlit application for assessing the quality of software bug reports before they are handed to a development team. It helps users spot missing information, weak reproduction steps, vague expected or actual behavior, and incomplete environment details.

## Main Features

- Structured form with six required fields:
  - Bug title
  - Bug description
  - Steps to reproduce
  - Expected behavior
  - Actual behavior
  - Environment details
- Transparent completeness calculation based on meaningful field content rather than raw text presence.
- Field-by-field status labels: missing, insufficient, unclear, and adequate.
- Targeted clarification questions based on the known gaps.
- Structured improved Markdown report preserving the reporter's original facts.
- Downloadable Markdown output.
- Deterministic pytest suite for assessment logic and report generation.

## Project Structure

```text
bugwise-ai/
├── app.py
├── README.md
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── agent.py
│   ├── quality_assessment.py
│   └── report_generator.py
├── tests/
│   ├── __init__.py
│   └── test_core.py
└── .venv/
```

## Python Requirements

- Python 3.10 or newer is recommended.
- Streamlit and pytest are required for the web app and automated tests.

## Installation

```bash
cd ~/Workspace/projects/bugwise-ai
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run the Application

```bash
streamlit run app.py
```

## Run Tests

```bash
python -m pytest -q
```

## Completeness Calculation

The completeness metric is based on the number of required fields that contain meaningful information, not simply any non-empty text:

```text
field_completeness = meaningful_fields / total_required_fields * 100
```

This means empty fields, placeholder-only values, and vague text do not count as complete. The metric is rounded to the nearest integer for display.

## Field Statuses

Each field is assigned one of the following statuses:

- missing: no useful information was supplied.
- insufficient: information exists, but it is too vague or incomplete to act on.
- unclear: the detail is ambiguous or contradictory enough that more clarification is needed.
- adequate: the field includes specific and usable information.

The system explains the status with a reason, supporting evidence excerpt, and an actionable suggestion.

## Known Limitations

- This is a transparent rule-based prototype, not a validated model.
- It detects likely quality issues using deterministic heuristics rather than learned predictions.
- It does not claim measured accuracy against a labelled benchmark unless such a benchmark exists.
- It is designed to support future evaluation with human-reviewed reports and labelled examples.

## Heuristic Assessment vs. Trained Model Performance

The current implementation is intentionally explainable and deterministic. It does not use severity labels as a proxy for report quality, and it does not claim machine-learning accuracy. If a labelled dataset becomes available, the project can later add a separate evaluation script that compares the rule-based engine against reviewed quality labels.

## Future Roadmap

- Add a human-annotation workflow for quality labels.
- Prepare evaluation scripts for labelled datasets and benchmark comparisons.
- Expand the rule set with more domain-aware heuristics.
- Explore optional NLP enhancements without replacing the transparent rule-based engine.
- Add more regression tests for edge cases and real-world bug reports..
