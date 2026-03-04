from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class BotIdentity:
    name: str
    mention: str


@dataclass(frozen=True)
class AppConfig:
    discord_token: str
    ollama_url: str
    ollama_model: str
    premium_trigger_file: Path
    base_dir: Path
    db_path: Path


YUNA = BotIdentity(name="Yuna", mention="@Yuna")
LIA = BotIdentity(name="Lia", mention="@Lia")


def load_config() -> AppConfig:
    base_dir = Path(os.getenv("YUNA_LIA_BASE_DIR", Path(__file__).resolve().parent))
    return AppConfig(
        discord_token=os.getenv("DISCORD_BOT_TOKEN", ""),
        ollama_url=os.getenv("OLLAMA_URL", "http://localhost:11434"),
        ollama_model=os.getenv("OLLAMA_MODEL", "llama3.2:3b"),
        premium_trigger_file=Path(
            os.getenv(
                "PREMIUM_TRIGGER_FILE",
                str(base_dir / "scenarios" / "premium" / "premium_triggers.txt"),
            )
        ),
        base_dir=base_dir,
        db_path=Path(os.getenv("BOT_DB_PATH", str(Path("data") / "bot_data.sqlite3"))),
    )
