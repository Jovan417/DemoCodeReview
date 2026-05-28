# Cloudfit Code Review API

FastAPI project organized around a code review workflow.

## Project structure

```text
app/
├── main.py
├── models/
│   └── review.py
├── schemas/
│   └── review.py
├── routers/
│   └── code_review.py
├── services/
│   ├── code_review_service.py
│   ├── llm_service.py
│   └── github_service.py
└── core/
    └── config.py
```

The service can review a raw git diff directly. It can also fetch a GitHub pull
request or commit diff when you provide a GitHub repository URL and either a
pull request number or commit SHA.

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open the API documentation:

```text
http://127.0.0.1:8000/docs
```

## Endpoints

- `GET /`
- `GET /health`
- `POST /code-review/`

## Example request

```json
{
  "repository_url": "https://github.com/example/project",
  "branch": "main",
  "pull_request_number": 12
}
```

You can also send a diff directly:

```json
{
  "branch": "main",
  "diff": "diff --git a/app.py b/app.py\n+++ b/app.py\n@@ -1,1 +1,2 @@\n+print(\"debug\")"
}
```
# DemoCodeReview
