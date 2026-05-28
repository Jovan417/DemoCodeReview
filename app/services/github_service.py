from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from app.core.config import settings


class GitHubService:
    def fetch_diff(
        self,
        repository_url: str,
        pull_request_number: int | None = None,
        commit_sha: str | None = None,
    ) -> str:
        owner, repo = self._parse_github_repository(repository_url)

        if pull_request_number:
            api_url = (
                f"https://api.github.com/repos/{owner}/{repo}"
                f"/pulls/{pull_request_number}"
            )
        elif commit_sha:
            api_url = (
                f"https://api.github.com/repos/{owner}/{repo}/commits/{commit_sha}"
            )
        else:
            raise ValueError("Provide a pull_request_number or commit_sha.")

        request = Request(
            api_url,
            headers=self._headers(),
            method="GET",
        )

        try:
            with urlopen(request, timeout=30) as response:
                return response.read().decode("utf-8")
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(
                f"GitHub returned {exc.code} while fetching the diff: {detail}"
            ) from exc
        except URLError as exc:
            raise RuntimeError(f"Could not connect to GitHub: {exc.reason}") from exc

    def _headers(self) -> dict[str, str]:
        headers = {
            "Accept": "application/vnd.github.v3.diff",
            "User-Agent": "cloudfit-code-review-api",
        }

        if settings.github_token:
            headers["Authorization"] = f"Bearer {settings.github_token}"

        return headers

    def _parse_github_repository(self, repository_url: str) -> tuple[str, str]:
        parsed_url = urlparse(repository_url)
        host = parsed_url.netloc.lower()

        if host not in {"github.com", "www.github.com"}:
            raise ValueError("Only GitHub repository URLs are supported.")

        path_parts = [part for part in parsed_url.path.split("/") if part]
        if len(path_parts) < 2:
            raise ValueError("Repository URL must include owner and repository name.")

        owner = path_parts[0]
        repo = path_parts[1].removesuffix(".git")
        return owner, repo
