"""Application configuration using Pydantic Settings.

Loads all environment variables from .env file for database,
authentication, AI services, and storage configuration.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Database (Neon PostgreSQL or Docker Postgres)
    DATABASE_URL: str = "postgresql+asyncpg://getshortlisted:getshortlisted_dev@db:5432/getshortlisted"

    # Google Gemini AI
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"

    # Cloudinary file storage
    CLOUDINARY_URL: str = "cloudinary://mock:mock@mock"

    # JWT Authentication
    JWT_SECRET_KEY: str = "72b3b6276a92e2e188138a4f508cce06e4cdef9b35412de434f4bd2f263d061d"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # ChromaDB vector store
    CHROMA_PERSIST_DIR: str = "./chroma_data"


settings = Settings()  # type: ignore[call-arg]
