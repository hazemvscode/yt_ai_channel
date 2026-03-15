from __future__ import annotations

from pathlib import Path

from moviepy import AudioFileClip, ImageClip, concatenate_videoclips


def build_video(
    images: list[Path],
    audio_path: Path,
    out_path: Path,
    fps: int = 24,
) -> None:
    if not images:
        raise ValueError("No images provided")

    audio = AudioFileClip(str(audio_path))
    duration_per_image = audio.duration / len(images)

    clips = []
    for image in images:
        clip = ImageClip(str(image)).set_duration(duration_per_image)
        clips.append(clip)

    video = concatenate_videoclips(clips, method="compose")
    video = video.set_audio(audio)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    video.write_videofile(str(out_path), fps=fps)