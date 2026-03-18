from pathlib import Path


THEMES_ROOT = Path("content/personas/themes")
SCRIPT_ONLY_THEMES = {"daily_questions_bonus.txt", "welcomes.txt"}


def _count_theme(path: Path) -> tuple[int, int]:
    triggers = 0
    scripts = 0
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("==="):
            scripts += 1
            continue
        if len([part.strip() for part in line.split("||")]) == 6:
            triggers += 1
    return triggers, scripts


def _count_triggers_by_actor(path: Path) -> dict[str, int]:
    counts = {"lia": 0, "yuna": 0, "shared": 0}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [part.strip() for part in line.split("||")]
        if len(parts) != 6:
            continue
        script_id = parts[1].lower()
        if script_id.startswith("lia_"):
            counts["lia"] += 1
        elif script_id.startswith("yuna_"):
            counts["yuna"] += 1
        else:
            counts["shared"] += 1
    return counts


def _count_multi_step_scripts(path: Path) -> int:
    current_id: str | None = None
    step_count = 0
    multi_step = 0
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("==="):
            if current_id and step_count >= 2:
                multi_step += 1
            current_id = line.removeprefix("===").strip()
            step_count = 0
            continue
        if line == "---":
            if current_id and step_count >= 2:
                multi_step += 1
            current_id = None
            step_count = 0
            continue
        if current_id is not None and ":" in line:
            step_count += 1
    if current_id and step_count >= 2:
        multi_step += 1
    return multi_step


def test_theme_files_are_scaffolded_for_writers() -> None:
    for path in sorted(THEMES_ROOT.glob("*.txt")):
        text = path.read_text(encoding="utf-8-sig")
        assert "# [TRIGGERS]" in text, f"{path} should keep trigger sections"
        assert "# [SCRIPTS]" in text, f"{path} should keep script sections"
        assert "# Trigger counts:" in text, f"{path} should document trigger counts"
        assert "# Trigger inventory:" in text, f"{path} should document trigger inventory state"
        if path.name not in SCRIPT_ONLY_THEMES:
            assert "# Coverage target: 20 Lia triggers, 20 Yuna triggers, and 20 shared/duo triggers per file." in text
            assert "# Conversation target:" in text
            assert "# Completion rule: a file is considered full when it has 60 triggers and 60 matching scripts." in text
        assert "â" not in text, f"{path} should not contain mojibake"


def test_each_trigger_has_exactly_one_script_and_each_script_is_trigger_owned() -> None:
    for path in sorted(THEMES_ROOT.glob("*.txt")):
        trigger_to_script: dict[str, str] = {}
        script_to_trigger: dict[str, str] = {}
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            parts = [part.strip() for part in line.split("||")]
            if len(parts) != 6:
                continue
            trigger, script_id, *_ = parts
            assert trigger not in trigger_to_script, f"{path} repeats trigger {trigger!r}"
            assert script_id not in script_to_trigger, f"{path} reuses script_id {script_id!r}"
            trigger_to_script[trigger] = script_id
            script_to_trigger[script_id] = trigger


def test_theme_files_are_either_empty_scaffolds_or_full_20_20_20_packs() -> None:
    for path in sorted(THEMES_ROOT.glob("*.txt")):
        if path.name in SCRIPT_ONLY_THEMES:
            continue

        trigger_count, script_count = _count_theme(path)
        actor_counts = _count_triggers_by_actor(path)
        total = actor_counts["lia"] + actor_counts["yuna"] + actor_counts["shared"]

        assert trigger_count == total, f"{path} has mismatched actor counting"
        assert script_count == trigger_count, f"{path} should keep trigger and script totals aligned"

        if trigger_count == 0:
            continue

        assert actor_counts == {"lia": 20, "yuna": 20, "shared": 20}, (
            f"{path} should target 20 Lia, 20 Yuna, and 20 shared triggers"
        )
        assert _count_multi_step_scripts(path) >= 5, f"{path} should include some fuller conversation scenes"
