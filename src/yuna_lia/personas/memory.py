from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .models import ChannelPresence, PersonaState, UserMemory


class MemoryStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._save(
                {
                    "users": {},
                    "personas": {
                        "Lia": asdict(PersonaState(name="Lia", mood="chaotic")),
                        "Yuna": asdict(PersonaState(name="Yuna", mood="observant")),
                    },
                    "channels": {},
                    "cooldowns": {},
                    "guild_notices": {},
                    "stats": {},
                }
            )

    def _load(self) -> dict[str, Any]:
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, FileNotFoundError, UnicodeDecodeError):
            payload = {"users": {}, "personas": {}, "channels": {}, "cooldowns": {}, "guild_notices": {}, "stats": {}}
            self._save(payload)
            return payload

    def _save(self, payload: dict[str, Any]) -> None:
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def get_user(self, user_id: str, display_name: str) -> UserMemory:
        payload = self._load()
        users = payload.setdefault("users", {})
        if user_id not in users:
            users[user_id] = asdict(UserMemory(name=display_name))
            self._save(payload)
        user = UserMemory(**users[user_id])
        if user.name != display_name:
            user.name = display_name
            users[user_id] = asdict(user)
            self._save(payload)
        return user

    def save_user(self, user_id: str, memory: UserMemory) -> None:
        payload = self._load()
        payload.setdefault("users", {})[user_id] = asdict(memory)
        self._save(payload)

    def user_count(self) -> int:
        return len(self._load().get("users", {}))

    def get_persona_state(self, name: str) -> PersonaState:
        payload = self._load()
        personas = payload.setdefault("personas", {})
        if name not in personas:
            personas[name] = asdict(PersonaState(name=name, mood="neutral"))
            self._save(payload)
        return PersonaState(**personas[name])

    def save_persona_state(self, state: PersonaState) -> None:
        payload = self._load()
        payload.setdefault("personas", {})[state.name] = asdict(state)
        self._save(payload)

    def get_channel(self, channel_id: int, guild_id: int) -> ChannelPresence:
        payload = self._load()
        channels = payload.setdefault("channels", {})
        key = str(channel_id)
        if key not in channels:
            channels[key] = asdict(ChannelPresence(channel_id=channel_id, guild_id=guild_id))
            self._save(payload)
        return ChannelPresence(**channels[key])

    def save_channel(self, state: ChannelPresence) -> None:
        payload = self._load()
        payload.setdefault("channels", {})[str(state.channel_id)] = asdict(state)
        self._save(payload)

    def all_channels(self) -> list[ChannelPresence]:
        payload = self._load()
        return [ChannelPresence(**raw) for raw in payload.get("channels", {}).values()]

    def cooldown_map(self) -> dict[str, str]:
        return dict(self._load().get("cooldowns", {}))

    def save_cooldown_map(self, cooldowns: dict[str, str]) -> None:
        payload = self._load()
        payload["cooldowns"] = cooldowns
        self._save(payload)

    def guild_notice_sent(self, guild_id: int, notice_key: str) -> bool:
        payload = self._load()
        notices = payload.setdefault("guild_notices", {})
        return bool(notices.get(str(guild_id), {}).get(notice_key, False))

    def mark_guild_notice_sent(self, guild_id: int, notice_key: str) -> None:
        payload = self._load()
        notices = payload.setdefault("guild_notices", {})
        guild_notices = notices.setdefault(str(guild_id), {})
        guild_notices[notice_key] = True
        self._save(payload)

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

    def increment_stat(self, key: str, amount: int = 1) -> None:
        payload = self._load()
        stats = self._stats(payload)
        stats[key] = int(stats.get(key, 0)) + amount
        self._save(payload)

    def record_trigger_match_count(self, count: int) -> None:
        if count <= 0:
            return
        self.increment_stat("trigger_matches", count)

    def record_script_fire(
        self,
        *,
        user_id: str,
        user_name: str,
        script_id: str,
        actor_names: list[str],
        triggers: list[str],
        ambient: bool = False,
    ) -> None:
        payload = self._load()
        stats = self._stats(payload)
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

        self._save(payload)

    def record_bot_message(self, *, actor: str, message_id: int, guild_id: int | None, channel_id: int) -> None:
        payload = self._load()
        stats = self._stats(payload)
        bot_messages = stats.setdefault("bot_messages", {})
        bot_messages[str(message_id)] = {
            "actor": actor,
            "guild_id": guild_id,
            "channel_id": channel_id,
            "likes": 0,
        }
        self._save(payload)

    def record_bot_message_like(self, message_id: int) -> str | None:
        payload = self._load()
        stats = self._stats(payload)
        bot_messages = stats.setdefault("bot_messages", {})
        raw = bot_messages.get(str(message_id))
        if raw is None:
            return None
        raw["likes"] = int(raw.get("likes", 0)) + 1
        actor = raw.get("actor")
        if actor:
            persona_likes = stats.setdefault("persona_like_counts", {"Lia": 0, "Yuna": 0})
            persona_likes[actor] = int(persona_likes.get(actor, 0)) + 1
        self._save(payload)
        return actor

    def stats_snapshot(self) -> dict[str, Any]:
        payload = self._load()
        stats = self._stats(payload)
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
