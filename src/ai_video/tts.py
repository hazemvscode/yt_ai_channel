from __future__ import annotations

import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Literal

import requests

from .config import Config


def _debug_elevenlabs(cfg: Config) -> bool:
    return os.getenv("DEBUG_EL", "").strip().lower() in {"1", "true", "yes"}


def _print_elevenlabs_key(cfg: Config) -> None:
    key = cfg.elevenlabs_api_key or ""
    tail = key[-4:] if len(key) >= 4 else key
    print(f"[elevenlabs] key_len={len(key)} key_tail={tail} voice_id={cfg.elevenlabs_voice_id}")


def _check_voices(cfg: Config) -> None:
    try:
        r = requests.get("https://api.elevenlabs.io/v1/voices", headers={"xi-api-key": cfg.elevenlabs_api_key}, timeout=20)
        print(f"[elevenlabs] voices_status={r.status_code}")
        if r.status_code != 200:
            print(f"[elevenlabs] voices_error={r.text[:200]}")
    except Exception as exc:
        print(f"[elevenlabs] voices_check_error={exc}")


def _run_async(coro) -> None:
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        asyncio.run(coro)
        return
    new_loop = asyncio.new_event_loop()
    try:
        new_loop.run_until_complete(coro)
    finally:
        new_loop.close()


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

    if _debug_elevenlabs(cfg):
        _print_elevenlabs_key(cfg)
        _check_voices(cfg)

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
    if _debug_elevenlabs(cfg) and response.status_code != 200:
        print(f"[elevenlabs] tts_status={response.status_code}")
        print(f"[elevenlabs] tts_error={response.text[:300]}")
    response.raise_for_status()
    out_path.write_bytes(response.content)


def generate_audio_hf(cfg: Config, text: str, out_path: Path) -> None:
    if not cfg.hf_api_key:
        raise ValueError("HF_API_KEY is required for Hugging Face TTS")

    model = os.getenv("HF_TTS_MODEL", "facebook/mms-tts-eng")
    url = f"https://api-inference.huggingface.co/models/{model}"
    headers = {"Authorization": f"Bearer {cfg.hf_api_key}"}
    payload = {"inputs": text}

    response = requests.post(url, headers=headers, json=payload, timeout=180)
    response.raise_for_status()
    out_path.write_bytes(response.content)


def _ensure_edge_tts() -> None:
    try:
        import edge_tts  # noqa: F401
        return
    except Exception:
        print("[edge-tts] installing edge-tts...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "edge-tts"])


def generate_audio_edge(cfg: Config, text: str, out_path: Path) -> None:
    _ensure_edge_tts()
    import edge_tts

    voice = os.getenv("EDGE_TTS_VOICE", "en-US-GuyNeural")
    rate = os.getenv("EDGE_TTS_RATE", "+0%")
    pitch = os.getenv("EDGE_TTS_PITCH", "+0Hz")

    async def _run() -> None:
        communicate = edge_tts.Communicate(text, voice=voice, rate=rate, pitch=pitch)
        await communicate.save(str(out_path))

    _run_async(_run())


def generate_audio(
    cfg: Config,
    text: str,
    out_path: Path,
    provider: Literal["openai", "elevenlabs", "hf", "edge"],
) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if provider == "openai":
        generate_audio_openai(cfg, text, out_path)
    elif provider == "elevenlabs":
        generate_audio_elevenlabs(cfg, text, out_path)
    elif provider == "hf":
        generate_audio_hf(cfg, text, out_path)
    elif provider == "edge":
        generate_audio_edge(cfg, text, out_path)
    else:
        raise ValueError(f"Unknown TTS provider: {provider}")
