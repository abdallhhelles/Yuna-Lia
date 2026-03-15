from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pytest

from yuna_lia.birthdays import BirthdayStore
from yuna_lia.app_runtime import DualPersonaRuntime
from yuna_lia.config import AppConfig, PersonaConfig
from yuna_lia.personas.content import PersonaContentStore
from yuna_lia.personas.models import UserMemory


def _config(tmp_path: Path) -> AppConfig:
    return AppConfig(
        yuna=PersonaConfig(name="Yuna", token="y", mention_aliases=("@yuna", "yuna")),
        lia=PersonaConfig(name="Lia", token="l", mention_aliases=("@lia", "lia")),
        enable_message_content=True,
        debug_persona=False,
        persona_test_mode=True,
        log_level="DEBUG",
        level_role_rewards={},
        content_dir=Path("content/personas"),
        data_dir=tmp_path,
    )


def test_birthday_store_updates_hidden_calendar(tmp_path: Path) -> None:
    store = BirthdayStore(tmp_path / "bot_data.sqlite3")

    record = store.set_birthday(user_id="42", display_name="Ameer", birthday=date(2001, 9, 14))
    hidden = store.hidden_calendar_entry("42")

    assert record.birthday == date(2001, 9, 14)
    assert hidden is not None
    assert hidden["event_key"] == "birthday:42"
    assert hidden["hidden"] == 1
    assert hidden["month"] == 9
    assert hidden["day"] == 14
    assert hidden["occurs_on"] == record.next_occurrence.isoformat()


def test_runtime_rejects_future_birthday(tmp_path: Path) -> None:
    runtime = DualPersonaRuntime(_config(tmp_path))
    tomorrow = (date.today() + timedelta(days=1)).isoformat()

    with pytest.raises(ValueError, match="future"):
        runtime.parse_birthday(tomorrow)


def test_runtime_accepts_iso_birthday(tmp_path: Path) -> None:
    runtime = DualPersonaRuntime(_config(tmp_path))

    assert runtime.parse_birthday("2000-02-29") == date(2000, 2, 29)


def test_birthday_content_has_50_variants() -> None:
    store = PersonaContentStore(Path("content/personas"))
    store.reload()

    birthday_scripts = [script_id for script_id in store.scripts if script_id.startswith("birthday_duo_")]
    assert len(birthday_scripts) == 50


def test_birthday_wish_tracking_is_once_per_day(tmp_path: Path) -> None:
    store = BirthdayStore(tmp_path / "bot_data.sqlite3")
    store.set_birthday(user_id="9", display_name="Noor", birthday=date(2000, 3, 12))

    assert store.has_sent_birthday_wish("9") is False
    store.record_birthday_wish(user_id="9", script_id="birthday_duo_01")
    assert store.has_sent_birthday_wish("9") is True


def test_daily_question_content_exists(tmp_path: Path) -> None:
    runtime = DualPersonaRuntime(_config(tmp_path))
    runtime.content.reload()

    script_id = runtime._daily_question_script_id()
    assert script_id is not None
    assert script_id.startswith("daily_question_")


def test_daily_question_prompt_extraction(tmp_path: Path) -> None:
    runtime = DualPersonaRuntime(_config(tmp_path))
    runtime.content.reload()

    script_id = runtime._daily_question_script_id()
    assert script_id is not None
    prompt = runtime._daily_question_prompt(script_id)
    assert prompt
    assert "daily question" not in prompt.lower()


def test_daily_answer_is_stored_privately(tmp_path: Path) -> None:
    runtime = DualPersonaRuntime(_config(tmp_path))
    runtime.content.reload()
    script_id = runtime._daily_question_script_id()
    assert script_id is not None
    runtime._record_daily_question_state(77, script_id, 123)
    runtime.memory.record_daily_answer(
        guild_id=77,
        user_id="1",
        user_name="Ameer",
        answer_date=runtime._current_daily_question_date(77),
        script_id=script_id,
        prompt=runtime._daily_question_prompt(script_id),
        answer="pineapple is elite",
        answered_at=datetime.now(timezone.utc).isoformat(),
    )

    assert runtime.memory.daily_answer_count(77, runtime._current_daily_question_date(77)) == 1


def test_current_daily_question_requires_posted_state(tmp_path: Path) -> None:
    runtime = DualPersonaRuntime(_config(tmp_path))
    runtime.content.reload()

    assert runtime._current_daily_question_script_id(77) is None
    assert runtime._current_daily_question_date(77) == ""


def test_daily_question_state_is_guild_scoped(tmp_path: Path) -> None:
    runtime = DualPersonaRuntime(_config(tmp_path))
    runtime.content.reload()

    script_id = runtime._daily_question_script_id()
    assert script_id is not None
    runtime._record_daily_question_state(77, script_id, 123)

    assert runtime._current_daily_question_script_id(77) == script_id
    assert runtime._current_daily_question_channel_id(77) == 123
    assert runtime._current_daily_question_script_id(88) is None
    assert runtime._current_daily_question_channel_id(88) is None


def test_ambient_schedule_stays_within_six_hours(tmp_path: Path) -> None:
    runtime = DualPersonaRuntime(_config(tmp_path))
    before = datetime.now(timezone.utc)
    scheduled = runtime._schedule_next_ambient()
    after = datetime.now(timezone.utc)
    stored = datetime.fromisoformat(runtime.memory.get_runtime_value("next_ambient_at"))
    window_start = datetime.fromisoformat(runtime.memory.get_runtime_value("next_ambient_window_start"))

    assert stored == scheduled
    assert 0 < (scheduled - before).total_seconds() <= 6 * 60 * 60
    assert (scheduled - after).total_seconds() <= 6 * 60 * 60
    assert window_start <= scheduled <= window_start + timedelta(hours=6)


def test_achievements_are_derived_from_user_memory(tmp_path: Path) -> None:
    runtime = DualPersonaRuntime(_config(tmp_path))
    memory = UserMemory(
        name="Mina",
        dramatic_messages=7,
        late_night_messages=6,
        food_messages=5,
        lia_trust=15,
        yuna_trust=8,
        lia_flirt_tension=9,
    )

    achievements = runtime._achievements_for(memory)
    assert "Most Dramatic User" in achievements
    assert "Night Owl" in achievements
    assert "Food War Starter" in achievements
    assert "Lia Favorite" in achievements
