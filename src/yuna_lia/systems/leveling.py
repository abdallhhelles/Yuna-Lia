from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import datetime, timedelta


XP_COOLDOWN_SECONDS = 90
XP_GAIN_MIN = 8
XP_GAIN_MAX = 14


def xp_for_level(level: int) -> int:
    if level <= 0:
        return 0
    return (level ** 3) * 180 + (level ** 2) * 420 + level * 900


def level_for_xp(xp: int) -> int:
    level = 0
    while xp_for_level(level + 1) <= xp:
        level += 1
    return level


def xp_progress(xp: int) -> tuple[int, int, int]:
    level = level_for_xp(xp)
    current_floor = xp_for_level(level)
    next_floor = xp_for_level(level + 1)
    return level, xp - current_floor, next_floor - current_floor


def should_award_xp(now: datetime, last_awarded_at: datetime | None) -> bool:
    if last_awarded_at is None:
        return True
    return now - last_awarded_at >= timedelta(seconds=XP_COOLDOWN_SECONDS)


def roll_xp() -> int:
    return random.randint(XP_GAIN_MIN, XP_GAIN_MAX)


@dataclass(frozen=True)
class LevelResult:
    awarded_xp: int
    old_level: int
    new_level: int
