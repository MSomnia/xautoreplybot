"""Configuration helpers for the X auto-reply bot."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    x_main_user_id: str
    x_api_key: str
    x_api_secret: str
    x_access_token: str
    x_access_token_secret: str
    x_bearer_token: str
    grok_api_key: str
    bot_system_prompt: str
    grok_model: str = "grok-4.1"
    grok_base_url: str = "https://api.x.ai/v1"
    max_generate_attempts: int = 3
    max_filter_attempts: int = 3
    recent_reply_window: int = 20
    max_reply_chars: int = 280


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def _optional_env(name: str, default: str) -> str:
    value = os.getenv(name)
    return value if value else default


def load_settings() -> Settings:
    """Load and validate all required environment variables."""
    return Settings(
        x_main_user_id=_require_env("X_MAIN_USER_ID"),
        x_api_key=_require_env("X_API_KEY"),
        x_api_secret=_require_env("X_API_SECRET"),
        x_access_token=_require_env("X_ACCESS_TOKEN"),
        x_access_token_secret=_require_env("X_ACCESS_TOKEN_SECRET"),
        x_bearer_token=_require_env("X_BEARER_TOKEN"),
        grok_api_key=_require_env("GROK_API_KEY"),
        bot_system_prompt=_require_env("BOT_SYSTEM_PROMPT"),
        grok_model=_optional_env("GROK_MODEL", "grok-4.1"),
        grok_base_url=_optional_env("GROK_BASE_URL", "https://api.x.ai/v1"),
    )
