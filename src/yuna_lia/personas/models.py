from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def utc_now_iso() -> str:
    return utc_now().isoformat()


@dataclass(frozen=True)
class TriggerRule:
    source_file: str
    trigger: str
    script_id: str
    weight: float
    cooldown_seconds: int
    attention_cost: str
    mood_shift: str


@dataclass(frozen=True)
class ScriptStep:
    actor: str
    message: str


@dataclass(frozen=True)
class Script:
    script_id: str
    steps: tuple[ScriptStep, ...]


@dataclass
class UserMemory:
    name: str
    first_seen: str = field(default_factory=utc_now_iso)
    last_seen: str = field(default_factory=utc_now_iso)
    lia_affinity: int = 0
    yuna_affinity: int = 0
    inside_jokes: list[str] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)
    favorite_topics: list[str] = field(default_factory=list)
    lia_trust: int = 0
    lia_rivalry: int = 0
    lia_flirt_tension: int = 0
    yuna_trust: int = 0
    yuna_rivalry: int = 0
    yuna_flirt_tension: int = 0
    messages_sent: int = 0
    late_night_messages: int = 0
    dramatic_messages: int = 0
    food_messages: int = 0
    direct_lia_mentions: int = 0
    direct_yuna_mentions: int = 0
    question_messages: int = 0
    slang_messages: int = 0
    vulnerability_messages: int = 0
    affection_messages: int = 0


@dataclass
class GuildMemberProgress:
    user_id: str
    guild_id: int
    name: str
    xp: int = 0
    level: int = 0
    eligible_messages: int = 0
    total_messages: int = 0
    last_xp_at: str = ""
    last_level_up_at: str = ""


@dataclass
class PersonaState:
    name: str
    mood: str
    energy: int = 75
    boredom: int = 30
    busy_until: str = ""
    last_message_at: str = field(default_factory=utc_now_iso)
    last_script_id: str = ""
    script_history: list[str] = field(default_factory=list)


@dataclass
class ChannelPresence:
    channel_id: int
    guild_id: int
    last_user_message_at: str = field(default_factory=utc_now_iso)
    last_bot_message_at: str = ""
    user_message_count: int = 0
    bot_message_count: int = 0
    last_script_id: str = ""
    recent_topics: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class SimulationDecision:
    script_id: str
    score: float
    reason: str
    rules: tuple[TriggerRule, ...]
