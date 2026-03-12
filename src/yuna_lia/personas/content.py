from __future__ import annotations

from pathlib import Path

from .models import Script, ScriptStep, TriggerRule


class PersonaContentStore:
    def __init__(self, root: Path) -> None:
        self.root = root
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
        for actor_key, actor_dir in (
            ("Lia", self.root / "lia"),
            ("Yuna", self.root / "yuna"),
            ("shared", self.root / "shared"),
        ):
            for path in sorted(actor_dir.glob("*.txt")):
                rules, scripts = self._load_asset(path)
                self.triggers_by_actor[actor_key].extend(rules)
                self.scripts.update(scripts)
        self._mtimes = {path: path.stat().st_mtime for path in self._all_files()}
        self._loaded = True

    def _has_changes(self) -> bool:
        current = {path: path.stat().st_mtime for path in self._all_files()}
        return current != self._mtimes

    def _all_files(self) -> list[Path]:
        return [path for path in self.root.rglob("*.txt") if path.is_file()]

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
