from __future__ import annotations

from pathlib import Path

from ..runtime import get_logger
from .models import Script, ScriptStep, TriggerRule


class PersonaContentStore:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.logger = get_logger("yuna_lia.content")
        self._loaded = False
        self._mtimes: dict[Path, float] = {}
        self.triggers_by_actor: dict[str, list[TriggerRule]] = {"Lia": [], "Yuna": [], "shared": []}
        self.scripts: dict[str, Script] = {}

    def ensure_loaded(self) -> None:
        if not self._loaded or self._has_changes():
            self.reload()

    def reload(self) -> None:
        self.triggers_by_actor = {"Lia": [], "Yuna": [], "shared": []}
        self.scripts = {}
        for path in sorted(self._all_files()):
            rules, scripts = self._load_asset(path)
            for rule in rules:
                self.triggers_by_actor[self._infer_actor(rule.script_id)].append(rule)
            duplicate_ids = sorted(script_id for script_id in scripts if script_id in self.scripts)
            if duplicate_ids:
                self.logger.warning("Duplicate script IDs in %s: %s", path.name, ", ".join(duplicate_ids))
            self.scripts.update(scripts)
        self._mtimes = {path: path.stat().st_mtime for path in self._all_files()}
        self._loaded = True

    def _has_changes(self) -> bool:
        current = {path: path.stat().st_mtime for path in self._all_files()}
        return current != self._mtimes

    def _all_files(self) -> list[Path]:
        return [path for path in self.root.rglob("*.txt") if path.is_file()]

    @staticmethod
    def _infer_actor(script_id: str) -> str:
        lowered = script_id.lower()
        if lowered.startswith("lia_"):
            return "Lia"
        if lowered.startswith("yuna_"):
            return "Yuna"
        return "shared"

    @staticmethod
    def _load_asset(path: Path) -> tuple[list[TriggerRule], dict[str, Script]]:
        rules: list[TriggerRule] = []
        scripts: dict[str, Script] = {}
        current_id: str | None = None
        current_steps: list[ScriptStep] = []

        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue

            if line.startswith("==="):
                if current_id and current_steps:
                    scripts[current_id] = Script(current_id, tuple(current_steps))
                current_id = line.removeprefix("===").strip()
                current_steps = []
                continue

            if line == "---":
                if current_id and current_steps:
                    scripts[current_id] = Script(current_id, tuple(current_steps))
                current_id = None
                current_steps = []
                continue

            if current_id is not None:
                if ":" not in line:
                    continue
                actor, message = line.split(":", 1)
                current_steps.append(ScriptStep(actor=actor.strip(), message=message.strip()))
                continue

            parts = [part.strip() for part in line.split("||")]
            if len(parts) == 6:
                trigger, script_id, weight, cooldown, attention_cost, mood_shift = parts
                rules.append(
                    TriggerRule(
                        source_file=str(path.name),
                        trigger=trigger.lower(),
                        script_id=script_id,
                        weight=float(weight),
                        cooldown_seconds=int(cooldown),
                        attention_cost=attention_cost,
                        mood_shift=mood_shift,
                    )
                )
        if current_id and current_steps:
            scripts[current_id] = Script(current_id, tuple(current_steps))
        return rules, scripts
