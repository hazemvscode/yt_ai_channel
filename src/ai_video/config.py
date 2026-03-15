from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv


def load_env() -> None:
    project_root = Path(__file__).resolve().parents[2]
    load_dotenv(dotenv_path=project_root / ".env")


@dataclass
class Config:
    openai_api_key: str
    openai_text_model: str
    openai_image_model: str
    openai_tts_model: str
    openai_tts_voice: str
    anthropic_api_key: str | None
    anthropic_model: str
    elevenlabs_api_key: str | None
    elevenlabs_voice_id: str | None
    youtube_client_secrets_file: str | None
    youtube_token_file: str | None


def get_config() -> Config:
    load_env()
    return Config(
        openai_api_key=os.getenv("OPENAI_API_KEY", "").strip(),
        openai_text_model=os.getenv("OPENAI_TEXT_MODEL", "gpt-4.1").strip(),
        openai_image_model=os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-1").strip(),
        openai_tts_model=os.getenv("OPENAI_TTS_MODEL", "gpt-4o-mini-tts").strip(),
        openai_tts_voice=os.getenv("OPENAI_TTS_VOICE", "alloy").strip(),
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY", "").strip() or None,
        anthropic_model=os.getenv("ANTHROPIC_MODEL", "claude-3-7-sonnet-20250219").strip(),
        elevenlabs_api_key=os.getenv("ELEVENLABS_API_KEY", "").strip() or None,
        elevenlabs_voice_id=os.getenv("ELEVENLABS_VOICE_ID", "").strip() or None,
        youtube_client_secrets_file=os.getenv("YOUTUBE_CLIENT_SECRETS_FILE", "").strip() or None,
        youtube_token_file=os.getenv("YOUTUBE_TOKEN_FILE", "").strip() or None,
    )
