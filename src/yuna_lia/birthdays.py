from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path


def _utc_now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _next_birthday_occurrence(birthday: date, today: date | None = None) -> date:
    today = today or date.today()
    year = today.year

    while True:
        try:
            candidate = birthday.replace(year=year)
        except ValueError:
            candidate = date(year, 2, 28)
        if candidate >= today:
            return candidate
        year += 1


@dataclass(frozen=True)
class BirthdayRecord:
    user_id: str
    display_name: str
    birthday: date
    next_occurrence: date
    created_at: str
    updated_at: str


class BirthdayStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS birthdays (
                    user_id TEXT PRIMARY KEY,
                    display_name TEXT NOT NULL,
                    birthday_iso TEXT NOT NULL,
                    month INTEGER NOT NULL,
                    day INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS hidden_calendar (
                    event_key TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    label TEXT NOT NULL,
                    hidden INTEGER NOT NULL DEFAULT 1,
                    occurs_on TEXT NOT NULL,
                    month INTEGER NOT NULL,
                    day INTEGER NOT NULL,
                    source TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS birthday_wishes (
                    user_id TEXT NOT NULL,
                    wish_date TEXT NOT NULL,
                    script_id TEXT NOT NULL,
                    wished_at TEXT NOT NULL,
                    PRIMARY KEY (user_id, wish_date)
                )
                """
            )

    def set_birthday(self, *, user_id: str, display_name: str, birthday: date) -> BirthdayRecord:
        now = _utc_now_iso()
        next_occurrence = _next_birthday_occurrence(birthday)
        existing = self.get_birthday(user_id)
        created_at = existing.created_at if existing is not None else now

        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO birthdays (
                    user_id, display_name, birthday_iso, month, day, year, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    display_name=excluded.display_name,
                    birthday_iso=excluded.birthday_iso,
                    month=excluded.month,
                    day=excluded.day,
                    year=excluded.year,
                    updated_at=excluded.updated_at
                """,
                (
                    user_id,
                    display_name,
                    birthday.isoformat(),
                    birthday.month,
                    birthday.day,
                    birthday.year,
                    created_at,
                    now,
                ),
            )
            connection.execute(
                """
                INSERT INTO hidden_calendar (
                    event_key, user_id, event_type, label, hidden, occurs_on, month, day, source, updated_at
                ) VALUES (?, ?, ?, ?, 1, ?, ?, ?, ?, ?)
                ON CONFLICT(event_key) DO UPDATE SET
                    user_id=excluded.user_id,
                    label=excluded.label,
                    occurs_on=excluded.occurs_on,
                    month=excluded.month,
                    day=excluded.day,
                    updated_at=excluded.updated_at
                """,
                (
                    f"birthday:{user_id}",
                    user_id,
                    "birthday",
                    f"{display_name}'s birthday",
                    next_occurrence.isoformat(),
                    birthday.month,
                    birthday.day,
                    "birthday",
                    now,
                ),
            )

        return BirthdayRecord(
            user_id=user_id,
            display_name=display_name,
            birthday=birthday,
            next_occurrence=next_occurrence,
            created_at=created_at,
            updated_at=now,
        )

    def get_birthday(self, user_id: str) -> BirthdayRecord | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT user_id, display_name, birthday_iso, created_at, updated_at
                FROM birthdays
                WHERE user_id = ?
                """,
                (user_id,),
            ).fetchone()
        if row is None:
            return None
        birthday = date.fromisoformat(row["birthday_iso"])
        return BirthdayRecord(
            user_id=row["user_id"],
            display_name=row["display_name"],
            birthday=birthday,
            next_occurrence=_next_birthday_occurrence(birthday),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def hidden_calendar_entry(self, user_id: str) -> dict[str, str | int] | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT event_key, user_id, event_type, label, hidden, occurs_on, month, day, source, updated_at
                FROM hidden_calendar
                WHERE event_key = ?
                """,
                (f"birthday:{user_id}",),
            ).fetchone()
        return dict(row) if row is not None else None

    def is_users_birthday(self, user_id: str, today: date | None = None) -> bool:
        record = self.get_birthday(user_id)
        if record is None:
            return False
        today = today or date.today()
        return record.birthday.month == today.month and record.birthday.day == today.day

    def has_sent_birthday_wish(self, user_id: str, wish_date: date | None = None) -> bool:
        wish_date = wish_date or date.today()
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT 1
                FROM birthday_wishes
                WHERE user_id = ? AND wish_date = ?
                """,
                (user_id, wish_date.isoformat()),
            ).fetchone()
        return row is not None

    def record_birthday_wish(self, *, user_id: str, script_id: str, wish_date: date | None = None) -> None:
        wish_date = wish_date or date.today()
        now = _utc_now_iso()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO birthday_wishes (user_id, wish_date, script_id, wished_at)
                VALUES (?, ?, ?, ?)
                """,
                (user_id, wish_date.isoformat(), script_id, now),
            )
