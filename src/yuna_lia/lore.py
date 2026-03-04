from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PersonaLore:
    name: str
    age: int
    heritage: str
    occupation: str
    appearance: list[str]
    personality: list[str]
    hobbies: list[str]
    communication_style: list[str]
    values: list[str]
    pet_peeves: list[str]
    inside_jokes: list[str]
    history_timeline: list[str]


@dataclass(frozen=True)
class SharedLore:
    friendship_origin: str
    recurring_conflicts: list[str]
    memorable_events: list[str]


class LoreStore:
    def __init__(self, meta_dir: Path) -> None:
        self.meta_dir = meta_dir
        self._persona: dict[str, PersonaLore] = {}
        self._shared: SharedLore | None = None

    def load(self) -> None:
        yuna_data = json.loads((self.meta_dir / "yuna_profile.json").read_text(encoding="utf-8"))
        lia_data = json.loads((self.meta_dir / "lia_profile.json").read_text(encoding="utf-8"))
        shared_data = json.loads((self.meta_dir / "shared_history.json").read_text(encoding="utf-8"))

        self._persona["Yuna"] = PersonaLore(**yuna_data)
        self._persona["Lia"] = PersonaLore(**lia_data)
        self._shared = SharedLore(**shared_data)

    def persona(self, name: str) -> PersonaLore:
        return self._persona[name]

    def shared(self) -> SharedLore:
        if self._shared is None:
            raise RuntimeError("Shared lore not loaded")
        return self._shared
