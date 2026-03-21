from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv


def load_env() -> None:
    project_root = Path(__file__).resolve().parents[2]
    load_dotenv(dotenv_path=project_root / ".env")


def _clean_model_id(value: str, default: str) -> str:
    v = (value or "").strip()
    if not v:
        return default
    if "=" in v:
        v = v.split("=")[-1].strip()
    return v


def _pick_youtube_file_env(primary: str, fallback: str, json_env: str, default_path: str) -> str:
    value = os.getenv(primary, "").strip()
    if not value:
        value = os.getenv(fallback, "").strip()
    if not value and os.getenv(json_env, "").strip():
        value = default_path
    return value


@dataclass
class Config:
    openai_api_key: str
    openai_text_model: str
    openai_image_model: str
    openai_tts_model: str
    openai_tts_voice: str
    groq_api_key: str | None
    groq_text_model: str
    hf_api_key: str | None
    hf_image_model: str | None
    hf_provider: str
    elevenlabs_api_key: str | None
    elevenlabs_voice_id: str | None
    youtube_client_secrets_file: str | None
    youtube_token_file: str | None


def get_config() -> Config:
    load_env()
    groq_model_default = "llama-3.3-70b-versatile"
    groq_model = _clean_model_id(os.getenv("GROQ_TEXT_MODEL", ""), groq_model_default)

    youtube_client_secrets_file = _pick_youtube_file_env(
        "YOUTUBE_CLIENT_SECRETS_FILE",
        "YOUTUBE_CLIENT_SECRET_FILE",
        "YOUTUBE_CLIENT_SECRETS_JSON",
        "/data/client_secrets.json",
    )
    youtube_token_file = _pick_youtube_file_env(
        "YOUTUBE_TOKEN_FILE",
        "YOUTUBE_TOKENFILE",
        "YOUTUBE_TOKEN_JSON",
        "/data/yt_token.json",
    )

    return Config(
        openai_api_key=os.getenv("OPENAI_API_KEY", "").strip(),
        openai_text_model=os.getenv("OPENAI_TEXT_MODEL", "gpt-4.1").strip(),
        openai_image_model=os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-1").strip(),
        openai_tts_model=os.getenv("OPENAI_TTS_MODEL", "gpt-4o-mini-tts").strip(),
        openai_tts_voice=os.getenv("OPENAI_TTS_VOICE", "alloy").strip(),
        groq_api_key=os.getenv("GROQ_API_KEY", "").strip() or None,
        groq_text_model=groq_model,
        hf_api_key=os.getenv("HF_API_KEY", "").strip() or None,
        hf_image_model=os.getenv("HF_IMAGE_MODEL", "").strip() or None,
        hf_provider=os.getenv("HF_PROVIDER", "hf-inference").strip() or "hf-inference",
        elevenlabs_api_key=os.getenv("ELEVENLABS_API_KEY", "").strip() or None,
        elevenlabs_voice_id=os.getenv("ELEVENLABS_VOICE_ID", "").strip() or None,
        youtube_client_secrets_file=youtube_client_secrets_file or None,
        youtube_token_file=youtube_token_file or None,
    )
