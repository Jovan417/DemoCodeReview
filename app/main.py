from fastapi import FastAPI

from .core.config import settings
from .routers import code_review


app = FastAPI(title=settings.app_name, version=settings.app_version)

app.include_router(code_review.router)


@app.get("/")
def root():
    return {"message": "Code Review API is running.", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok"}
