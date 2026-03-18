from pathlib import Path

from yuna_lia.personas.content import PersonaContentStore
from yuna_lia.systems.leveling import level_for_xp, should_award_xp, xp_for_level, xp_progress


def test_level_curve_is_slow() -> None:
    assert xp_for_level(1) >= 1000
    assert xp_for_level(5) > 20000
    assert level_for_xp(xp_for_level(3)) == 3


def test_xp_progress_reports_current_band() -> None:
    level, current_xp, needed_xp = xp_progress(xp_for_level(2) + 50)
    assert level == 2
    assert current_xp == 50
    assert needed_xp > current_xp


def test_welcome_content_scaffold_exists() -> None:
    store = PersonaContentStore(Path("content/personas/themes"))
    store.reload()

    welcome_scripts = [script_id for script_id in store.scripts if script_id.startswith("welcome_")]
    assert welcome_scripts == []
    assert Path("content/personas/themes/welcomes.txt").exists()


def test_level_award_cooldown_is_long_enough() -> None:
    from datetime import datetime, timedelta, timezone

    now = datetime.now(timezone.utc)
    assert should_award_xp(now, None) is True
    assert should_award_xp(now, now - timedelta(seconds=30)) is False
    assert should_award_xp(now, now - timedelta(seconds=120)) is True
