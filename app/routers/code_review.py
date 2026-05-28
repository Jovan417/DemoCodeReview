from fastapi import APIRouter, HTTPException, status

from app.schemas.review import CodeReviewRequest, CodeReviewResponse, ReviewComment
from app.services.code_review_service import CodeReviewService


router = APIRouter(prefix="/code-review", tags=["code review"])
code_review_service = CodeReviewService()


@router.post("/", response_model=CodeReviewResponse)
def review_code(request: CodeReviewRequest):
    try:
        result = code_review_service.review_code(request)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    return CodeReviewResponse(
        repository_url=request.repository_url,
        branch=request.branch,
        summary=result.summary,
        comments=[
            ReviewComment(
                message=comment.message,
                severity=comment.severity,
                file_path=comment.file_path,
                line_number=comment.line_number,
            )
            for comment in result.comments
        ],
    )
