from pathlib import Path
from unittest.mock import patch

from yuna_lia.personas.content import PersonaContentStore
from yuna_lia.personas.engine import PersonaSimulationEngine
from yuna_lia.personas.memory import MemoryStore


def _fixture_content_root(tmp_path: Path) -> Path:
    root = tmp_path / "content"
    root.mkdir()
    (root / "fixture.txt").write_text(
        "\n".join(
            [
                "# fixture content for engine tests",
                "# [TRIGGERS]",
                "# [LIA TRIGGERS]",
                "drama || lia_test_drama_01 || 1.00 || 300 || medium || irritated+",
                "cute || lia_test_cute_01 || 1.00 || 300 || low || flirty+",
                "# [YUNA TRIGGERS]",
                "# none",
                "# [SHARED/DUO TRIGGERS]",
                "pizza || duo_test_pizza_01 || 1.00 || 300 || medium || playful+",
                "# [SCRIPTS]",
                "=== lia_test_drama_01",
                "Lia: drama again. of course it is.",
                "---",
                "=== lia_test_cute_01",
                "Lia: cute is never a harmless word in here.",
                "---",
                "=== duo_test_pizza_01",
                "Lia: pineapple belongs on pizza and i will defend that with style.",
                "Yuna: terrible judgment. useful trigger.",
                "---",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return root


def _engine(tmp_path: Path) -> PersonaSimulationEngine:
    content = PersonaContentStore(_fixture_content_root(tmp_path))
    content.reload()
    memory = MemoryStore(tmp_path / "persona_state.json")
    return PersonaSimulationEngine(content, memory, tmp_path / "script_log.jsonl")


def test_triggered_message_returns_duo_script(tmp_path: Path) -> None:
    engine = _engine(tmp_path)

    with patch("yuna_lia.personas.engine.random.choice", side_effect=lambda seq: seq[0]), patch(
        "yuna_lia.personas.engine.random.uniform", return_value=0.0
    ), patch("yuna_lia.personas.engine.random.random", return_value=0.0):
        events = engine.handle_message(
            user_id="1",
            display_name="Ameer",
            guild_id=100,
            channel_id=200,
            content="pizza is the only thing that matters",
        )

    assert len(events) >= 2
    assert events[0].actor in {"Lia", "Yuna"}
    assert any("pineapple" in event.message for event in events)


def test_engine_tracks_user_memory(tmp_path: Path) -> None:
    engine = _engine(tmp_path)
    with patch("yuna_lia.personas.engine.random.choice", side_effect=lambda seq: seq[0]), patch(
        "yuna_lia.personas.engine.random.uniform", return_value=0.0
    ), patch("yuna_lia.personas.engine.random.random", return_value=0.0):
        engine.handle_message(
            user_id="2",
            display_name="Mina",
            guild_id=100,
            channel_id=200,
            content="drama again",
        )

    memory = engine.inspect_user("2", "Mina")
    assert "drama" in memory.favorite_topics


def test_engine_tracks_human_style_signals(tmp_path: Path) -> None:
    engine = _engine(tmp_path)
    with patch("yuna_lia.personas.engine.random.choice", side_effect=lambda seq: seq[0]), patch(
        "yuna_lia.personas.engine.random.uniform", return_value=0.0
    ), patch("yuna_lia.personas.engine.random.random", return_value=0.0):
        engine.handle_message(
            user_id="20",
            display_name="Rin",
            guild_id=100,
            channel_id=200,
            content="lia i'm tired ngl, rough day. love you guys tho?",
        )

    memory = engine.inspect_user("20", "Rin")
    assert memory.direct_lia_mentions == 1
    assert memory.question_messages == 1
    assert memory.slang_messages == 1
    assert memory.vulnerability_messages == 1
    assert memory.affection_messages == 1


def test_trigger_matching_uses_word_boundaries(tmp_path: Path) -> None:
    engine = _engine(tmp_path)
    with patch("yuna_lia.personas.engine.random.choice", side_effect=lambda seq: seq[0]), patch(
        "yuna_lia.personas.engine.random.uniform", return_value=0.0
    ), patch("yuna_lia.personas.engine.random.random", return_value=0.0):
        events = engine.handle_message(
            user_id="3",
            display_name="Noor",
            guild_id=100,
            channel_id=200,
            content="pizzazz is not pizza",
        )

    assert events

    with patch("yuna_lia.personas.engine.random.choice", side_effect=lambda seq: seq[0]), patch(
        "yuna_lia.personas.engine.random.uniform", return_value=0.0
    ), patch("yuna_lia.personas.engine.random.random", return_value=0.0):
        no_events = engine.handle_message(
            user_id="4",
            display_name="Noor",
            guild_id=100,
            channel_id=201,
            content="pizzazz only",
        )

    assert no_events == []


def test_selected_script_updates_actor_mood_from_trigger(tmp_path: Path) -> None:
    engine = _engine(tmp_path)
    with patch("yuna_lia.personas.engine.random.choice", side_effect=lambda seq: seq[0]), patch(
        "yuna_lia.personas.engine.random.uniform", return_value=0.0
    ), patch("yuna_lia.personas.engine.random.random", return_value=0.0):
        engine.handle_message(
            user_id="5",
            display_name="Sami",
            guild_id=100,
            channel_id=200,
            content="cute",
        )

    lia_state = engine.memory.get_persona_state("Lia")
    assert lia_state.mood == "flirty"


def test_trigger_cooldown_is_per_user_and_5_minutes(tmp_path: Path) -> None:
    engine = _engine(tmp_path)

    with patch("yuna_lia.personas.engine.random.choice", side_effect=lambda seq: seq[0]), patch(
        "yuna_lia.personas.engine.random.uniform", return_value=0.0
    ), patch("yuna_lia.personas.engine.random.random", return_value=0.0):
        first = engine.handle_message(
            user_id="10",
            display_name="A",
            guild_id=100,
            channel_id=200,
            content="drama",
        )
        second = engine.handle_message(
            user_id="10",
            display_name="A",
            guild_id=100,
            channel_id=200,
            content="drama",
        )
        third = engine.handle_message(
            user_id="11",
            display_name="B",
            guild_id=100,
            channel_id=200,
            content="drama",
        )

    assert first
    assert second == []
    assert third


def test_engine_tracks_channel_activity_details(tmp_path: Path) -> None:
    engine = _engine(tmp_path)

    with patch("yuna_lia.personas.engine.random.choice", side_effect=lambda seq: seq[0]), patch(
        "yuna_lia.personas.engine.random.uniform", return_value=0.0
    ), patch("yuna_lia.personas.engine.random.random", return_value=0.0):
        engine.handle_message(
            user_id="12",
            display_name="Kai",
            guild_id=500,
            channel_id=900,
            content="pizza and drama",
        )

    channel = engine.memory.get_channel(900, 500)
    assert channel.user_message_count == 1
    assert channel.bot_message_count == 1
    assert channel.last_script_id
