"""Application configuration using Pydantic settings."""

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application settings
    app_name: str = "Gradio Chatbot"
    app_host: str = "0.0.0.0"
    app_port: int = 8080
    debug: bool = False

    # AWS settings
    aws_region: str = "us-east-1"
    aws_secret_name: Optional[str] = None

    # Database settings (can be overridden by Secrets Manager)
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "chatbot"
    db_user: str = "postgres"
    db_password: str = "postgres"

    # Bedrock settings
    bedrock_model_id: str = "mistral.mistral-large-2402-v1:0"
    bedrock_max_tokens: int = 1024
    bedrock_temperature: float = 0.7

    # Auth settings
    auth_enabled: bool = True

    @property
    def database_url(self) -> str:
        """Build PostgreSQL connection URL."""
        return (
            f"postgresql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
