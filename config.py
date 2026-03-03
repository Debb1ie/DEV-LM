from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # App
    APP_ENV: str = "development"
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./devlog.db"
    # For Postgres: postgresql+asyncpg://user:pass@localhost/devlog

    # Anthropic
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-sonnet-4-20250514"
    ANTHROPIC_MAX_TOKENS: int = 1000

    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:5500"]

    # Rate limiting
    RATE_LIMIT_REQUESTS: int = 60       # requests per window
    RATE_LIMIT_WINDOW_SECONDS: int = 60  # 1 minute window
    CHAT_RATE_LIMIT_REQUESTS: int = 20   # stricter limit for AI calls
    CHAT_RATE_LIMIT_WINDOW_SECONDS: int = 60

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
