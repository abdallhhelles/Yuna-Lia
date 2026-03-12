from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


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


def _read_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _read_int(name: str, default: int, minimum: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return max(minimum, default)
    try:
        return max(minimum, int(raw.strip()))
    except ValueError:
        return max(minimum, default)


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
    content_dir: Path
    data_dir: Path
    ambient_min_seconds: int
    ambient_max_seconds: int


def load_config() -> AppConfig:
    repo_root = Path(__file__).resolve().parents[2]
    _load_dotenv(repo_root / ".env")
    content_dir = Path(os.getenv("PERSONA_CONTENT_DIR", repo_root / "content" / "personas"))
    data_dir = Path(os.getenv("PERSONA_DATA_DIR", repo_root / "data"))
    ambient_min_seconds = _read_int("AMBIENT_MIN_SECONDS", default=120, minimum=30)
    ambient_max_seconds = _read_int("AMBIENT_MAX_SECONDS", default=300, minimum=60)
    ambient_max_seconds = max(ambient_min_seconds, ambient_max_seconds)

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
        enable_message_content=_read_bool("ENABLE_MESSAGE_CONTENT", default=True),
        debug_persona=_read_bool("DEBUG_PERSONA", default=True),
        persona_test_mode=_read_bool("PERSONA_TEST_MODE", default=False),
        content_dir=content_dir,
        data_dir=data_dir,
        ambient_min_seconds=ambient_min_seconds,
        ambient_max_seconds=ambient_max_seconds,
    )
