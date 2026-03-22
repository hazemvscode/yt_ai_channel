from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Iterable

import requests
from huggingface_hub import InferenceClient
from PIL import Image

from .config import Config


def generate_images_hf(
    cfg: Config,
    prompts: Iterable[str],
    out_dir: Path,
) -> list[Path]:
    if not cfg.hf_api_key:
        raise ValueError("HF_API_KEY is required for Hugging Face image generation")

    out_dir.mkdir(parents=True, exist_ok=True)
    client = InferenceClient(api_key=cfg.hf_api_key, provider=cfg.hf_provider)
    model_id = cfg.hf_image_model or None

    paths: list[Path] = []
    for idx, prompt in enumerate(prompts, start=1):
        image = client.text_to_image(prompt=prompt, model=model_id)
        path = out_dir / f"scene_{idx:02d}.png"
        image.save(path)
        paths.append(path)

    return paths


def _download_image(url: str, timeout_sec: int = 60) -> Image.Image:
    resp = requests.get(url, timeout=timeout_sec)
    resp.raise_for_status()
    image = Image.open(BytesIO(resp.content))
    if image.mode != "RGB":
        image = image.convert("RGB")
    return image


def generate_images_es24(
    cfg: Config,
    prompts: Iterable[str],
    out_dir: Path,
) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)

    endpoint = cfg.es24_endpoint
    style = cfg.es24_style
    ratio = cfg.es24_ratio

    paths: list[Path] = []
    for idx, prompt in enumerate(prompts, start=1):
        payload = {"prompt": prompt, "style": style, "ratio": ratio}
        resp = requests.post(endpoint, json=payload, timeout=90)
        resp.raise_for_status()
        data = resp.json()

        if not data.get("status"):
            raise ValueError(f"ES24 error: {data}")

        images = data.get("images") or []
        if not images:
            raise ValueError(f"ES24 returned no images: {data}")

        image_url = images[0]
        image = _download_image(image_url)
        path = out_dir / f"scene_{idx:02d}.png"
        image.save(path, format="PNG")
        paths.append(path)

    return paths
