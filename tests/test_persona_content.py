from pathlib import Path

import logging

from yuna_lia.personas.content import PersonaContentStore


def test_content_store_loads_scripts_and_triggers() -> None:
    store = PersonaContentStore(Path("content/personas/themes"))
    store.reload()

    assert Path("content/personas/themes").exists()
    all_rules = (
        store.triggers_by_actor["shared"]
        + store.triggers_by_actor["Lia"]
        + store.triggers_by_actor["Yuna"]
    )
    assert len(all_rules) == len({rule.trigger for rule in all_rules})
    assert all(rule.script_id in store.scripts for rule in all_rules)
    for script in store.scripts.values():
        if script.script_id.startswith("lia_"):
            assert all(step.actor == "Lia" for step in script.steps)
        elif script.script_id.startswith("yuna_"):
            assert all(step.actor == "Yuna" for step in script.steps)


def test_content_store_skips_misowned_and_duplicate_entries(tmp_path, caplog) -> None:
    asset = tmp_path / "mixed.txt"
    asset.write_text(
        "\n".join(
            [
                "# [TRIGGERS]",
                "# [LIA TRIGGERS]",
                "hi lia || lia_greeting_01 || 0.7 || 180 || low || warm+",
                "wrong owner || yuna_greeting_01 || 0.7 || 180 || low || warm+",
                "# [YUNA TRIGGERS]",
                "hi lia || yuna_greeting_02 || 0.7 || 180 || low || warm+",
                "# [SHARED/DUO TRIGGERS]",
                "duo time || duo_scene_01 || 0.7 || 180 || low || warm+",
                "bad shared || lia_scene_99 || 0.7 || 180 || low || warm+",
                "# [SCRIPTS]",
                "=== lia_greeting_01",
                "Lia: hi.",
                "---",
                "=== yuna_greeting_01",
                "Yuna: hello.",
                "---",
                "=== yuna_greeting_02",
                "Yuna: again.",
                "---",
                "=== duo_scene_01",
                "Lia: wow.",
                "Yuna: unfortunately yes.",
                "---",
                "=== lia_scene_99",
                "Yuna: this should not load.",
                "---",
            ]
        ),
        encoding="utf-8",
    )

    store = PersonaContentStore(tmp_path)
    with caplog.at_level(logging.WARNING, logger="yuna_lia.content"):
        store.reload()

    assert [rule.trigger for rule in store.triggers_by_actor["Lia"]] == ["hi lia"]
    assert [rule.trigger for rule in store.triggers_by_actor["shared"]] == ["duo time"]
    assert store.triggers_by_actor["Yuna"] == []
    assert "lia_scene_99" not in store.scripts
    assert "mismatched actor" in caplog.text.lower()
    assert "duplicate trigger text ignored" in caplog.text.lower()
