from __future__ import annotations

import json
import re
from typing import Any

from groq import Groq
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


def _build_prompt(topic: str, duration_sec: int, language: str) -> str:
    return f"""
You are a YouTube scriptwriter and director.
Create a complete short video plan.
Return ONLY valid JSON with this schema:
{{
  \"title\": string,
  \"description\": string,
  \"tags\": [string, ...],
  \"scenes\": [
    {{\"narration\": string, \"image_prompt\": string}}
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


def _extract_groq_text(response) -> str:
    return response.choices[0].message.content.strip()


def _generate_storyboard_groq(
    cfg: Config,
    topic: str,
    duration_sec: int,
    language: str,
) -> dict[str, Any]:
    if not cfg.groq_api_key:
        raise ValueError("GROQ_API_KEY is missing.")

    client = Groq(api_key=cfg.groq_api_key)
    prompt = _build_prompt(topic, duration_sec, language)
    response = client.chat.completions.create(
        model=cfg.groq_text_model,
        messages=[{"role": "user", "content": prompt}],
    )
    data = _extract_json(_extract_groq_text(response))
    if "scenes" not in data or not isinstance(data["scenes"], list):
        raise ValueError("Invalid storyboard JSON: missing scenes list")
    return data


def _generate_storyboard_openai(
    cfg: Config,
    topic: str,
    duration_sec: int,
    language: str,
) -> dict[str, Any]:
    if not cfg.openai_api_key:
        raise ValueError("OPENAI_API_KEY is missing.")

    client = OpenAI(api_key=cfg.openai_api_key)
    prompt = _build_prompt(topic, duration_sec, language)

    response = client.responses.create(
        model=cfg.openai_text_model,
        input=prompt,
    )

    data = _extract_json(response.output_text)
    if "scenes" not in data or not isinstance(data["scenes"], list):
        raise ValueError("Invalid storyboard JSON: missing scenes list")
    return data


def generate_storyboard(
    cfg: Config,
    topic: str,
    duration_sec: int,
    language: str,
) -> dict[str, Any]:
    if cfg.groq_api_key:
        return _generate_storyboard_groq(cfg, topic, duration_sec, language)
    return _generate_storyboard_openai(cfg, topic, duration_sec, language)


def generate_topic(cfg: Config, themes: str, language: str) -> str:
    if not cfg.groq_api_key:
        raise ValueError("GROQ_API_KEY is missing for topic generation.")

    client = Groq(api_key=cfg.groq_api_key)
    prompt = (
        "Generate ONE unique YouTube video topic title.\n"
        f"Themes (pick one or blend): {themes}\n"
        f"Language: {language}\n"
        "Rules:\n"
        "- Return a single line title only.\n"
        "- No quotes, no markdown, no bullet points.\n"
        "- Make it specific and engaging.\n"
    )
    response = client.chat.completions.create(
        model=cfg.groq_text_model,
        messages=[{"role": "user", "content": prompt}],
    )
    return _extract_groq_text(response).strip()
