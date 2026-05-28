from app.models.review import ReviewResult
from app.schemas.review import CodeReviewRequest
from app.services.github_service import GitHubService
from app.services.llm_service import LLMService


class CodeReviewService:
    def __init__(
        self,
        github_service: GitHubService | None = None,
        llm_service: LLMService | None = None,
    ) -> None:
        self.github_service = github_service or GitHubService()
        self.llm_service = llm_service or LLMService()

    def review_code(self, request: CodeReviewRequest) -> ReviewResult:
        diff = request.diff.strip() if request.diff else None

        if not diff and request.repository_url:
            diff = self.github_service.fetch_diff(
                repository_url=str(request.repository_url),
                pull_request_number=request.pull_request_number,
                commit_sha=request.commit_sha,
            )

        if not diff:
            raise ValueError("No code changes were found to review.")

        return self.llm_service.review_diff(diff)
