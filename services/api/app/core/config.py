"""Application configuration using Pydantic Settings."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration parameters for AgriSmart."""

    PROJECT_NAME: str = "AgriSmart API"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEMO_MODE: bool = True

    # Server binding
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # CORS
    ALLOWED_ORIGINS: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ]
    )

    # Database & Storage
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/agrismart"
    STATIC_DIR: str = "./app/static"

    # Directory holding ONNX weights for crop identification and disease models
    AI_MODEL_PATH: str = "./models"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
