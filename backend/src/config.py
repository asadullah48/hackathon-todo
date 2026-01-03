"""Environment configuration loader."""

from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str = "postgresql+asyncpg://user:password@localhost:5432/todo"

    # Security
    jwt_secret: str = "your-super-secret-jwt-key-min-32-characters-long"
    jwt_algorithm: str = "HS256"
    jwt_expiry_days: int = 7

    # CORS
    cors_origins: str = "http://localhost:3000"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True

    # OpenAI (for Phase 3 AI chatbot)
    openai_api_key: str | None = None

    @property
    def sync_database_url(self) -> str:
        """Get synchronous database URL for MCP server."""
        # Convert asyncpg to psycopg2 for sync operations
        return self.database_url.replace("+asyncpg", "")

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
