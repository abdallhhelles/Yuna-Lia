from pathlib import Path

from yuna_lia.mood import MoodState, mood_label, update_mood_from_message
from yuna_lia.premium import load_premium_triggers
from yuna_lia.scenarios import ScenarioLibrary
from yuna_lia.typing_sim import typing_time_seconds


def test_mood_update_and_label() -> None:
    mood = MoodState()
    updated = update_mood_from_message(mood, "lol prank time")
    assert updated.playfulness >= 0.5
    assert mood_label(updated) in {"playful", "neutral", "dominant", "heated"}


def test_typing_sim_positive() -> None:
    t = typing_time_seconds("Yuna", "hello world from bot", MoodState())
    assert t > 0


def test_scenario_load_and_choose() -> None:
    lib = ScenarioLibrary(Path("src/yuna_lia/scenarios/free/scenarios.json"))
    lib.load()
    sc = lib.choose(bot="Yuna", mood="playful", trigger="prank", premium_enabled=False)
    assert sc is not None
    assert sc.bot == "Yuna"


def test_premium_parser() -> None:
    triggers = load_premium_triggers(Path("src/yuna_lia/scenarios/premium/premium_triggers.txt"))
    assert len(triggers) == 1
    assert triggers[0].scenario_id == 3012
