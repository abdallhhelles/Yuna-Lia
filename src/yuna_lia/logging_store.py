from __future__ import annotations

import sqlite3
from pathlib import Path


SCHEMA = """
CREATE TABLE IF NOT EXISTS messages (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts DATETIME DEFAULT CURRENT_TIMESTAMP,
  channel_id TEXT NOT NULL,
  author TEXT NOT NULL,
  bot TEXT,
  scenario_id INTEGER,
  content TEXT NOT NULL,
  reaction_count INTEGER DEFAULT 0,
  reply_count INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS server_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts DATETIME DEFAULT CURRENT_TIMESTAMP,
  event TEXT NOT NULL,
  server_id TEXT NOT NULL,
  server_name TEXT NOT NULL
);
"""


class LogStore:
    def __init__(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(path)
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def log_message(
        self,
        channel_id: str,
        author: str,
        content: str,
        bot: str | None = None,
        scenario_id: int | None = None,
    ) -> None:
        self.conn.execute(
            """
            INSERT INTO messages(channel_id, author, bot, scenario_id, content)
            VALUES (?, ?, ?, ?, ?)
            """,
            (channel_id, author, bot, scenario_id, content),
        )
        self.conn.commit()

    def log_server_event(self, event: str, server_id: str, server_name: str) -> None:
        self.conn.execute(
            "INSERT INTO server_events(event, server_id, server_name) VALUES (?, ?, ?)",
            (event, server_id, server_name),
        )
        self.conn.commit()
