import os
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMConfig(BaseModel):
    primary_model: str = "gemini/gemini-2.5-pro"
    embedding_model: str = "nomic-embed"
    temperature: float = 0.1
    max_tokens: int = 4096
    timeout: int = 300


class Settings(BaseSettings):
    app_name: str = "OpenClaw AI API"
    debug: bool = False
    environment: str = "development"  # testing | development | production
    database_url: str = "postgresql+asyncpg://openclaw:openclaw_dev@localhost:5434/openclaw"
    redis_url: str = "redis://localhost:6379/0"
    qdrant_url: str = "http://localhost:6333"
    api_key: str = "bc0d688e1baaf577c56b6ab454b004004b40009c77f3253e"
    cors_origins: list[str] = ["*"]
    llm: LLMConfig = LLMConfig()

    # Google Gemini
    google_api_key: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def is_testing(self) -> bool:
        return self.environment == "testing" or os.getenv("PYTEST_CURRENT_TEST") is not None


settings = Settings()


def get_config() -> Settings:
    return settings
