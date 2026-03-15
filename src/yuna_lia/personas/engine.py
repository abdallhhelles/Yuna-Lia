from __future__ import annotations

import json
import random
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

from ..runtime import get_logger
from .content import PersonaContentStore
from .memory import MemoryStore
from .models import ChannelPresence, PersonaState, SimulationDecision, TriggerRule, UserMemory, utc_now, utc_now_iso


def _parse_iso(value: str) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def _debug_timestamp() -> str:
    return utc_now().strftime("%H:%M:%S")


def _normalize_text(value: str) -> str:
    lowered = value.lower()
    lowered = re.sub(r"\s+", " ", lowered)
    return lowered.strip()


def _contains_trigger(content: str, trigger: str) -> bool:
    pattern = rf"(?<!\w){re.escape(trigger)}(?!\w)"
    return re.search(pattern, content) is not None


@dataclass(frozen=True)
class OutboundEvent:
    actor: str
    message: str


class PersonaSimulationEngine:
    def __init__(
        self,
        content: PersonaContentStore,
        memory: MemoryStore,
        log_path: Path,
        *,
        debug: bool = True,
        test_mode: bool = False,
    ) -> None:
        self.content = content
        self.memory = memory
        self.log_path = log_path
        self.debug = debug
        self.test_mode = test_mode
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.logger = get_logger("yuna_lia.engine")

    def reload(self) -> None:
        self.content.reload()

    def inspect_user(self, user_id: str, display_name: str) -> UserMemory:
        return self.memory.get_user(user_id, display_name)

    def status(self) -> dict[str, object]:
        self.content.ensure_loaded()
        return {
            "Lia": self.memory.get_persona_state("Lia"),
            "Yuna": self.memory.get_persona_state("Yuna"),
            "content_files": len(list(self.content.root.rglob("*.txt"))),
            "script_count": len(self.content.scripts),
            "trigger_count": sum(len(rules) for rules in self.content.triggers_by_actor.values()),
        }

    def script_ids_with_prefix(self, prefix: str) -> list[str]:
        self.content.ensure_loaded()
        return sorted(script_id for script_id in self.content.scripts if script_id.startswith(prefix))

    def render_script_by_id(self, script_id: str, user_id: str, display_name: str) -> list[OutboundEvent]:
        self.content.ensure_loaded()
        memory = self.memory.get_user(user_id, display_name)
        script = self.content.scripts.get(script_id)
        if script is None:
            raise KeyError(f"Unknown script_id: {script_id}")
        return [OutboundEvent(actor=step.actor, message=self._render(step.message, memory, "")) for step in script.steps]

    def handle_message(
        self,
        *,
        user_id: str,
        display_name: str,
        guild_id: int,
        channel_id: int,
        content: str,
    ) -> list[OutboundEvent]:
        self.content.ensure_loaded()
        memory = self.memory.get_user(user_id, display_name)
        channel = self.memory.get_channel(channel_id, guild_id)
        self.memory.increment_stat("messages_seen")
        self._update_memory(memory, channel, content)
        self.memory.save_user(user_id, memory)
        self.memory.save_channel(channel)

        candidates = self._candidate_rules(content)
        self.memory.record_trigger_match_count(len(candidates))
        self._debug_candidates(content, candidates)
        decision = self._choose_decision(user_id, candidates, memory, channel)
        if decision is None:
            if candidates:
                self._debug_print("matched triggers but no script cleared cooldown/attention gates")
            return []

        self._debug_decision(decision)
        self._apply_decision(user_id, decision, memory)
        self.apply_relationship_progression(memory, decision.script_id, decision.rules)
        self.memory.save_user(user_id, memory)
        channel.bot_message_count += 1
        channel.last_bot_message_at = utc_now_iso()
        channel.last_script_id = decision.script_id
        self.memory.save_channel(channel)
        script = self.content.scripts[decision.script_id]
        actors = sorted({step.actor for step in script.steps if step.actor in {"Lia", "Yuna"}})
        answered_triggers = sorted({rule.trigger for rule in decision.rules})
        self.memory.record_script_fire(
            user_id=user_id,
            user_name=display_name,
            script_id=decision.script_id,
            actor_names=actors,
            triggers=answered_triggers,
            ambient=False,
        )
        events = [
            OutboundEvent(actor=step.actor, message=self._render(step.message, memory, content))
            for step in script.steps
        ]
        self._log_fire(user_id, channel_id, decision)
        return events

    def maybe_ambient_event(self, *, guild_id: int, channel_id: int) -> list[OutboundEvent]:
        self.content.ensure_loaded()
        channel = self.memory.get_channel(channel_id, guild_id)
        last_activity = _parse_iso(channel.last_user_message_at)
        if last_activity is None:
            return []
        silence = (utc_now() - last_activity).total_seconds()
        if silence < 900:
            return []
        pool = self._eligible_ambient_scripts()
        if not pool:
            return []
        chance = min(0.45, 0.08 + (silence / 1800.0) + (self._average_boredom() / 400.0))
        if random.random() > chance:
            return []
        weighted = [(script_id, self._ambient_score(script_id, silence)) for script_id in pool]
        weighted.sort(key=lambda item: item[1], reverse=True)
        top_score = weighted[0][1]
        top = [item for item in weighted if item[1] >= top_score - 0.12]
        script_id = random.choice(top)[0]
        decision = SimulationDecision(script_id=script_id, score=0.5, reason="ambient", rules=tuple())
        self._debug_print(f"ambient trigger selected script={script_id} guild={guild_id} channel={channel_id}")
        events = [
            OutboundEvent(actor=step.actor, message=step.message)
            for step in self.content.scripts[script_id].steps
        ]
        actors = sorted({step.actor for step in self.content.scripts[script_id].steps if step.actor in {"Lia", "Yuna"}})
        self.memory.record_script_fire(
            user_id="ambient",
            user_name="ambient",
            script_id=script_id,
            actor_names=actors,
            triggers=[],
            ambient=True,
        )
        channel.bot_message_count += 1
        channel.last_bot_message_at = utc_now_iso()
        channel.last_script_id = script_id
        self.memory.save_channel(channel)
        cooldowns = self.memory.cooldown_map()
        cooldowns[f"ambient:{script_id}"] = (utc_now() + timedelta(hours=6)).isoformat()
        self.memory.save_cooldown_map(cooldowns)
        self._log_fire("ambient", channel_id, decision)
        return events

    def _candidate_rules(self, content: str) -> list[TriggerRule]:
        lowered = _normalize_text(content)
        rules = (
            self.content.triggers_by_actor["shared"]
            + self.content.triggers_by_actor["Lia"]
            + self.content.triggers_by_actor["Yuna"]
        )
        return [rule for rule in rules if _contains_trigger(lowered, rule.trigger)]

    def _debug_candidates(self, content: str, rules: list[TriggerRule]) -> None:
        if not self.debug:
            return
        preview = content.strip().replace("\n", " ")
        if len(preview) > 80:
            preview = preview[:77] + "..."
        if not rules:
            self._debug_print(f'no trigger match for "{preview}"')
            return
        details = ", ".join(
            f"{rule.trigger}->{rule.script_id} ({rule.source_file})"
            for rule in rules[:8]
        )
        suffix = "" if len(rules) <= 8 else f" ... +{len(rules) - 8} more"
        self._debug_print(f'matched {len(rules)} trigger(s) for "{preview}": {details}{suffix}')

    def _debug_decision(self, decision: SimulationDecision) -> None:
        if not self.debug:
            return
        rules = ", ".join(rule.trigger for rule in decision.rules[:8]) or "ambient"
        suffix = "" if len(decision.rules) <= 8 else f" ... +{len(decision.rules) - 8} more"
        self._debug_print(
            f"selected script={decision.script_id} reason={decision.reason} "
            f"score={decision.score:.2f} from [{rules}{suffix}]"
        )

    def _choose_decision(
        self,
        user_id: str,
        rules: list[TriggerRule],
        memory: UserMemory,
        channel: ChannelPresence,
    ) -> SimulationDecision | None:
        if not rules:
            return None
        cooldowns = self.memory.cooldown_map()
        now = utc_now()
        weighted: list[tuple[TriggerRule, float]] = []
        for rule in rules:
            key = f"user:{user_id}:{rule.script_id}"
            if not self.test_mode:
                expiry = _parse_iso(cooldowns.get(key, ""))
                if expiry and expiry > now:
                    continue
            weighted.append((rule, self._score_rule(rule, memory, channel)))
        if not weighted:
            return None
        weighted.sort(key=lambda item: item[1], reverse=True)
        top_score = weighted[0][1]
        top = [item for item in weighted if item[1] >= top_score - 0.15]
        chosen_rule = random.choice(top)[0]
        return SimulationDecision(
            script_id=chosen_rule.script_id,
            score=top_score,
            reason=f"trigger:{chosen_rule.trigger}",
            rules=tuple(rule for rule, _ in weighted if rule.script_id == chosen_rule.script_id),
        )

    def _apply_decision(self, user_id: str, decision: SimulationDecision, memory: UserMemory) -> None:
        cooldowns = self.memory.cooldown_map()
        now = utc_now()
        cooldown_seconds = max((rule.cooldown_seconds for rule in decision.rules), default=300)
        if not self.test_mode:
            cooldowns[f"user:{user_id}:{decision.script_id}"] = (now + timedelta(seconds=cooldown_seconds)).isoformat()
        self.memory.save_cooldown_map(cooldowns)

        for rule in decision.rules:
            topic = rule.trigger
            if topic not in memory.favorite_topics:
                memory.favorite_topics.append(topic)
        memory.favorite_topics = memory.favorite_topics[-8:]
        memory.last_seen = utc_now_iso()
        self.memory.save_user(user_id, memory)

        new_mood = self._dominant_mood(decision.rules)
        script = self.content.scripts.get(decision.script_id)
        involved_actors = {step.actor for step in script.steps} if script is not None else {"Lia", "Yuna"}
        for actor in ("Lia", "Yuna"):
            state = self.memory.get_persona_state(actor)
            self._refresh_persona_state(state)
            state.last_script_id = decision.script_id
            state.last_message_at = utc_now_iso()
            state.script_history.append(decision.script_id)
            state.script_history = state.script_history[-12:]
            state.energy = max(5, state.energy - self._attention_cost(decision.rules))
            state.boredom = max(0, state.boredom - 15)
            state.busy_until = ""
            if actor in involved_actors:
                state.mood = new_mood
            elif state.mood == new_mood:
                state.mood = "observant" if actor == "Yuna" else "chaotic"
            self.memory.save_persona_state(state)

    @staticmethod
    def _render(template: str, memory: UserMemory, original_message: str) -> str:
        return (
            template.replace("{user}", memory.name)
            .replace("{topic}", (memory.favorite_topics[-1] if memory.favorite_topics else "that"))
            .replace("{message}", original_message)
        )

    @staticmethod
    def _update_memory(memory: UserMemory, channel: ChannelPresence, content: str) -> None:
        memory.last_seen = utc_now_iso()
        lowered = content.lower()
        topic = lowered.split(" ")[0][:24] if content.strip() else "silence"
        memory.messages_sent += 1
        channel.user_message_count += 1
        if any(token in lowered for token in ("drama", "fight", "argue", "ghosted", "messy")):
            memory.dramatic_messages += 1
        if any(token in lowered for token in ("pizza", "food", "pasta", "snack", "dessert", "coffee", "tea")):
            memory.food_messages += 1
        if any(token in lowered for token in ("lia", "@lia")):
            memory.direct_lia_mentions += 1
        if any(token in lowered for token in ("yuna", "@yuna")):
            memory.direct_yuna_mentions += 1
        hour = utc_now().hour
        if hour >= 23 or hour < 5:
            memory.late_night_messages += 1
        if topic and topic not in memory.favorite_topics:
            memory.favorite_topics.append(topic)
        memory.favorite_topics = memory.favorite_topics[-8:]
        channel.last_user_message_at = utc_now_iso()
        if topic and topic not in channel.recent_topics:
            channel.recent_topics.append(topic)
        channel.recent_topics = channel.recent_topics[-8:]

    def apply_relationship_progression(self, memory: UserMemory, script_id: str, rules: tuple[TriggerRule, ...]) -> None:
        script = self.content.scripts.get(script_id)
        if script is None:
            return
        involved_actors = {step.actor for step in script.steps if step.actor in {"Lia", "Yuna"}}
        mood_tokens = " ".join(rule.mood_shift.lower() for rule in rules)

        for actor in involved_actors:
            prefix = actor.lower()
            if any(token in mood_tokens for token in ("soft", "warm", "reflective", "supportive", "casual", "playful")):
                setattr(memory, f"{prefix}_trust", min(100, getattr(memory, f"{prefix}_trust") + 2))
            if any(token in mood_tokens for token in ("heated", "aggressive", "rivalry", "tension")):
                setattr(memory, f"{prefix}_rivalry", min(100, getattr(memory, f"{prefix}_rivalry") + 2))
            if any(token in mood_tokens for token in ("flirty", "romantic", "intimate")):
                setattr(memory, f"{prefix}_flirt_tension", min(100, getattr(memory, f"{prefix}_flirt_tension") + 2))

    def _score_rule(self, rule: TriggerRule, memory: UserMemory, channel: ChannelPresence) -> float:
        score = rule.weight
        if rule.trigger in memory.favorite_topics:
            score += 0.10
        if rule.trigger in channel.recent_topics:
            score += 0.06

        boredom = self._average_boredom()
        if any(token in rule.mood_shift for token in ("chaotic", "playful")):
            score += boredom / 250.0
        if "reflective" in rule.mood_shift and boredom < 30:
            score += 0.04

        recent_scripts = set()
        for actor in ("Lia", "Yuna"):
            state = self.memory.get_persona_state(actor)
            recent_scripts.update(state.script_history[-3:])
            if state.last_script_id == rule.script_id:
                score -= 0.22
        if rule.script_id in recent_scripts:
            score -= 0.08

        score += random.uniform(0.0, 0.12)
        return score

    @staticmethod
    def _dominant_mood(rules: tuple[TriggerRule, ...]) -> str:
        if not rules:
            return "observant"
        counts: dict[str, int] = {}
        for rule in rules:
            mood = rule.mood_shift.rstrip("+- ").strip().lower()
            if mood:
                counts[mood] = counts.get(mood, 0) + 1
        if not counts:
            return "observant"
        return max(counts.items(), key=lambda item: item[1])[0]

    def _eligible_ambient_scripts(self) -> list[str]:
        cooldowns = self.memory.cooldown_map()
        now = utc_now()
        pool: list[str] = []
        for script_id, script in self.content.scripts.items():
            if not (script_id.startswith("ambient_") or script_id.startswith("duo_")):
                continue
            actors = {step.actor for step in script.steps if step.actor in {"Lia", "Yuna"}}
            if actors != {"Lia", "Yuna"}:
                continue
            expiry = _parse_iso(cooldowns.get(f"ambient:{script_id}", ""))
            if expiry and expiry > now:
                continue
            pool.append(script_id)
        return pool

    def _ambient_score(self, script_id: str, silence: float) -> float:
        score = 0.2 if script_id.startswith("ambient_") else 0.1
        score += min(0.3, silence / 2400.0)
        if "late_night" in script_id or "soft" in script_id:
            score += 0.04
        score += random.uniform(0.0, 0.08)
        return score

    def _average_boredom(self) -> float:
        states = [self.memory.get_persona_state("Lia"), self.memory.get_persona_state("Yuna")]
        return sum(state.boredom for state in states) / len(states)

    def _debug_print(self, message: str) -> None:
        if self.debug:
            self.logger.debug("[%s] %s", _debug_timestamp(), message)

    @staticmethod
    def _attention_cost(rules: tuple[TriggerRule, ...] | list[TriggerRule]) -> int:
        scale = {"low": 10, "medium": 24, "high": 40}
        values = [scale.get(rule.attention_cost.lower(), 18) for rule in rules]
        return max(values or [18])

    @staticmethod
    def _refresh_persona_state(state: PersonaState) -> None:
        last_message = _parse_iso(state.last_message_at)
        if last_message is not None:
            elapsed = max(0, int((utc_now() - last_message).total_seconds() // 60))
            state.energy = min(100, state.energy + elapsed)
            state.boredom = min(100, state.boredom + max(0, elapsed // 2))

    def _log_fire(self, user_id: str, channel_id: int, decision: SimulationDecision) -> None:
        entry = {
            "timestamp": utc_now_iso(),
            "user_id": user_id,
            "channel_id": channel_id,
            "script_id": decision.script_id,
            "reason": decision.reason,
            "score": decision.score,
        }
        with self.log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry) + "\n")
