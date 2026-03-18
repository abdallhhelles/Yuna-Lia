from __future__ import annotations

import re
from pathlib import Path

from ..runtime import get_logger
from .models import Script, ScriptStep, TriggerRule


class PersonaContentStore:
    _TRIGGER_SECTION_ACTORS = {
        "# [LIA TRIGGERS]": "Lia",
        "# [YUNA TRIGGERS]": "Yuna",
        "# [SHARED/DUO TRIGGERS]": "shared",
        "[LIA TRIGGERS]": "Lia",
        "[YUNA TRIGGERS]": "Yuna",
        "[SHARED/DUO TRIGGERS]": "shared",
    }

    def __init__(self, root: Path) -> None:
        self.root = root
        self.logger = get_logger("yuna_lia.content")
        self._loaded = False
        self._mtimes: dict[Path, float] = {}
        self.triggers_by_actor: dict[str, list[TriggerRule]] = {"Lia": [], "Yuna": [], "shared": []}
        self.all_rules: tuple[TriggerRule, ...] = ()
        self.trigger_index: dict[str, tuple[TriggerRule, ...]] = {}
        self.tokenless_rules: tuple[TriggerRule, ...] = ()
        self.scripts: dict[str, Script] = {}

    def ensure_loaded(self) -> None:
        if not self._loaded or self._has_changes():
            self.reload()

    def reload(self) -> None:
        self.triggers_by_actor = {"Lia": [], "Yuna": [], "shared": []}
        all_rules: list[TriggerRule] = []
        self.scripts = {}
        seen_triggers: dict[str, str] = {}
        for path in sorted(self._all_files()):
            rules, scripts = self._load_asset(path)
            for rule in rules:
                trigger_owner = seen_triggers.get(rule.trigger)
                if trigger_owner:
                    self.logger.warning(
                        "Duplicate trigger text ignored across content files: %s in %s (already defined in %s)",
                        rule.trigger,
                        path.name,
                        trigger_owner,
                    )
                    continue
                seen_triggers[rule.trigger] = path.name
                self.triggers_by_actor[self._infer_actor(rule.script_id)].append(rule)
                all_rules.append(rule)
            duplicate_ids = sorted(script_id for script_id in scripts if script_id in self.scripts)
            if duplicate_ids:
                self.logger.warning("Duplicate script IDs in %s: %s", path.name, ", ".join(duplicate_ids))
            for script_id, script in scripts.items():
                if script_id in self.scripts:
                    continue
                if not self._script_matches_owner(script):
                    self.logger.warning("Skipped actor-mismatched script %s in %s", script_id, path.name)
                    continue
                self.scripts[script_id] = script
        self.all_rules = tuple(all_rules)
        self.trigger_index, self.tokenless_rules = self._build_trigger_index(self.all_rules)
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

    def _load_asset(self, path: Path) -> tuple[list[TriggerRule], dict[str, Script]]:
        rules: list[TriggerRule] = []
        scripts: dict[str, Script] = {}
        current_id: str | None = None
        current_steps: list[ScriptStep] = []
        current_trigger_section: str | None = None

        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line:
                continue
            if line.startswith("#"):
                current_trigger_section = self._TRIGGER_SECTION_ACTORS.get(line, current_trigger_section)
                if line == "# [SCRIPTS]":
                    current_trigger_section = None
                continue
            if line in self._TRIGGER_SECTION_ACTORS:
                current_trigger_section = self._TRIGGER_SECTION_ACTORS[line]
                continue
            if line == "[SCRIPTS]":
                current_trigger_section = None
                continue

            if line.startswith("==="):
                if current_id and current_steps:
                    scripts[current_id] = Script(current_id, tuple(current_steps))
                current_id = line.removeprefix("===").strip()
                current_steps = []
                continue

            if self._is_script_separator(line):
                if current_id and current_steps:
                    scripts[current_id] = Script(current_id, tuple(current_steps))
                current_id = None
                current_steps = []
                continue

            if current_id is not None:
                if ":" not in line:
                    continue
                actor, message = line.split(":", 1)
                current_steps.append(ScriptStep(actor=self._normalize_actor(actor), message=message.strip()))
                continue

            parts = [part.strip() for part in line.split("||")]
            if len(parts) == 6:
                trigger, script_id, weight, cooldown, attention_cost, mood_shift = parts
                expected_actor = current_trigger_section
                actual_actor = self._infer_actor(script_id)
                if expected_actor is None:
                    self.logger.warning("Skipped trigger outside actor section in %s: %s", path.name, trigger)
                    continue
                if expected_actor == "shared" and actual_actor != "shared":
                    self.logger.warning(
                        "Skipped trigger with mismatched actor in %s: %s -> %s should be shared",
                        path.name,
                        trigger,
                        script_id,
                    )
                    continue
                if expected_actor in {"Lia", "Yuna"} and actual_actor != expected_actor:
                    self.logger.warning(
                        "Skipped trigger with mismatched actor in %s: %s -> %s should belong to %s",
                        path.name,
                        trigger,
                        script_id,
                        expected_actor,
                    )
                    continue
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

    @staticmethod
    def _build_trigger_index(rules: tuple[TriggerRule, ...]) -> tuple[dict[str, tuple[TriggerRule, ...]], tuple[TriggerRule, ...]]:
        indexed: dict[str, list[TriggerRule]] = {}
        tokenless: list[TriggerRule] = []
        for rule in rules:
            tokens = PersonaContentStore._trigger_tokens(rule.trigger)
            if not tokens:
                tokenless.append(rule)
                continue
            for token in tokens:
                indexed.setdefault(token, []).append(rule)
        return (
            {token: tuple(entries) for token, entries in indexed.items()},
            tuple(tokenless),
        )

    @staticmethod
    def _trigger_tokens(text: str) -> tuple[str, ...]:
        return tuple(dict.fromkeys(re.findall(r"[a-z0-9']+", text.lower())))

    @staticmethod
    def _script_matches_owner(script: Script) -> bool:
        actor = PersonaContentStore._infer_actor(script.script_id)
        if actor == "shared":
            return True
        return all(step.actor == actor for step in script.steps)

    @staticmethod
    def _is_script_separator(line: str) -> bool:
        return line == "---" or (set(line) == {"-"} and len(line) >= 3)

    @staticmethod
    def _normalize_actor(actor: str) -> str:
        lowered = actor.strip().lower()
        if lowered == "lia":
            return "Lia"
        if lowered == "yuna":
            return "Yuna"
        return actor.strip()
