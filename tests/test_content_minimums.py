from pathlib import Path


SPECIAL_SCRIPT_ONLY = {"birthdays", "daily_questions", "social_events", "welcomes"}
THEMES_ROOT = Path("content/personas/themes")
MINIMUM = 50


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


def test_theme_files_meet_minimum_content_floor() -> None:
    for path in sorted(THEMES_ROOT.glob("*.txt")):
        triggers, scripts = _count_theme(path)
        assert scripts >= MINIMUM, f"{path} should have at least {MINIMUM} scripts"
        if path.stem not in SPECIAL_SCRIPT_ONLY:
            assert triggers >= MINIMUM, f"{path} should have at least {MINIMUM} triggers"
