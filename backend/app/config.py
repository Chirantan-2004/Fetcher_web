from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "sqlite:///./fetcher.db"
    fetch_timeout: float = 20.0
    max_response_size: int = 5_000_000
    user_agent: str = "Fetcher/1.0 (+https://localhost)"
    enable_browser_rendering: bool = False
    storage_type: str = "local"
    storage_path: str = "./storage"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    log_level: str = "INFO"
    max_batch_size: int = 10
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

@lru_cache
def get_settings() -> Settings:
    return Settings()
