"""
VANTAGE — Core Configuration
Loads all environment variables with type safety.
"""
from functools import lru_cache
from pathlib import Path
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_ENV_FILE = Path(__file__).resolve().parents[3] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(str(ROOT_ENV_FILE), ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── App ──────────────────────────────────────
    app_name: str = "VANTAGE"
    app_version: str = "1.0.0"
    debug: bool = False
    secret_key: str = "change-me-in-production"
    cors_origins: list[str] = ["http://localhost:3000"]

    # ── Database ─────────────────────────────────
    database_url: str = "postgresql+psycopg://vantage:vantage_pass@localhost:5432/vantage_db"
    database_url_sync: str = "postgresql+psycopg://vantage:vantage_pass@localhost:5432/vantage_db"

    # ── Redis ────────────────────────────────────
    redis_url: str = "redis://localhost:6379/0"

    # ── LLM ──────────────────────────────────────
    llm_provider: Literal["openai", "ollama"] = "openai"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"

    # ── ML ───────────────────────────────────────
    embedding_model: str = "all-MiniLM-L6-v2"
    similarity_threshold: float = 0.82

    # ── Scraper ───────────────────────────────────
    scrape_interval_minutes: int = 30
    max_articles_per_crawl: int = 50


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
