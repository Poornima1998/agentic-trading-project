from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
REPORTS_DIR = BASE_DIR / "reports"

RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


@dataclass(frozen=True)
class Settings:
    aws_access_key_id: str | None = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_access_key: str | None = os.getenv("AWS_SECRET_ACCESS_KEY")
    aws_default_region: str = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
    s3_bucket: str | None = os.getenv("S3_BUCKET")
    database_url: str | None = os.getenv("DATABASE_URL")
    newsapi_key: str | None = os.getenv("NEWSAPI_KEY")
    default_period: str = os.getenv("DEFAULT_PERIOD", "1y")
    default_interval: str = os.getenv("DEFAULT_INTERVAL", "1d")


settings = Settings()
