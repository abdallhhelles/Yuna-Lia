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
        enable_message_content=os.getenv("ENABLE_MESSAGE_CONTENT", "1").strip().lower() in {"1", "true", "yes", "on"},
        debug_persona=os.getenv("DEBUG_PERSONA", "1").strip().lower() in {"1", "true", "yes", "on"},
        persona_test_mode=os.getenv("PERSONA_TEST_MODE", "0").strip().lower() in {"1", "true", "yes", "on"},
        content_dir=content_dir,
        data_dir=data_dir,
        ambient_min_seconds=max(30, int(os.getenv("AMBIENT_MIN_SECONDS", "120"))),
        ambient_max_seconds=max(60, int(os.getenv("AMBIENT_MAX_SECONDS", "300"))),
    )
