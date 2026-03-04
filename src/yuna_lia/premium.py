from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PremiumTrigger:
    trigger: str
    scenario_id: int
    description: str


def load_premium_triggers(path: Path) -> list[PremiumTrigger]:
    if not path.exists():
        return []

    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    triggers: list[PremiumTrigger] = []

    current: dict[str, str] = {}
    for line in lines:
        key, _, value = line.partition(":")
        current[key.strip().lower()] = value.strip()
        if {"trigger", "scenario_id", "description"}.issubset(current.keys()):
            triggers.append(
                PremiumTrigger(
                    trigger=current["trigger"],
                    scenario_id=int(current["scenario_id"]),
                    description=current["description"],
                )
            )
            current = {}
    return triggers
