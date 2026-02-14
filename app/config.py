"""Application configuration loading and validation."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError


class Settings(BaseModel):
    """Runtime settings loaded from environment variables."""

    db_path: str = Field(alias="DB_PATH")
    confidence_threshold: float = Field(alias="CONFIDENCE_THRESHOLD")
    inbox_path: str = Field(alias="INBOX_PATH")
    outbox_path: str = Field(alias="OUTBOX_PATH")
    tracker_path: str = Field(alias="TRACKER_PATH")
    log_level: str = Field(alias="LOG_LEVEL")


def load_settings() -> Settings:
    """Load and validate application settings from .env and environment."""

    load_dotenv()

    raw = {
        "DB_PATH": os.getenv("DB_PATH"),
        "CONFIDENCE_THRESHOLD": os.getenv("CONFIDENCE_THRESHOLD"),
        "INBOX_PATH": os.getenv("INBOX_PATH"),
        "OUTBOX_PATH": os.getenv("OUTBOX_PATH"),
        "TRACKER_PATH": os.getenv("TRACKER_PATH"),
        "LOG_LEVEL": os.getenv("LOG_LEVEL"),
    }

    try:
        settings = Settings.model_validate(raw)
    except ValidationError as exc:
        raise ValueError(f"Invalid configuration: {exc}") from exc

    _ensure_directories(settings)
    return settings


def _ensure_directories(settings: Settings) -> None:
    """Create configured data directories if they do not already exist."""

    Path(settings.inbox_path).mkdir(parents=True, exist_ok=True)
    Path(settings.outbox_path).mkdir(parents=True, exist_ok=True)
    Path(settings.tracker_path).mkdir(parents=True, exist_ok=True)
    Path(settings.db_path).parent.mkdir(parents=True, exist_ok=True)
