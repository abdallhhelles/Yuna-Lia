from pathlib import Path

from yuna_lia.config import load_config


def test_load_config_boolean_parsing(monkeypatch):
    monkeypatch.setenv("DISCORD_TOKEN_YUNA", "token-y")
    monkeypatch.setenv("DISCORD_TOKEN_LIA", "token-l")
    monkeypatch.setenv("ENABLE_MESSAGE_CONTENT", "true")
    monkeypatch.setenv("DEBUG_PERSONA", "0")
    monkeypatch.setenv("PERSONA_TEST_MODE", "no")

    config = load_config()

    assert config.enable_message_content is True
    assert config.debug_persona is False
    assert config.persona_test_mode is False


def test_load_config_parses_role_rewards_and_log_level(monkeypatch):
    monkeypatch.setenv("DISCORD_TOKEN_YUNA", "token-y")
    monkeypatch.setenv("DISCORD_TOKEN_LIA", "token-l")
    monkeypatch.setenv("LEVEL_ROLE_REWARDS", "5:Regular,10: Insomniac,broken,0:nope")
    monkeypatch.setenv("LOG_LEVEL", "warning")

    config = load_config()

    assert config.level_role_rewards == {5: "Regular", 10: "Insomniac"}
    assert config.log_level == "WARNING"


def test_load_config_resolves_custom_paths(monkeypatch, tmp_path: Path):
    content_dir = tmp_path / "content"
    data_dir = tmp_path / "data"
    content_dir.mkdir()
    monkeypatch.setenv("DISCORD_TOKEN_YUNA", "token-y")
    monkeypatch.setenv("DISCORD_TOKEN_LIA", "token-l")
    monkeypatch.setenv("PERSONA_CONTENT_DIR", str(content_dir))
    monkeypatch.setenv("PERSONA_DATA_DIR", str(data_dir))

    config = load_config()

    assert config.content_dir == content_dir.resolve()
    assert config.data_dir == data_dir.resolve()
    assert data_dir.exists()
