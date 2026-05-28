from pydantic import BaseModel, Field, HttpUrl, model_validator

from app.models.review import ReviewSeverity


class CodeReviewRequest(BaseModel):
    repository_url: HttpUrl | None = Field(
        default=None,
        description="GitHub repository URL, for example https://github.com/org/repo.",
    )
    branch: str = Field(default="main", min_length=1, max_length=120)
    pull_request_number: int | None = Field(default=None, ge=1)
    commit_sha: str | None = Field(default=None, min_length=7, max_length=64)
    diff: str | None = Field(
        default=None,
        description="Raw git diff. If provided, the API reviews this directly.",
    )

    @model_validator(mode="after")
    def require_review_source(self) -> "CodeReviewRequest":
        has_direct_diff = bool(self.diff and self.diff.strip())
        has_github_source = bool(
            self.repository_url and (self.pull_request_number or self.commit_sha)
        )

        if not has_direct_diff and not has_github_source:
            raise ValueError(
                "Provide either diff, or repository_url with pull_request_number "
                "or commit_sha."
            )

        return self


class ReviewComment(BaseModel):
    message: str
    severity: ReviewSeverity
    file_path: str | None = None
    line_number: int | None = None


class CodeReviewResponse(BaseModel):
    status: str = "completed"
    repository_url: HttpUrl | None = None
    branch: str
    summary: str
    comments: list[ReviewComment]
