from __future__ import annotations

from pathlib import Path
from typing import Iterable

from huggingface_hub import InferenceClient

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
