from __future__ import annotations

import os
from pathlib import Path

from moviepy import AudioFileClip, ColorClip, ImageClip, concatenate_videoclips


def build_video(
    images: list[Path],
    audio_path: Path,
    out_path: Path,
    fps: int = 24,
    target_size: tuple[int, int] = (1080, 1920),
    min_image_duration: float = 3.5,
    transition_duration: float = 0.25,
) -> None:
    if not images:
        raise ValueError("No images provided")

    audio = AudioFileClip(str(audio_path))

    # Pick a number of images so each stays on screen >= min_image_duration
    max_images = max(1, int((audio.duration + transition_duration) // (min_image_duration + transition_duration)))
    selected = images[:max_images]
    if not selected:
        raise ValueError("No images selected")

    total_transition = transition_duration * (len(selected) - 1)
    available = max(0.1, audio.duration - total_transition)
    duration_per_image = available / len(selected)

    clips = []
    for image in selected:
        clip = (
            ImageClip(str(image))
            .resized(new_size=target_size)
            .with_duration(duration_per_image)
        )
        clips.append(clip)

    transition = ColorClip(size=target_size, color=(0, 0, 0)).with_duration(transition_duration)
    video = concatenate_videoclips(clips, method="chain", transition=transition)
    video = video.with_audio(audio)

    out_path.parent.mkdir(parents=True, exist_ok=True)

    preset = os.getenv("VIDEO_PRESET", "ultrafast")
    bitrate = os.getenv("VIDEO_BITRATE", "2000k")
    threads = int(os.getenv("VIDEO_THREADS", "2"))

    video.write_videofile(
        str(out_path),
        fps=fps,
        codec="libx264",
        audio_codec="aac",
        preset=preset,
        bitrate=bitrate,
        threads=threads,
        ffmpeg_params=["-movflags", "+faststart"],
    )
    video.close()
    audio.close()
