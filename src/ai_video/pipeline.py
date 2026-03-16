from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

from .config import Config
from .images import generate_images_hf
from .llm import generate_storyboard
from .tts import generate_audio
from .video import build_video


def run_pipeline(
    cfg: Config,
    topic: str,
    duration_sec: int,
    language: str,
    out_dir: Path,
    tts_provider: Literal["openai", "elevenlabs"],
    skip_tts: bool,
    skip_images: bool,
    skip_video: bool,
    images_dir: Path | None,
    upload: bool,
    privacy_status: str,
) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)

    storyboard = generate_storyboard(cfg, topic, duration_sec, language)
    (out_dir / "storyboard.json").write_text(
        json.dumps(storyboard, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    narration_text = "\n".join(scene["narration"] for scene in storyboard["scenes"]).strip()
    (out_dir / "script.txt").write_text(narration_text, encoding="utf-8")

    audio_path = out_dir / "voiceover.mp3"
    if not skip_tts:
        generate_audio(cfg, narration_text, audio_path, tts_provider)

    if images_dir:
        image_paths = sorted(images_dir.glob("*.png")) + sorted(images_dir.glob("*.jpg"))
    else:
        image_paths = []

    if not image_paths and not skip_images:
        prompts = [scene["image_prompt"] for scene in storyboard["scenes"]]
        image_paths = generate_images_hf(cfg, prompts, out_dir / "images")

    video_path = out_dir / "final_video.mp4"
    if not skip_video:
        if not audio_path.exists():
            raise FileNotFoundError("Audio file not found. Enable TTS or provide audio.")
        if not image_paths:
            raise FileNotFoundError("No images found. Enable image generation or provide images.")
        build_video(image_paths, audio_path, video_path)

    if upload:
        if not cfg.youtube_client_secrets_file or not cfg.youtube_token_file:
            raise ValueError("YouTube client secrets/token file paths are required for upload")
        from .youtube_upload import upload_to_youtube
        upload_to_youtube(
            Path(cfg.youtube_client_secrets_file),
            Path(cfg.youtube_token_file),
            video_path,
            storyboard.get("title", ""),
            storyboard.get("description", ""),
            storyboard.get("tags", []),
            privacy_status=privacy_status,
        )

    return {
        "storyboard": storyboard,
        "audio_path": str(audio_path),
        "video_path": str(video_path),
        "images": [str(p) for p in image_paths],
    }
