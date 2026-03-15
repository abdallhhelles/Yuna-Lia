from pathlib import Path

from yuna_lia.personas.content import PersonaContentStore


def test_content_store_loads_scripts_and_triggers() -> None:
    store = PersonaContentStore(Path("content/personas"))
    store.reload()

    assert store.scripts
    assert "duo_food_war_01" in store.scripts
    assert any(rule.trigger == "pizza" for rule in store.triggers_by_actor["shared"])
    assert any(rule.trigger == "drama" for rule in store.triggers_by_actor["Lia"])
    assert Path("content/personas/themes").exists()
