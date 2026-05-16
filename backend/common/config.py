from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "EmoBook API"
    api_prefix: str = "/api/v1"
    database_url: str = "mysql+pymysql://emobook:emobook@localhost:3306/emobook"
    local_storage_root: Path = Path("backend/local_storage")
    public_storage_base_url: str = "/storage"
    elevenlabs_api_key: str | None = None
    elevenlabs_base_url: str = "https://api.elevenlabs.io"
    elevenlabs_tts_model_id: str = "eleven_multilingual_v2"
    elevenlabs_output_format: str = "mp3_44100_128"
    elevenlabs_remove_background_noise: bool = True

    jwt_secret_key: str = "your-super-secret-key-for-development-only"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 10080  # 60 * 24 * 7 (1 week)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="EMOBOOK_",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
