from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

import requests

from .config import Config


def generate_audio_openai(cfg: Config, text: str, out_path: Path) -> None:
    if not cfg.openai_api_key:
        raise ValueError("OPENAI_API_KEY is required for OpenAI TTS")

    url = "https://api.openai.com/v1/audio/speech"
    headers = {
        "Authorization": f"Bearer {cfg.openai_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": cfg.openai_tts_model,
        "voice": cfg.openai_tts_voice,
        "input": text,
        "format": "mp3",
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=120)
    response.raise_for_status()
    out_path.write_bytes(response.content)


def generate_audio_elevenlabs(cfg: Config, text: str, out_path: Path) -> None:
    if not cfg.elevenlabs_api_key or not cfg.elevenlabs_voice_id:
        raise ValueError("ELEVENLABS_API_KEY and ELEVENLABS_VOICE_ID are required")

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{cfg.elevenlabs_voice_id}"
    headers = {
        "xi-api-key": cfg.elevenlabs_api_key,
        "Content-Type": "application/json",
    }
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.4,
            "similarity_boost": 0.8,
        },
    }

    response = requests.post(url, headers=headers, json=payload, timeout=120)
    response.raise_for_status()
    out_path.write_bytes(response.content)


def generate_audio(
    cfg: Config,
    text: str,
    out_path: Path,
    provider: Literal["openai", "elevenlabs"],
) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if provider == "openai":
        generate_audio_openai(cfg, text, out_path)
    elif provider == "elevenlabs":
        generate_audio_elevenlabs(cfg, text, out_path)
    else:
        raise ValueError(f"Unknown TTS provider: {provider}")