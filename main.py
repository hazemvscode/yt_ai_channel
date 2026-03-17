from __future__ import annotations

import argparse
import os
import sys
import time as time_module
from datetime import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from ai_video.config import get_config
from ai_video.llm import generate_topic
from ai_video.pipeline import run_pipeline
from ai_video.schedule import ScheduleConfig, should_run, get_next_run_time


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AI video generation pipeline")
    parser.add_argument("--topic", default="auto", help="Video topic or 'auto'")
    parser.add_argument("--themes", default="", help="Comma-separated themes for auto topic")
    parser.add_argument("--duration", type=int, default=120, help="Target duration in seconds")
    parser.add_argument("--language", default="en", help="Narration language")
    parser.add_argument("--out-dir", default="outputs", help="Output directory")
    parser.add_argument("--tts", choices=["openai", "elevenlabs", "hf", "edge"], default="elevenlabs")
    parser.add_argument("--skip-tts", action="store_true")
    parser.add_argument("--skip-images", action="store_true")
    parser.add_argument("--skip-video", action="store_true")
    parser.add_argument("--images-dir", default="", help="Use existing images in this folder")
    parser.add_argument("--upload", action="store_true", help="Upload to YouTube")
    parser.add_argument("--privacy", default="private", help="YouTube privacy status")
    parser.add_argument("--schedule", action="store_true", help="Enable random schedule gate")
    parser.add_argument("--loop", action="store_true", help="Run forever, checking schedule")
    parser.add_argument("--loop-sleep", type=int, default=300, help="Seconds to sleep between checks")
    return parser


def _build_schedule(args) -> ScheduleConfig:
    tz = os.getenv("SCHEDULE_TIMEZONE", "Africa/Cairo")
    window_start = os.getenv("SCHEDULE_WINDOW_START", "00:00")
    window_end = os.getenv("SCHEDULE_WINDOW_END", "23:59")
    daily_target = int(os.getenv("SCHEDULE_DAILY_TARGET", "5"))
    min_gap_hours = float(os.getenv("SCHEDULE_MIN_GAP_HOURS", "4.8"))

    return ScheduleConfig(
        timezone=tz,
        window_start=time.fromisoformat(window_start),
        window_end=time.fromisoformat(window_end),
        daily_target=daily_target,
        min_gap_minutes=int(round(min_gap_hours * 60)),
        state_path=Path(args.out_dir) / "schedule_state.json",
    )


def _run_once(args) -> None:
    cfg = get_config()

    if args.schedule:
        sched = _build_schedule(args)
        next_run = get_next_run_time(sched)
        if next_run:
            print(f"[next-run] {next_run}")
        if not should_run(sched):
            return

    themes = args.themes.strip() or os.getenv("TOPIC_THEMES", "").strip()
    topic = args.topic.strip()
    if topic.lower() == "auto":
        if not themes:
            raise ValueError("Set --themes or TOPIC_THEMES for auto topic.")
        topic = generate_topic(cfg, themes, args.language)

    images_dir = Path(args.images_dir).resolve() if args.images_dir else None
    out_dir = Path(args.out_dir).resolve()

    run_pipeline(
        cfg=cfg,
        topic=topic,
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


def main() -> None:
    args = build_parser().parse_args()

    if args.loop:
        while True:
            try:
                _run_once(args)
            except Exception as exc:
                print(f"[loop] error: {exc}")
            time_module.sleep(args.loop_sleep)
        return

    _run_once(args)


if __name__ == "__main__":
    main()

