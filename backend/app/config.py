from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "EmoBook API"
    api_prefix: str = "/api/v1"
    database_url: str = "mysql+pymysql://emobook:emobook@localhost:3306/emobook"
    local_storage_root: Path = Path("backend/local_storage")
    public_storage_base_url: str = "/storage"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="EMOBOOK_",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()

