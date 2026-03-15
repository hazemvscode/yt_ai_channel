from __future__ import annotations

import base64
import json
from pathlib import Path
from typing import Iterable

import requests

from .config import Config


def generate_images_openai(
    cfg: Config,
    prompts: Iterable[str],
    out_dir: Path,
    size: str = "1024x1024",
) -> list[Path]:
    if not cfg.openai_api_key:
        raise ValueError("OPENAI_API_KEY is required for OpenAI image generation")

    out_dir.mkdir(parents=True, exist_ok=True)
    url = "https://api.openai.com/v1/images/generations"
    headers = {
        "Authorization": f"Bearer {cfg.openai_api_key}",
        "Content-Type": "application/json",
    }

    paths: list[Path] = []
    for idx, prompt in enumerate(prompts, start=1):
        payload = {
            "model": cfg.openai_image_model,
            "prompt": prompt,
            "size": size,
            "n": 1,
            "response_format": "b64_json",
        }
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=180)
        response.raise_for_status()
        data = response.json()
        b64 = data["data"][0]["b64_json"]
        image_bytes = base64.b64decode(b64)

        path = out_dir / f"scene_{idx:02d}.png"
        path.write_bytes(image_bytes)
        paths.append(path)

    return paths