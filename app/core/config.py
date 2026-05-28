import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "Cloudfit Code Review API")
    app_version: str = os.getenv("APP_VERSION", "1.0.0")
    github_token: str | None = os.getenv("GITHUB_TOKEN") or None
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY") or None


settings = Settings()
