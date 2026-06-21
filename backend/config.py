from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "OpenClaw AI API"
    debug: bool = False
    database_url: str = "postgresql+asyncpg://user:pass@localhost:5432/openclaw"
    redis_url: str = "redis://localhost:6379/0"
    qdrant_url: str = "http://localhost:6333"
    api_key: str = "default_api_key"
    cors_origins: list[str] = ["*"]
    
    class Config:
        env_file = ".env"

settings = Settings()
