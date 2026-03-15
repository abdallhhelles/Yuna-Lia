from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _parse_role_rewards() -> dict[int, str]:
    raw = os.getenv("LEVEL_ROLE_REWARDS", "").strip()
    rewards: dict[int, str] = {}
    if not raw:
        return rewards
    for entry in raw.split(","):
        if ":" not in entry:
            continue
        level_raw, role_raw = entry.split(":", 1)
        try:
            level = int(level_raw.strip())
        except ValueError:
            continue
        role = role_raw.strip()
        if level > 0 and role:
            rewards[level] = role
    return dict(sorted(rewards.items()))


def _parse_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _parse_path(name: str, default: Path) -> Path:
    raw = os.getenv(name)
    if raw is None or not raw.strip():
        return default.resolve()
    return Path(raw).expanduser().resolve()


def _parse_log_level() -> str:
    value = os.getenv("LOG_LEVEL", "INFO").strip().upper()
    return value if value in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"} else "INFO"


def _load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


@dataclass(frozen=True)
class PersonaConfig:
    name: str
    token: str
    mention_aliases: tuple[str, ...]


@dataclass(frozen=True)
class AppConfig:
    yuna: PersonaConfig
    lia: PersonaConfig
    enable_message_content: bool
    debug_persona: bool
    persona_test_mode: bool
    log_level: str
    level_role_rewards: dict[int, str]
    content_dir: Path
    data_dir: Path


def load_config() -> AppConfig:
    repo_root = Path(__file__).resolve().parents[2]
    _load_dotenv(repo_root / ".env")
    content_dir = _parse_path("PERSONA_CONTENT_DIR", repo_root / "content" / "personas")
    data_dir = _parse_path("PERSONA_DATA_DIR", repo_root / "data")
    data_dir.mkdir(parents=True, exist_ok=True)
    if not content_dir.exists():
        raise RuntimeError(f"Persona content directory does not exist: {content_dir}")

    return AppConfig(
        yuna=PersonaConfig(
            name="Yuna",
            token=os.getenv("DISCORD_TOKEN_YUNA", ""),
            mention_aliases=("@yuna", "yuna"),
        ),
        lia=PersonaConfig(
            name="Lia",
            token=os.getenv("DISCORD_TOKEN_LIA", ""),
            mention_aliases=("@lia", "lia"),
        ),
        enable_message_content=_parse_bool("ENABLE_MESSAGE_CONTENT", True),
        debug_persona=_parse_bool("DEBUG_PERSONA", False),
        persona_test_mode=_parse_bool("PERSONA_TEST_MODE", False),
        log_level=_parse_log_level(),
        level_role_rewards=_parse_role_rewards(),
        content_dir=content_dir,
        data_dir=data_dir,
    )
