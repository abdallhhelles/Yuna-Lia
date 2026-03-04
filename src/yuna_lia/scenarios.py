from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Scenario:
    scenario_id: int
    bot: str
    mood: str
    trigger: str
    text: str
    premium: bool


class ScenarioLibrary:
    def __init__(self, scenario_file: Path) -> None:
        self.scenario_file = scenario_file
        self._scenarios: list[Scenario] = []

    def load(self) -> None:
        raw = json.loads(self.scenario_file.read_text(encoding="utf-8"))
        self._scenarios = [Scenario(**item) for item in raw["scenarios"]]

    def choose(self, bot: str, mood: str, trigger: str, premium_enabled: bool) -> Scenario | None:
        pool = [
            sc
            for sc in self._scenarios
            if sc.bot == bot and sc.trigger == trigger and (premium_enabled or not sc.premium)
        ]
        if not pool:
            pool = [sc for sc in self._scenarios if sc.bot == bot and (premium_enabled or not sc.premium)]
        if not pool:
            return None

        weighted = []
        for sc in pool:
            weight = 3 if sc.mood == mood else 1
            weighted.extend([sc] * weight)
        return random.choice(weighted)
