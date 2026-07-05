"""Application configuration loaded from environment variables.

Secrets (QVeris and DeepSeek API keys) are backend-only. They are never
exposed through API responses, logs, or the frontend bundle.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

# Load .env from repo root and backend dir if present (local-first MVP).
for candidate in (Path(__file__).resolve().parents[2] / ".env", Path(__file__).resolve().parents[1] / ".env"):
    if candidate.exists():
        load_dotenv(candidate, override=False)


@dataclass
class Settings:
    qveris_api_key: str = field(default_factory=lambda: os.getenv("QVERIS_API_KEY", ""))
    qveris_base_url: str = field(default_factory=lambda: os.getenv("QVERIS_BASE_URL", "https://qveris.ai/api/v1"))
    qveris_session_id: str = field(default_factory=lambda: os.getenv("QVERIS_SESSION_ID", "alphainvestpro-local"))

    deepseek_api_key: str = field(default_factory=lambda: os.getenv("DEEPSEEK_API_KEY", ""))
    deepseek_base_url: str = field(default_factory=lambda: os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"))
    deepseek_model: str = field(default_factory=lambda: os.getenv("DEEPSEEK_MODEL", "deepseek-chat"))

    database_url: str = field(
        default_factory=lambda: os.getenv("DATABASE_URL", "sqlite:///./alphainvestpro.db")
    )

    # Small pause between orchestrator steps so progress is visible in the UI.
    step_delay_seconds: float = field(
        default_factory=lambda: float(os.getenv("ANALYSIS_STEP_DELAY_SECONDS", "0.6"))
    )


def get_settings() -> Settings:
    return Settings()
