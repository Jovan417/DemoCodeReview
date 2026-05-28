from dataclasses import dataclass
from enum import StrEnum


class ReviewSeverity(StrEnum):
    info = "info"
    warning = "warning"
    error = "error"


@dataclass(frozen=True)
class ReviewIssue:
    message: str
    severity: ReviewSeverity = ReviewSeverity.info
    file_path: str | None = None
    line_number: int | None = None


@dataclass(frozen=True)
class ReviewResult:
    summary: str
    comments: list[ReviewIssue]
