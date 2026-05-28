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

`commit_sha` must be the actual hexadecimal commit id or abbreviated commit id,
not the commit message.

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

The examples below assume the API is running locally at:

```text
http://127.0.0.1:8000
```

### `GET /`

Checks that the API is running and returns the API docs path.

Example response:

```json
{
  "message": "Code Review API is running.",
  "docs": "/docs"
}
```

### `GET /health`

Health check endpoint for uptime monitoring.

Example response:

```json
{
  "status": "ok"
}
```

### `POST /code-review/`

Reviews code changes and returns a summary plus line-level comments.

You can use this endpoint in one of three ways:

1. Send a raw git diff directly with `diff`.
2. Send a GitHub repository URL with `pull_request_number`.
3. Send a GitHub repository URL with `commit_sha`.

#### Request body

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `repository_url` | string or null | Required for GitHub reviews | GitHub repository URL, for example `https://github.com/org/repo`. |
| `branch` | string | No | Branch name. Defaults to `main`. |
| `pull_request_number` | integer or null | Required when reviewing a pull request | GitHub pull request number. Must be greater than or equal to `1`. |
| `commit_sha` | string or null | Required when reviewing a commit | Git commit SHA or abbreviated SHA. Must be hexadecimal and between 7 and 64 characters. |
| `diff` | string or null | Required when reviewing a direct diff | Raw git diff. When provided, the API reviews this directly and does not fetch from GitHub. |

You must provide either:

- `diff`
- `repository_url` plus `pull_request_number`
- `repository_url` plus `commit_sha`

#### Direct diff example

Request:

```powershell
curl.exe -X POST "http://127.0.0.1:8000/code-review/" `
  -H "Content-Type: application/json" `
  -d '{
    "branch": "main",
    "diff": "diff --git a/app.py b/app.py\n+++ b/app.py\n@@ -1,1 +1,2 @@\n+print(\"debug\")"
  }'
```

Response:

```json
{
  "status": "completed",
  "repository_url": null,
  "branch": "main",
  "summary": "Found 1 potential issue(s) in the submitted diff.",
  "comments": [
    {
      "message": "Use structured logging instead of print statements.",
      "severity": "warning",
      "file_path": "app.py",
      "line_number": 1
    }
  ]
}
```

#### GitHub pull request example

Request body:

```json
{
  "repository_url": "https://github.com/example/project",
  "branch": "main",
  "pull_request_number": 12
}
```

#### GitHub commit example

Request body:

```json
{
  "repository_url": "https://github.com/example/project",
  "branch": "main",
  "commit_sha": "a1b2c3d"
}
```

#### Response fields

| Field | Type | Description |
| --- | --- | --- |
| `status` | string | Current review status. Successful reviews return `completed`. |
| `repository_url` | string or null | Repository URL from the request, or `null` for direct diff reviews. |
| `branch` | string | Branch from the request. |
| `summary` | string | Human-readable review summary. |
| `comments` | array | Review comments found in the submitted diff. |

Each comment contains:

| Field | Type | Description |
| --- | --- | --- |
| `message` | string | Review message. |
| `severity` | string | One of `info`, `warning`, or `error`. |
| `file_path` | string or null | File path related to the comment, when available. |
| `line_number` | integer or null | New-file line number related to the comment, when available. |

#### Error responses

`422 Unprocessable Entity` is returned when the request body fails schema
validation, for example:

- Missing `diff` and missing GitHub review source.
- `commit_sha` is not a hexadecimal SHA.
- `pull_request_number` is less than `1`.

Example:

```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body"],
      "msg": "Value error, Provide either diff, or repository_url with pull_request_number or commit_sha.",
      "input": {
        "branch": "main"
      }
    }
  ]
}
```

`400 Bad Request` is returned when the request passes schema validation but the
review source cannot be used, for example:

- `repository_url` is not a GitHub repository URL.
- No code changes were found to review.

Example:

```json
{
  "detail": "Only GitHub repository URLs are supported."
}
```

`502 Bad Gateway` is returned when the API cannot fetch the diff from GitHub.

Example:

```json
{
  "detail": "Could not connect to GitHub: ..."
}
```

# DemoCodeReview
