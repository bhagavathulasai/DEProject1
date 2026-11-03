from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "DentalVision API")
    app_version: str = os.getenv("APP_VERSION", "1.0.0")
    api_prefix: str = "/api/v1"
    environment: str = os.getenv("ENVIRONMENT", "development")
    log_level: str = os.getenv("LOG_LEVEL", "INFO").upper()
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://dentalvision:dentalvision@localhost:5432/dentalvision",
    )
    model_dir: Path = Path(os.getenv("DENTALVISION_MODEL_DIR", BASE_DIR / "models"))
    upload_dir: Path = Path(os.getenv("DENTALVISION_UPLOAD_DIR", BASE_DIR / "storage" / "uploads"))
    secure_storage_dir: Path = Path(
        os.getenv("DENTALVISION_STORAGE_DIR", BASE_DIR / "storage" / "secure")
    )
    max_upload_size_mb: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "8"))
    allowed_extensions: tuple[str, ...] = (".png", ".jpg", ".jpeg", ".bmp", ".webp")
    default_model_path: str | None = os.getenv("DENTALVISION_MODEL_PATH")
    secret_key: str = os.getenv("SECRET_KEY", "dentalvision-dev-secret")

    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024

    def __post_init__(self):
        object.__setattr__(self, "model_dir", Path(self.model_dir))
        object.__setattr__(self, "upload_dir", Path(self.upload_dir))
        object.__setattr__(self, "secure_storage_dir", Path(self.secure_storage_dir))


settings = Settings()
