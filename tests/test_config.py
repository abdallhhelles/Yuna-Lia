from yuna_lia.config import load_config


def test_load_config_handles_invalid_int_env(monkeypatch):
    monkeypatch.setenv("DISCORD_TOKEN_YUNA", "token-y")
    monkeypatch.setenv("DISCORD_TOKEN_LIA", "token-l")
    monkeypatch.setenv("AMBIENT_MIN_SECONDS", "abc")
    monkeypatch.setenv("AMBIENT_MAX_SECONDS", "xyz")

    config = load_config()

    assert config.ambient_min_seconds == 120
    assert config.ambient_max_seconds == 300


def test_load_config_keeps_ambient_max_at_least_min(monkeypatch):
    monkeypatch.setenv("DISCORD_TOKEN_YUNA", "token-y")
    monkeypatch.setenv("DISCORD_TOKEN_LIA", "token-l")
    monkeypatch.setenv("AMBIENT_MIN_SECONDS", "240")
    monkeypatch.setenv("AMBIENT_MAX_SECONDS", "100")

    config = load_config()

    assert config.ambient_min_seconds == 240
    assert config.ambient_max_seconds == 240


def test_load_config_boolean_defaults(monkeypatch):
    monkeypatch.setenv("DISCORD_TOKEN_YUNA", "token-y")
    monkeypatch.setenv("DISCORD_TOKEN_LIA", "token-l")
    monkeypatch.delenv("ENABLE_MESSAGE_CONTENT", raising=False)
    monkeypatch.delenv("DEBUG_PERSONA", raising=False)
    monkeypatch.delenv("PERSONA_TEST_MODE", raising=False)

    config = load_config()

    assert config.enable_message_content is True
    assert config.debug_persona is True
    assert config.persona_test_mode is False
