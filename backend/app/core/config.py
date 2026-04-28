from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
SAMPLES_DIR = BASE_DIR / "samples"
FRONTEND_DIR = BASE_DIR.parent / "frontend"
DEFAULT_SQLITE_DB = DATA_DIR / "forensic_wm.db"


class Settings(BaseSettings):
    app_name: str = "Forensic Watermarking"
    environment: str = "dev"
    database_url: str = f"sqlite:///{DEFAULT_SQLITE_DB.as_posix()}"
    data_dir: Path = DATA_DIR
    samples_dir: Path = SAMPLES_DIR
    frontend_dir: Path = FRONTEND_DIR
    redis_url: str = "redis://localhost:6379/0"
    secret_key: str = "change-this-in-production"
    payload_hmac_key: str = "change-this-payload-hmac-key"
    cors_origins: list[str] = ["*"]
    watermark_window: int = 3  # was 30; denser for higher detection confidence

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
