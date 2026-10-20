
# BugWise AI

**An AI-assisted bug report quality assessment and clarification system.**

BugWise AI helps users identify incomplete or unclear bug reports, asks targeted clarification questions, and generates a structured bug report.

## Features

- Evaluates six key bug report fields:
  - Bug title
  - Bug description
  - Steps to reproduce
  - Expected behavior
  - Actual behavior
  - Environment details
- Identifies missing, vague, or potentially insufficient information using rule-based checks.
- Generates clarification questions for problematic fields.
- Produces an improved, structured bug report.
- Provides a simple Streamlit web interface.

## Technology Stack

- Python
- Streamlit
- pytest

## Getting Started

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd bugwise-ai
```

Replace `YOUR_GITHUB_REPOSITORY_URL` with your repository's actual URL.

### 2. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
python -m streamlit run app.py
```

### 5. Run tests

```bash
python -m pytest tests/ -v
```

## Current Status

This is an early prototype. Its current quality assessment uses transparent rule-based checks. It does not yet provide a validated machine-learning model for overall bug report quality.

## Project Structure

```text
bugwise-ai/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── src/
│   ├── agent.py
│   ├── quality_assessment.py
│   └── report_generator.py
└── tests/
    └── test_core.py
```
