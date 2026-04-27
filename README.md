# PolicyLens AI

Understand government policies in simple, personalized language.

PolicyLens AI is a Python/Flask web app that helps users understand Indian and global government policies. Users enter a policy name, choose their role and preferred language, and receive a structured AI-generated explanation.

## Features

- Policy explanations tailored by user type
- Multiple Indian language options
- Structured output:
  - Simple explanation
  - Why it was introduced
  - Personal impact
  - Pros and cons
  - Summary
- Live web context using DuckDuckGo search
- One-click copy in the frontend

## Tech Stack

| Component | Technology |
| --- | --- |
| Frontend | HTML, CSS, React 18 via CDN, plain JavaScript |
| Backend | Python, Flask |
| Production Server | Gunicorn |
| AI Provider | Anthropic Claude API |
| Web Context | duckduckgo-search |
| Deployment | Render |

## Project Structure

```text
.
├── app.py
├── api/
│   ├── ai.py
│   ├── constants.py
│   ├── routes.py
│   ├── search.py
│   └── utils.py
├── public/
│   ├── index.html
│   ├── css/
│   └── js/
├── requirements.txt
├── Procfile
└── render.yaml
```

## Local Setup

1. Create and activate a Python virtual environment.

```bash
python -m venv .venv
```

2. Install dependencies.

```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your Anthropic API key.

```bash
ANTHROPIC_API_KEY=your_api_key_here
```

4. Run the app.

```bash
python app.py
```

The app runs locally at:

```text
http://localhost:3000
```

## Deployment

This project is configured for Render as a Python web service.

```yaml
buildCommand: pip install -r requirements.txt
startCommand: gunicorn app:app --bind 0.0.0.0:$PORT
```

Required environment variable:

```text
ANTHROPIC_API_KEY
```
