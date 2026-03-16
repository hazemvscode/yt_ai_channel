from __future__ import annotations

import json
import random
from dataclasses import dataclass
from datetime import datetime, time
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


@dataclass
class ScheduleConfig:
    timezone: str
    window_start: time
    window_end: time
    daily_target: int
    min_gap_minutes: int
    state_path: Path


def _time_to_minutes(t: time) -> int:
    return t.hour * 60 + t.minute


def _minutes_to_hhmm(m: int) -> str:
    return f"{m // 60:02d}:{m % 60:02d}"


def _load_state(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _save_state(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _generate_times(cfg: ScheduleConfig, date_str: str) -> list[str]:
    start = _time_to_minutes(cfg.window_start)
    end = _time_to_minutes(cfg.window_end)
    if end <= start:
        end = start + 1

    window = end - start
    required = cfg.min_gap_minutes * max(0, cfg.daily_target - 1)
    if cfg.min_gap_minutes > 0 and required <= window:
        times = [start + i * cfg.min_gap_minutes for i in range(cfg.daily_target)]
        return [_minutes_to_hhmm(m) for m in times]

    times: list[int] = []
    attempts = 0
    rng = random.Random(date_str)

    while len(times) < cfg.daily_target and attempts < 5000:
        attempts += 1
        m = rng.randint(start, end - 1)
        if all(abs(m - t) >= cfg.min_gap_minutes for t in times):
            times.append(m)

    if len(times) < cfg.daily_target:
        step = max(cfg.min_gap_minutes, (end - start) // max(1, cfg.daily_target))
        times = [start + i * step for i in range(cfg.daily_target)]

    times.sort()
    return [_minutes_to_hhmm(m) for m in times]


def _ensure_state(cfg: ScheduleConfig) -> dict:
    try:
        tz = ZoneInfo(cfg.timezone)
    except ZoneInfoNotFoundError:
        tz = ZoneInfo("UTC")

    now = datetime.now(tz)
    date_str = now.strftime("%Y-%m-%d")

    state = _load_state(cfg.state_path)
    if state.get("date") != date_str:
        times = _generate_times(cfg, date_str)
        state = {"date": date_str, "times": times, "executed": []}
        _save_state(cfg.state_path, state)

    return state


def should_run(cfg: ScheduleConfig) -> bool:
    try:
        tz = ZoneInfo(cfg.timezone)
    except ZoneInfoNotFoundError:
        tz = ZoneInfo("UTC")

    now = datetime.now(tz)
    state = _ensure_state(cfg)

    now_hhmm = now.strftime("%H:%M")
    pending = [t for t in state["times"] if t <= now_hhmm and t not in state["executed"]]
    if not pending:
        return False

    state["executed"].append(pending[-1])
    _save_state(cfg.state_path, state)
    return True


def get_next_run_time(cfg: ScheduleConfig) -> str | None:
    try:
        tz = ZoneInfo(cfg.timezone)
    except ZoneInfoNotFoundError:
        tz = ZoneInfo("UTC")

    now = datetime.now(tz)
    state = _ensure_state(cfg)

    now_hhmm = now.strftime("%H:%M")
    remaining = [t for t in state["times"] if t > now_hhmm and t not in state["executed"]]
    if remaining:
        return f"{state['date']} {remaining[0]} ({cfg.timezone})"

    return None
