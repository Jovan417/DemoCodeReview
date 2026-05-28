import re

from app.models.review import ReviewIssue, ReviewResult, ReviewSeverity


class LLMService:
    def review_diff(self, diff: str) -> ReviewResult:
        comments = self._review_with_local_rules(diff)

        if comments:
            summary = f"Found {len(comments)} potential issue(s) in the submitted diff."
        else:
            summary = "No obvious issues were found in the submitted diff."

        return ReviewResult(summary=summary, comments=comments)

    def _review_with_local_rules(self, diff: str) -> list[ReviewIssue]:
        comments: list[ReviewIssue] = []
        current_file: str | None = None
        new_line_number: int | None = None

        for line in diff.splitlines():
            if line.startswith("+++ "):
                current_file = self._normalize_file_path(line[4:].strip())
                continue

            if line.startswith("@@"):
                new_line_number = self._extract_new_line_number(line)
                continue

            if line.startswith("+") and not line.startswith("+++"):
                content = line[1:]
                comments.extend(
                    self._review_added_line(
                        content=content,
                        file_path=current_file,
                        line_number=new_line_number,
                    )
                )
                if new_line_number is not None:
                    new_line_number += 1
                continue

            if line.startswith(" ") and new_line_number is not None:
                new_line_number += 1

        return comments

    def _review_added_line(
        self,
        content: str,
        file_path: str | None,
        line_number: int | None,
    ) -> list[ReviewIssue]:
        comments: list[ReviewIssue] = []
        lowered_content = content.lower()

        if "todo" in lowered_content:
            comments.append(
                ReviewIssue(
                    message="TODO left in new code.",
                    severity=ReviewSeverity.info,
                    file_path=file_path,
                    line_number=line_number,
                )
            )

        if "print(" in content:
            comments.append(
                ReviewIssue(
                    message="Use structured logging instead of print statements.",
                    severity=ReviewSeverity.warning,
                    file_path=file_path,
                    line_number=line_number,
                )
            )

        if re.search(r"\bexcept\s*(Exception)?\s*:", content):
            comments.append(
                ReviewIssue(
                    message="Avoid broad exception handlers without specific recovery.",
                    severity=ReviewSeverity.warning,
                    file_path=file_path,
                    line_number=line_number,
                )
            )

        if self._looks_like_secret_assignment(content):
            comments.append(
                ReviewIssue(
                    message="Potential secret or credential added in code.",
                    severity=ReviewSeverity.error,
                    file_path=file_path,
                    line_number=line_number,
                )
            )

        if len(content) > 120:
            comments.append(
                ReviewIssue(
                    message="Line is longer than 120 characters.",
                    severity=ReviewSeverity.warning,
                    file_path=file_path,
                    line_number=line_number,
                )
            )

        return comments

    def _extract_new_line_number(self, hunk_header: str) -> int | None:
        match = re.search(r"\+(\d+)", hunk_header)
        if not match:
            return None

        return int(match.group(1))

    def _normalize_file_path(self, file_path: str) -> str | None:
        if file_path == "/dev/null":
            return None
        if file_path.startswith("b/"):
            return file_path[2:]
        return file_path

    def _looks_like_secret_assignment(self, content: str) -> bool:
        lowered_content = content.lower()
        secret_names = ("password", "secret", "token", "api_key", "apikey")

        if not any(name in lowered_content for name in secret_names):
            return False

        if "os.getenv" in content or "os.environ" in content:
            return False

        return "=" in content
