from __future__ import annotations

import json
import os
import threading
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .models import ChannelPresence, GuildMemberProgress, PersonaState, UserMemory


def _default_payload() -> dict[str, Any]:
    return {
        "users": {},
        "personas": {
            "Lia": asdict(PersonaState(name="Lia", mood="chaotic")),
            "Yuna": asdict(PersonaState(name="Yuna", mood="observant")),
        },
        "channels": {},
        "member_progress": {},
        "daily_answers": {},
        "cooldowns": {},
        "guild_notices": {},
        "runtime": {},
        "stats": {},
    }


class MemoryStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self._lock = threading.RLock()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._payload = self._load_from_disk()
        self._save_locked()

    def _load_from_disk(self) -> dict[str, Any]:
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, FileNotFoundError, UnicodeDecodeError):
            payload = _default_payload()
        return self._normalize(payload)

    def _normalize(self, payload: dict[str, Any]) -> dict[str, Any]:
        normalized = _default_payload()
        for key in ("users", "personas", "channels", "member_progress", "daily_answers", "cooldowns", "guild_notices", "runtime", "stats"):
            raw = payload.get(key)
            if isinstance(raw, dict):
                normalized[key] = raw

        personas = normalized["personas"]
        personas.setdefault("Lia", asdict(PersonaState(name="Lia", mood="chaotic")))
        personas.setdefault("Yuna", asdict(PersonaState(name="Yuna", mood="observant")))
        return normalized

    def _save_locked(self) -> None:
        temp_path = self.path.with_suffix(f"{self.path.suffix}.tmp")
        temp_path.write_text(json.dumps(self._payload, indent=2), encoding="utf-8")
        os.replace(temp_path, self.path)

    def flush(self) -> None:
        with self._lock:
            self._save_locked()

    def get_user(self, user_id: str, display_name: str) -> UserMemory:
        with self._lock:
            users = self._payload.setdefault("users", {})
            if user_id not in users:
                users[user_id] = asdict(UserMemory(name=display_name))
                self._save_locked()
            user = UserMemory(**users[user_id])
            if user.name != display_name:
                user.name = display_name
                users[user_id] = asdict(user)
                self._save_locked()
            return user

    def save_user(self, user_id: str, memory: UserMemory, *, flush: bool = True) -> None:
        with self._lock:
            self._payload.setdefault("users", {})[user_id] = asdict(memory)
            if flush:
                self._save_locked()

    def user_count(self) -> int:
        with self._lock:
            return len(self._payload.get("users", {}))

    def get_persona_state(self, name: str) -> PersonaState:
        with self._lock:
            personas = self._payload.setdefault("personas", {})
            if name not in personas:
                personas[name] = asdict(PersonaState(name=name, mood="neutral"))
                self._save_locked()
            return PersonaState(**personas[name])

    def save_persona_state(self, state: PersonaState, *, flush: bool = True) -> None:
        with self._lock:
            self._payload.setdefault("personas", {})[state.name] = asdict(state)
            if flush:
                self._save_locked()

    def get_channel(self, channel_id: int, guild_id: int) -> ChannelPresence:
        with self._lock:
            channels = self._payload.setdefault("channels", {})
            key = str(channel_id)
            if key not in channels:
                channels[key] = asdict(ChannelPresence(channel_id=channel_id, guild_id=guild_id))
                self._save_locked()
            return ChannelPresence(**channels[key])

    def save_channel(self, state: ChannelPresence, *, flush: bool = True) -> None:
        with self._lock:
            self._payload.setdefault("channels", {})[str(state.channel_id)] = asdict(state)
            if flush:
                self._save_locked()

    def all_channels(self) -> list[ChannelPresence]:
        with self._lock:
            return [ChannelPresence(**raw) for raw in self._payload.get("channels", {}).values()]

    @staticmethod
    def _member_progress_key(guild_id: int, user_id: str) -> str:
        return f"{guild_id}:{user_id}"

    def get_member_progress(self, guild_id: int, user_id: str, display_name: str) -> GuildMemberProgress:
        with self._lock:
            progress_map = self._payload.setdefault("member_progress", {})
            key = self._member_progress_key(guild_id, user_id)
            if key not in progress_map:
                progress_map[key] = asdict(GuildMemberProgress(user_id=user_id, guild_id=guild_id, name=display_name))
                self._save_locked()
            progress = GuildMemberProgress(**progress_map[key])
            if progress.name != display_name:
                progress.name = display_name
                progress_map[key] = asdict(progress)
                self._save_locked()
            return progress

    def save_member_progress(self, progress: GuildMemberProgress) -> None:
        with self._lock:
            progress_map = self._payload.setdefault("member_progress", {})
            key = self._member_progress_key(progress.guild_id, progress.user_id)
            progress_map[key] = asdict(progress)
            self._save_locked()

    def leaderboard_snapshot(self, guild_id: int, limit: int = 10) -> list[GuildMemberProgress]:
        with self._lock:
            entries = [
                GuildMemberProgress(**raw)
                for raw in self._payload.get("member_progress", {}).values()
                if int(raw.get("guild_id", 0)) == guild_id
            ]
        entries.sort(key=lambda item: (item.level, item.xp, item.eligible_messages), reverse=True)
        return entries[:limit]

    def record_daily_answer(
        self,
        *,
        guild_id: int,
        user_id: str,
        user_name: str,
        answer_date: str,
        script_id: str,
        prompt: str,
        answer: str,
        answered_at: str,
        flush: bool = True,
    ) -> None:
        with self._lock:
            daily_answers = self._payload.setdefault("daily_answers", {})
            key = f"{guild_id}:{answer_date}:{user_id}"
            daily_answers[key] = {
                "guild_id": guild_id,
                "user_id": user_id,
                "user_name": user_name,
                "answer_date": answer_date,
                "script_id": script_id,
                "prompt": prompt,
                "answer": answer,
                "answered_at": answered_at,
            }
            if flush:
                self._save_locked()

    def daily_answer_count(self, guild_id: int, answer_date: str) -> int:
        with self._lock:
            return sum(
                1
                for raw in self._payload.get("daily_answers", {}).values()
                if int(raw.get("guild_id", 0)) == guild_id and raw.get("answer_date") == answer_date
            )

    def cooldown_map(self) -> dict[str, str]:
        with self._lock:
            return dict(self._payload.get("cooldowns", {}))

    def save_cooldown_map(self, cooldowns: dict[str, str], *, flush: bool = True) -> None:
        with self._lock:
            self._payload["cooldowns"] = cooldowns
            if flush:
                self._save_locked()

    def guild_notice_sent(self, guild_id: int, notice_key: str) -> bool:
        with self._lock:
            notices = self._payload.setdefault("guild_notices", {})
            return bool(notices.get(str(guild_id), {}).get(notice_key, False))

    def mark_guild_notice_sent(self, guild_id: int, notice_key: str) -> None:
        with self._lock:
            notices = self._payload.setdefault("guild_notices", {})
            guild_notices = notices.setdefault(str(guild_id), {})
            guild_notices[notice_key] = True
            self._save_locked()

    def get_runtime_value(self, key: str, default: Any = None) -> Any:
        with self._lock:
            runtime = self._payload.setdefault("runtime", {})
            return runtime.get(key, default)

    def set_runtime_value(self, key: str, value: Any, *, flush: bool = True) -> None:
        with self._lock:
            runtime = self._payload.setdefault("runtime", {})
            runtime[key] = value
            if flush:
                self._save_locked()

    def _stats(self, payload: dict[str, Any]) -> dict[str, Any]:
        stats = payload.setdefault("stats", {})
        stats.setdefault("messages_seen", 0)
        stats.setdefault("trigger_matches", 0)
        stats.setdefault("triggered_replies", 0)
        stats.setdefault("ambient_replies", 0)
        stats.setdefault("persona_reply_counts", {"Lia": 0, "Yuna": 0})
        stats.setdefault("persona_like_counts", {"Lia": 0, "Yuna": 0})
        stats.setdefault("script_fire_counts", {})
        stats.setdefault("trigger_answer_counts", {})
        stats.setdefault("user_reply_counts", {})
        stats.setdefault("user_trigger_discoveries", {})
        stats.setdefault("bot_messages", {})
        return stats

    def increment_stat(self, key: str, amount: int = 1, *, flush: bool = True) -> None:
        with self._lock:
            stats = self._stats(self._payload)
            stats[key] = int(stats.get(key, 0)) + amount
            if flush:
                self._save_locked()

    def record_trigger_match_count(self, count: int, *, flush: bool = True) -> None:
        if count <= 0:
            return
        self.increment_stat("trigger_matches", count, flush=flush)

    def record_script_fire(
        self,
        *,
        user_id: str,
        user_name: str,
        script_id: str,
        actor_names: list[str],
        triggers: list[str],
        ambient: bool = False,
        flush: bool = True,
    ) -> None:
        with self._lock:
            stats = self._stats(self._payload)
            key = "ambient_replies" if ambient else "triggered_replies"
            stats[key] = int(stats.get(key, 0)) + 1
            script_counts = stats.setdefault("script_fire_counts", {})
            script_counts[script_id] = int(script_counts.get(script_id, 0)) + 1

            if not ambient:
                user_reply_counts = stats.setdefault("user_reply_counts", {})
                user_reply_counts[user_id] = {
                    "name": user_name,
                    "count": int(user_reply_counts.get(user_id, {}).get("count", 0)) + 1,
                }

            persona_counts = stats.setdefault("persona_reply_counts", {"Lia": 0, "Yuna": 0})
            for actor in actor_names:
                persona_counts[actor] = int(persona_counts.get(actor, 0)) + 1

            trigger_counts = stats.setdefault("trigger_answer_counts", {})
            for trigger in triggers:
                trigger_counts[trigger] = int(trigger_counts.get(trigger, 0)) + 1

            if not ambient:
                discoveries = stats.setdefault("user_trigger_discoveries", {})
                user_discovery = discoveries.setdefault(user_id, {"name": user_name, "triggers": [], "hits": 0})
                user_discovery["name"] = user_name
                user_discovery["hits"] = int(user_discovery.get("hits", 0)) + len(triggers)
                existing = set(user_discovery.get("triggers", []))
                for trigger in triggers:
                    if trigger not in existing:
                        user_discovery.setdefault("triggers", []).append(trigger)
                        existing.add(trigger)

            if flush:
                self._save_locked()

    def record_bot_message(self, *, actor: str, message_id: int, guild_id: int | None, channel_id: int) -> None:
        with self._lock:
            stats = self._stats(self._payload)
            bot_messages = stats.setdefault("bot_messages", {})
            bot_messages[str(message_id)] = {
                "actor": actor,
                "guild_id": guild_id,
                "channel_id": channel_id,
                "likes": 0,
            }
            self._save_locked()

    def record_bot_message_like(self, message_id: int) -> str | None:
        with self._lock:
            stats = self._stats(self._payload)
            bot_messages = stats.setdefault("bot_messages", {})
            raw = bot_messages.get(str(message_id))
            if raw is None:
                return None
            raw["likes"] = int(raw.get("likes", 0)) + 1
            actor = raw.get("actor")
            if actor:
                persona_likes = stats.setdefault("persona_like_counts", {"Lia": 0, "Yuna": 0})
                persona_likes[actor] = int(persona_likes.get(actor, 0)) + 1
            self._save_locked()
            return actor

    def stats_snapshot(self) -> dict[str, Any]:
        with self._lock:
            stats = self._stats(self._payload)
            return {
                "messages_seen": int(stats.get("messages_seen", 0)),
                "trigger_matches": int(stats.get("trigger_matches", 0)),
                "triggered_replies": int(stats.get("triggered_replies", 0)),
                "ambient_replies": int(stats.get("ambient_replies", 0)),
                "persona_reply_counts": dict(stats.get("persona_reply_counts", {})),
                "persona_like_counts": dict(stats.get("persona_like_counts", {})),
                "script_fire_counts": dict(stats.get("script_fire_counts", {})),
                "trigger_answer_counts": dict(stats.get("trigger_answer_counts", {})),
                "user_reply_counts": dict(stats.get("user_reply_counts", {})),
                "user_trigger_discoveries": dict(stats.get("user_trigger_discoveries", {})),
            }
