from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from ai_video.config import get_config
from ai_video.pipeline import run_pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AI video generation pipeline")
    parser.add_argument("--topic", required=True, help="Video topic")
    parser.add_argument("--duration", type=int, default=120, help="Target duration in seconds")
    parser.add_argument("--language", default="ar", help="Narration language")
    parser.add_argument("--out-dir", default="outputs", help="Output directory")
    parser.add_argument("--tts", choices=["openai", "elevenlabs"], default="openai")
    parser.add_argument("--skip-tts", action="store_true")
    parser.add_argument("--skip-images", action="store_true")
    parser.add_argument("--skip-video", action="store_true")
    parser.add_argument("--images-dir", default="", help="Use existing images in this folder")
    parser.add_argument("--upload", action="store_true", help="Upload to YouTube")
    parser.add_argument("--privacy", default="private", help="YouTube privacy status")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    cfg = get_config()

    images_dir = Path(args.images_dir).resolve() if args.images_dir else None
    out_dir = Path(args.out_dir).resolve()

    run_pipeline(
        cfg=cfg,
        topic=args.topic,
        duration_sec=args.duration,
        language=args.language,
        out_dir=out_dir,
        tts_provider=args.tts,
        skip_tts=args.skip_tts,
        skip_images=args.skip_images,
        skip_video=args.skip_video,
        images_dir=images_dir,
        upload=args.upload,
        privacy_status=args.privacy,
    )


if __name__ == "__main__":
    main()
