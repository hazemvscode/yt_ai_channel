from __future__ import annotations

import json
import re
from typing import Any

from openai import OpenAI

from .config import Config


def _extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("{") and text.endswith("}"):
        return json.loads(text)

    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        raise ValueError("No JSON object found in model output")
    return json.loads(match.group(0))


def generate_storyboard(
    cfg: Config,
    topic: str,
    duration_sec: int,
    language: str,
) -> dict[str, Any]:
    client = OpenAI(api_key=cfg.openai_api_key)

    prompt = f"""
You are a YouTube scriptwriter and director.
Create a complete short video plan.
Return ONLY valid JSON with this schema:
{{
  "title": string,
  "description": string,
  "tags": [string, ...],
  "scenes": [
    {{"narration": string, "image_prompt": string}}
  ]
}}

Rules:
- Language for title/description/narration/tags: {language}
- image_prompt MUST be in English and describe a single image clearly
- Total length ~ {duration_sec} seconds
- 6 to 12 scenes
- Narration per scene should be brief and timed evenly
- No markdown, no commentary, JSON only

Topic: {topic}
""".strip()

    response = client.responses.create(
        model=cfg.openai_text_model,
        input=prompt,
    )

    data = _extract_json(response.output_text)
    if "scenes" not in data or not isinstance(data["scenes"], list):
        raise ValueError("Invalid storyboard JSON: missing scenes list")
    return data