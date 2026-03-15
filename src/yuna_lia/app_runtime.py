from __future__ import annotations

import asyncio
import logging
import random
from datetime import date, datetime, timedelta, timezone

import discord
from discord.ext import commands

from .birthdays import BirthdayRecord, BirthdayStore
from .commands.game_commands import register_game_commands
from .config import AppConfig, PersonaConfig, load_config
from .personas import MemoryStore, PersonaContentStore, PersonaSimulationEngine
from .personas.engine import OutboundEvent
from .personas.models import GuildMemberProgress
from .runtime import get_logger, setup_logging
from .systems.conversation_pacing import ConversationPacingSystem
from .systems.leveling import LevelResult, level_for_xp, roll_xp, should_award_xp, xp_progress

YUNA_SPEAKER = "Yuna"
LIA_SPEAKER = "Lia"
LIA_INVITE_LINK = "https://discord.com/oauth2/authorize?client_id=1478877587026739220"
YUNA_INVITE_LINK = "https://discord.com/oauth2/authorize?client_id=1478877501169209424"


def _debug_timestamp() -> str:
    return datetime.now().strftime("%H:%M:%S")


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _local_now() -> datetime:
    return datetime.now().astimezone()


def _parse_iso_datetime(value: str) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


class DualPersonaRuntime:
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.logger = get_logger("yuna_lia.runtime")
        self.content = PersonaContentStore(config.content_dir)
        self.memory = MemoryStore(config.data_dir / "persona_state.json")
        self.birthdays = BirthdayStore(config.data_dir / "bot_data.sqlite3")
        self.engine = PersonaSimulationEngine(
            self.content,
            self.memory,
            config.data_dir / "script_fire_log.jsonl",
            debug=config.debug_persona,
            test_mode=config.persona_test_mode,
        )
        self.yuna_bot: commands.Bot | None = None
        self.lia_bot: commands.Bot | None = None
        self.pacing: ConversationPacingSystem | None = None
        self._ambient_task: asyncio.Task[None] | None = None
        self._daily_question_task: asyncio.Task[None] | None = None
        self._daily_question_prefix = "daily_question_"
        self._welcome_prefix = "welcome_"
        self._social_event_prefixes = {
            "pick_a_side": "social_pick_a_side_",
            "mini_poll": "social_mini_poll_",
            "hot_take": "social_hot_take_",
            "confession": "social_confession_",
            "late_night": "social_late_night_",
        }

    def bind_bots(self, yuna_bot: commands.Bot, lia_bot: commands.Bot) -> None:
        self.yuna_bot = yuna_bot
        self.lia_bot = lia_bot
        self.pacing = ConversationPacingSystem(self._resolve_bot_for_speaker)
        self.content.ensure_loaded()
        self._ambient_task = asyncio.create_task(self._ambient_loop(), name="persona-ambient-loop")
        self._daily_question_task = asyncio.create_task(self._daily_question_loop(), name="persona-daily-question-loop")

    def _resolve_bot_for_speaker(self, speaker: str) -> commands.Bot | None:
        if speaker == LIA_SPEAKER:
            return self.lia_bot
        return self.yuna_bot

    def _require_pacing(self) -> ConversationPacingSystem:
        if self.pacing is None:
            raise RuntimeError("runtime_not_initialized")
        return self.pacing

    async def command_about(self, interaction: discord.Interaction) -> None:
        lines = [
            "Lia and Yuna are scripted Discord personas, not AI chatbots.",
            "They react through external trigger files, human-written scripts, cooldowns, moods, attention rules, and lightweight memory.",
            "They now also track birthdays, relationship progression, passive achievements, daily questions, and social event prompts.",
            "",
            f"Content root: {self.config.content_dir}",
            "Use `/status` to inspect persona state.",
            "Use `/social_event`, `/relationship`, `/achievements`, and `/answer` for the engagement systems.",
            "Use `/reload_personas` after editing trigger or script files.",
        ]
        await interaction.response.send_message("\n".join(lines), ephemeral=True)

    async def command_status(self, interaction: discord.Interaction) -> None:
        status = self.engine.status()
        lia = status["Lia"]
        yuna = status["Yuna"]
        lines = [
            "Persona Status",
            "",
            f"Lia: mood={lia.mood} energy={lia.energy} boredom={lia.boredom} last_script={lia.last_script_id or 'none'}",
            f"Yuna: mood={yuna.mood} energy={yuna.energy} boredom={yuna.boredom} last_script={yuna.last_script_id or 'none'}",
            f"Message content intent: {'enabled' if self.config.enable_message_content else 'disabled'}",
            f"Loaded content files: {status['content_files']}",
            f"Loaded scripts: {status['script_count']}",
            f"Loaded triggers: {status['trigger_count']}",
        ]
        await interaction.response.send_message("\n".join(lines), ephemeral=True)

    async def command_memory(self, interaction: discord.Interaction, user: discord.User | discord.Member) -> None:
        memory = self.engine.inspect_user(str(user.id), user.display_name if hasattr(user, "display_name") else user.name)
        lines = [
            f"Memory for {memory.name}",
            f"First seen: {memory.first_seen}",
            f"Last seen: {memory.last_seen}",
            f"Lia affinity: {memory.lia_affinity}",
            f"Yuna affinity: {memory.yuna_affinity}",
            f"Favorite topics: {', '.join(memory.favorite_topics) or 'none'}",
            f"Inside jokes: {', '.join(memory.inside_jokes) or 'none'}",
            f"Conflicts: {', '.join(memory.conflicts) or 'none'}",
        ]
        await interaction.response.send_message("\n".join(lines), ephemeral=True)

    async def command_stats(self, interaction: discord.Interaction) -> None:
        stats = self.memory.stats_snapshot()
        persona_likes = stats["persona_like_counts"]
        persona_replies = stats["persona_reply_counts"]
        liked_winner = "tie"
        if persona_likes.get("Lia", 0) > persona_likes.get("Yuna", 0):
            liked_winner = "Lia"
        elif persona_likes.get("Yuna", 0) > persona_likes.get("Lia", 0):
            liked_winner = "Yuna"
        top_discoverers = sorted(
            stats["user_trigger_discoveries"].items(),
            key=lambda item: (len(item[1].get("triggers", [])), item[1].get("hits", 0)),
            reverse=True,
        )[:5]
        top_scripts = sorted(stats["script_fire_counts"].items(), key=lambda item: item[1], reverse=True)[:5]

        lines = [
            "Fun Stats",
            "",
            f"Servers: Yuna={len(self.yuna_bot.guilds) if self.yuna_bot else 0} Lia={len(self.lia_bot.guilds) if self.lia_bot else 0}",
            f"Tracked users: {self.memory.user_count()}",
            f"Tracked guild member progress rows: {len(self.memory.leaderboard_snapshot(interaction.guild_id, 1000)) if interaction.guild_id else 0}",
            f"Messages seen: {stats['messages_seen']}",
            f"Trigger matches found: {stats['trigger_matches']}",
            f"Total triggers loaded: {self.engine.status()['trigger_count']}",
            f"Triggered replies sent: {stats['triggered_replies']}",
            f"Ambient replies sent: {stats['ambient_replies']}",
            f"Lia lines sent: {persona_replies.get('Lia', 0)}",
            f"Yuna lines sent: {persona_replies.get('Yuna', 0)}",
            f"Lia liked message reactions: {persona_likes.get('Lia', 0)}",
            f"Yuna liked message reactions: {persona_likes.get('Yuna', 0)}",
            f"Most liked right now: {liked_winner}",
            "",
            "Top Trigger Discoverers",
        ]
        if top_discoverers:
            for index, (_, raw) in enumerate(top_discoverers, start=1):
                lines.append(
                    f"{index}. {raw.get('name', 'unknown')} - unique triggers {len(raw.get('triggers', []))}, hits {raw.get('hits', 0)}"
                )
        else:
            lines.append("No discoveries yet.")

        lines.append("")
        lines.append("Top Fired Scripts")
        if top_scripts:
            for index, (script_id, count) in enumerate(top_scripts, start=1):
                lines.append(f"{index}. {script_id} - {count}")
        else:
            lines.append("No scripts fired yet.")

        await interaction.response.send_message("\n".join(lines), ephemeral=True)

    async def command_reload(self, interaction: discord.Interaction) -> None:
        self.engine.reload()
        await interaction.response.send_message("Reloaded persona trigger and script files from disk.", ephemeral=True)

    async def command_level(
        self,
        interaction: discord.Interaction,
        user: discord.User | discord.Member | None = None,
    ) -> None:
        if interaction.guild_id is None:
            await interaction.response.send_message("`/level` only works in a server.", ephemeral=True)
            return
        target = user or interaction.user
        progress = self.memory.get_member_progress(interaction.guild_id, str(target.id), target.display_name if hasattr(target, "display_name") else target.name)
        level, current_xp, needed_xp = xp_progress(progress.xp)
        lines = [
            f"Level card for {progress.name}",
            f"Level: {level}",
            f"XP: {progress.xp}",
            f"Progress: {current_xp}/{needed_xp}",
            f"Eligible chat messages: {progress.eligible_messages}",
            f"Total chat messages: {progress.total_messages}",
        ]
        await interaction.response.send_message("\n".join(lines), ephemeral=True)

    async def command_leaderboard(self, interaction: discord.Interaction) -> None:
        if interaction.guild_id is None:
            await interaction.response.send_message("`/leaderboard` only works in a server.", ephemeral=True)
            return
        leaders = self.memory.leaderboard_snapshot(interaction.guild_id, 10)
        if not leaders:
            await interaction.response.send_message("No one has earned level XP here yet.", ephemeral=True)
            return
        lines = ["Level Leaderboard", ""]
        for index, entry in enumerate(leaders, start=1):
            lines.append(f"{index}. {entry.name} - level {entry.level} ({entry.xp} xp)")
        await interaction.response.send_message("\n".join(lines), ephemeral=True)

    async def command_roompulse(self, interaction: discord.Interaction) -> None:
        if interaction.guild_id is None:
            await interaction.response.send_message("`/roompulse` only works in a server channel.", ephemeral=True)
            return
        channel = self.memory.get_channel(interaction.channel_id, interaction.guild_id)
        now = _utc_now()
        last_activity = _parse_iso_datetime(channel.last_user_message_at)
        quiet_minutes = int((now - last_activity).total_seconds() // 60) if last_activity else None
        status = self.engine.status()
        topics = ", ".join(channel.recent_topics[-5:]) or "none yet"
        lines = [
            f"Room pulse for <#{interaction.channel_id}>",
            f"User messages tracked: {channel.user_message_count}",
            f"Bot scenes sent: {channel.bot_message_count}",
            f"Recent topics: {topics}",
            f"Quiet time: {quiet_minutes} minutes" if quiet_minutes is not None else "Quiet time: unknown",
            f"Last script: {channel.last_script_id or 'none'}",
            f"Lia mood: {status['Lia'].mood} | Yuna mood: {status['Yuna'].mood}",
            f"Suggestion: {self._engagement_suggestion(quiet_minutes)}",
        ]
        await interaction.response.send_message("\n".join(lines), ephemeral=True)

    async def command_birthday(self, interaction: discord.Interaction, raw_birthday: str) -> None:
        birthday = self.parse_birthday(raw_birthday)
        display_name = interaction.user.display_name if isinstance(interaction.user, discord.Member) else interaction.user.name
        record = self.birthdays.set_birthday(
            user_id=str(interaction.user.id),
            display_name=display_name,
            birthday=birthday,
        )
        await interaction.response.send_message(self._birthday_confirmation(record), ephemeral=True)

    async def command_answer(self, interaction: discord.Interaction, answer_text: str) -> None:
        if interaction.guild_id is None:
            await interaction.response.send_message("`/answer` only works in a server.", ephemeral=True)
            return
        script_id = self._current_daily_question_script_id(interaction.guild_id)
        if script_id is None:
            await interaction.response.send_message("There is no daily question active right now.", ephemeral=True)
            return
        channel_id = self._current_daily_question_channel_id(interaction.guild_id)
        if channel_id is None:
            await interaction.response.send_message(
                "There is no live daily-question post in this server yet. Wait for the automatic post, then try again.",
                ephemeral=True,
            )
            return
        prompt = self._daily_question_prompt(script_id)
        answer_date = self._current_daily_question_date(interaction.guild_id)
        self.memory.record_daily_answer(
            guild_id=interaction.guild_id,
            user_id=str(interaction.user.id),
            user_name=interaction.user.display_name if isinstance(interaction.user, discord.Member) else interaction.user.name,
            answer_date=answer_date,
            script_id=script_id,
            prompt=prompt,
            answer=answer_text.strip(),
            answered_at=_utc_now().isoformat(),
        )
        count = self.memory.daily_answer_count(interaction.guild_id, answer_date)
        announced = await self._announce_daily_answer(
            guild_id=interaction.guild_id,
            answer=answer_text.strip(),
        )
        if not announced:
            await interaction.response.send_message(
                "There is no live daily-question post in this server yet. Wait for the automatic post, then try again.",
                ephemeral=True,
            )
            return
        await interaction.response.send_message(
            f"Saved your answer and sent it through the bots to this server.\nPrompt: {prompt}\nTotal answers today: {count}",
            ephemeral=True,
        )

    async def command_social_event(self, interaction: discord.Interaction, category: str) -> None:
        prefix = self._social_event_prefixes[category]
        script_ids = self.engine.script_ids_with_prefix(prefix)
        if not script_ids:
            await interaction.response.send_message("That social event pack is empty right now.", ephemeral=True)
            return
        script_id = random.choice(script_ids)
        events = self.engine.render_script_by_id(script_id, str(interaction.user.id), interaction.user.display_name)
        await interaction.response.defer()
        await self._send_scripted_events(interaction.channel_id, events)

    async def command_relationship(
        self,
        interaction: discord.Interaction,
        user: discord.User | discord.Member | None = None,
    ) -> None:
        target = user or interaction.user
        memory = self.engine.inspect_user(str(target.id), target.display_name if hasattr(target, "display_name") else target.name)
        lines = [
            f"Relationship profile for {memory.name}",
            f"Lia: trust={memory.lia_trust} rivalry={memory.lia_rivalry} flirt_tension={memory.lia_flirt_tension}",
            f"Yuna: trust={memory.yuna_trust} rivalry={memory.yuna_rivalry} flirt_tension={memory.yuna_flirt_tension}",
        ]
        await interaction.response.send_message("\n".join(lines), ephemeral=True)

    async def command_achievements(
        self,
        interaction: discord.Interaction,
        user: discord.User | discord.Member | None = None,
    ) -> None:
        target = user or interaction.user
        memory = self.engine.inspect_user(str(target.id), target.display_name if hasattr(target, "display_name") else target.name)
        achievements = self._achievements_for(memory)
        lines = [f"Passive achievements for {memory.name}"]
        lines.extend(f"- {item}" for item in achievements)
        await interaction.response.send_message("\n".join(lines), ephemeral=True)

    @staticmethod
    def parse_birthday(raw_birthday: str) -> date:
        value = raw_birthday.strip()
        try:
            birthday = date.fromisoformat(value)
        except ValueError as exc:
            raise ValueError("Please use `YYYY-MM-DD`, for example `2001-09-14`.") from exc

        today = date.today()
        if birthday >= today:
            raise ValueError("That birthday is in the future. Use your real birth date.")
        if birthday.year < 1900:
            raise ValueError("Please enter a birthday from 1900 or later.")
        return birthday

    @staticmethod
    def _birthday_confirmation(record: BirthdayRecord) -> str:
        return (
            f"Saved your birthday as `{record.birthday.isoformat()}`.\n"
            f"Your next birthday is tracked privately for `{record.next_occurrence.isoformat()}` in the hidden calendar."
        )

    async def handle_user_message(self, message: discord.Message) -> None:
        if message.guild is None or message.author.bot or not message.content.strip():
            return
        await self._maybe_award_chat_xp(message)
        self._debug_print(
            f'message guild={message.guild.id} channel={message.channel.id} '
            f'user={message.author.display_name}: "{message.content}"'
        )
        await self._maybe_send_birthday_wish(message)
        await self._maybe_react(message)
        try:
            events = self.engine.handle_message(
                user_id=str(message.author.id),
                display_name=message.author.display_name,
                guild_id=message.guild.id,
                channel_id=message.channel.id,
                content=message.content,
            )
        except Exception:
            self.logger.exception("Failed handling user message in guild=%s channel=%s", message.guild.id, message.channel.id)
            return
        if not events:
            self._debug_print("no outbound events scheduled")
            return
        try:
            await self._send_scripted_events(message.channel.id, events)
        except Exception:
            self.logger.exception("Failed sending scripted events in channel=%s", message.channel.id)

    async def _maybe_react(self, message: discord.Message) -> None:
        lowered = message.content.lower()
        reaction = None
        actor = None
        if any(token in lowered for token in ("lol", "lmao", "skull")):
            actor, reaction = LIA_SPEAKER, "\U0001F480"
        elif any(token in lowered for token in ("coffee", "tea")):
            actor, reaction = YUNA_SPEAKER, "\u2615"
        elif any(token in lowered for token in ("pizza", "pasta", "food")):
            actor, reaction = LIA_SPEAKER, "\U0001F35D"
        elif any(token in lowered for token in ("lie", "cap", "dishonest")):
            actor, reaction = YUNA_SPEAKER, "\U0001F440"
        if actor is None or reaction is None or random.random() > 0.35:
            return
        bot = self._resolve_bot_for_speaker(actor)
        if bot is None:
            return
        channel = bot.get_channel(message.channel.id)
        if channel is None:
            try:
                channel = await bot.fetch_channel(message.channel.id)
            except Exception:
                self.logger.debug("Failed resolving channel %s for reaction", message.channel.id, exc_info=True)
                return
        try:
            target = await channel.fetch_message(message.id)
            await target.add_reaction(reaction)
        except Exception:
            self.logger.debug("Failed adding reaction to message %s", message.id, exc_info=True)
            return

    async def _maybe_send_birthday_wish(self, message: discord.Message) -> None:
        user_id = str(message.author.id)
        if not self.birthdays.is_users_birthday(user_id):
            return
        if self.birthdays.has_sent_birthday_wish(user_id):
            return

        self.content.ensure_loaded()
        candidates = sorted(script_id for script_id in self.content.scripts if script_id.startswith("birthday_duo_"))
        if not candidates:
            return

        script_id = random.choice(candidates)
        script = self.content.scripts[script_id]
        events = [OutboundEvent(actor=step.actor, message=step.message) for step in script.steps]
        await self._send_scripted_events(message.channel.id, events)
        self.birthdays.record_birthday_wish(user_id=user_id, script_id=script_id)

    async def _ambient_loop(self) -> None:
        while True:
            next_ambient_at = self._next_ambient_at()
            wait_seconds = max(1.0, (next_ambient_at - _utc_now()).total_seconds())
            await asyncio.sleep(wait_seconds)
            self._schedule_next_ambient()
            if self.yuna_bot is None:
                continue
            candidate_channels = self.memory.all_channels()[-20:]
            random.shuffle(candidate_channels)
            for channel_state in candidate_channels:
                events = self.engine.maybe_ambient_event(
                    guild_id=channel_state.guild_id,
                    channel_id=channel_state.channel_id,
                )
                if not events:
                    continue
                try:
                    await self._send_scripted_events(channel_state.channel_id, events)
                    window_start = self.memory.get_runtime_value("next_ambient_window_start", "")
                    if window_start:
                        self.memory.set_runtime_value("last_ambient_window_start", window_start)
                    break
                except Exception:
                    self.logger.warning("Ambient send failed in channel=%s", channel_state.channel_id, exc_info=True)
                    continue

    async def _daily_question_loop(self) -> None:
        while True:
            next_daily_question_at = self._next_daily_question_at()
            wait_seconds = max(1.0, (next_daily_question_at - _local_now()).total_seconds())
            await asyncio.sleep(wait_seconds)

            script_id = self._daily_question_script_id()
            if script_id is not None:
                today = _local_now().date().isoformat()
                for guild_id, channel_id in self._select_daily_question_channels().items():
                    if self._daily_question_posted_today(guild_id, today):
                        continue
                    try:
                        events = self.engine.render_script_by_id(script_id, "daily-question", "chat")
                        await self._send_scripted_events(channel_id, events)
                        self._record_daily_question_state(guild_id, script_id, channel_id, today)
                    except Exception:
                        self.logger.warning(
                            "Daily question send failed in guild=%s channel=%s",
                            guild_id,
                            channel_id,
                            exc_info=True,
                        )

            self._schedule_next_daily_question()

    async def _send_scripted_events(self, channel_id: int, events) -> None:
        previous_actor: str | None = None
        for index, event in enumerate(events):
            if index > 0:
                delay = self._inter_message_delay(previous_actor, event.actor)
                self._debug_print(f"waiting {delay:.1f}s before next line actor={event.actor}")
                await asyncio.sleep(delay)
            preview = event.message.replace("\n", " ")
            if len(preview) > 90:
                preview = preview[:87] + "..."
            self._debug_print(f'sending actor={event.actor} channel={channel_id} text="{preview}"')
            sent_message = await self._require_pacing().send_turn(channel_id, event.actor, event.message)
            if sent_message is not None:
                self.memory.record_bot_message(
                    actor=event.actor,
                    message_id=sent_message.id,
                    guild_id=sent_message.guild.id if sent_message.guild else None,
                    channel_id=channel_id,
                )
            self._debug_print(f'sent actor={event.actor} channel={channel_id} text="{preview}"')
            previous_actor = event.actor

    async def _announce_daily_answer(self, *, guild_id: int, answer: str) -> bool:
        channel_id = self.memory.get_runtime_value(self._daily_question_key(guild_id, "channel_id"), None)
        if channel_id is None:
            return False
        actor = random.choice((LIA_SPEAKER, YUNA_SPEAKER))
        if actor == LIA_SPEAKER:
            message = (
                f"okay someone said, \"{answer}\"\n"
                "ngl that one has flavor."
            )
        else:
            message = (
                f"someone answered, \"{answer}\"\n"
                "noted. better than the average room contribution."
            )
        await self._send_scripted_events(channel_id, [OutboundEvent(actor=actor, message=message)])
        return True

    async def _maybe_award_chat_xp(self, message: discord.Message) -> None:
        guild = message.guild
        if guild is None:
            return
        progress = self.memory.get_member_progress(guild.id, str(message.author.id), message.author.display_name)
        progress.total_messages += 1
        now = _utc_now()
        last_awarded = _parse_iso_datetime(progress.last_xp_at)
        if not should_award_xp(now, last_awarded):
            self.memory.save_member_progress(progress)
            return

        awarded = roll_xp()
        old_level = progress.level
        progress.xp += awarded
        progress.eligible_messages += 1
        progress.level = level_for_xp(progress.xp)
        progress.last_xp_at = now.isoformat()
        leveled_up = progress.level > old_level
        if leveled_up:
            progress.last_level_up_at = now.isoformat()
        self.memory.save_member_progress(progress)

        if leveled_up:
            result = LevelResult(awarded_xp=awarded, old_level=old_level, new_level=progress.level)
            await self._handle_level_up(message.author, guild, message.channel, progress, result)

    async def _handle_level_up(
        self,
        member: discord.Member,
        guild: discord.Guild,
        channel: discord.abc.Messageable,
        progress: GuildMemberProgress,
        result: LevelResult,
    ) -> None:
        reward_text = await self._apply_level_roles(member, progress.level)
        try:
            await channel.send(
                f"{member.mention} hit level {result.new_level} after a very suspicious amount of lurking and chatting."
                + (f" {reward_text}" if reward_text else "")
            )
        except Exception:
            self.logger.warning("Failed announcing level up for user=%s guild=%s", member.id, guild.id, exc_info=True)

    async def _apply_level_roles(self, member: discord.Member, level: int) -> str:
        if not self.config.level_role_rewards:
            return ""
        applied: list[str] = []
        for reward_level, role_name in self.config.level_role_rewards.items():
            if reward_level != level:
                continue
            role = discord.utils.get(member.guild.roles, name=role_name)
            if role is None and role_name.isdigit():
                role = member.guild.get_role(int(role_name))
            if role is None:
                self.logger.warning("Configured level reward role not found: %s", role_name)
                continue
            try:
                await member.add_roles(role, reason=f"Reached level {level}")
                applied.append(role.name)
            except Exception:
                self.logger.warning("Failed applying role reward %s to user=%s", role_name, member.id, exc_info=True)
        if not applied:
            return ""
        return "Unlocked role: " + ", ".join(applied)

    async def send_welcome_for_member(self, member: discord.Member) -> None:
        channel = self._resolve_announcement_channel(member.guild)
        if channel is None:
            self.logger.warning("No writable welcome channel found for guild=%s", member.guild.id)
            return
        script_ids = self.engine.script_ids_with_prefix(self._welcome_prefix)
        if not script_ids:
            self.logger.warning("No welcome scripts loaded.")
            return
        script_id = random.choice(script_ids)
        events = self.engine.render_script_by_id(script_id, str(member.id), member.display_name)
        try:
            await self._send_scripted_events(channel.id, events)
        except Exception:
            self.logger.warning("Failed sending welcome for user=%s guild=%s", member.id, member.guild.id, exc_info=True)

    def _debug_print(self, message: str) -> None:
        if self.config.debug_persona:
            self.logger.debug("[%s] %s", _debug_timestamp(), message)

    def _daily_question_script_id(self) -> str | None:
        script_ids = self.engine.script_ids_with_prefix(self._daily_question_prefix)
        if not script_ids:
            return None
        day_index = date.today().toordinal() % len(script_ids)
        return script_ids[day_index]

    @staticmethod
    def _daily_question_key(guild_id: int, suffix: str) -> str:
        return f"daily_question:{guild_id}:{suffix}"

    def _daily_question_posted_today(self, guild_id: int, today: str | None = None) -> bool:
        return self._current_daily_question_date(guild_id) == (today or _local_now().date().isoformat())

    def _current_daily_question_script_id(self, guild_id: int) -> str | None:
        stored_date = self.memory.get_runtime_value(self._daily_question_key(guild_id, "date"), "")
        today = _local_now().date().isoformat()
        if stored_date != today:
            return None
        stored_script = self.memory.get_runtime_value(self._daily_question_key(guild_id, "script_id"), "")
        return stored_script or None

    def _current_daily_question_date(self, guild_id: int) -> str:
        return self.memory.get_runtime_value(self._daily_question_key(guild_id, "date"), "")

    def _current_daily_question_channel_id(self, guild_id: int) -> int | None:
        return self.memory.get_runtime_value(self._daily_question_key(guild_id, "channel_id"), None)

    def _record_daily_question_state(self, guild_id: int, script_id: str, channel_id: int, today: str | None = None) -> None:
        active_date = today or _local_now().date().isoformat()
        self.memory.set_runtime_value(self._daily_question_key(guild_id, "date"), active_date)
        self.memory.set_runtime_value(self._daily_question_key(guild_id, "script_id"), script_id)
        self.memory.set_runtime_value(self._daily_question_key(guild_id, "channel_id"), channel_id)

    def _daily_question_prompt(self, script_id: str) -> str:
        script = self.content.scripts.get(script_id)
        if script is None:
            return "unknown prompt"
        for step in script.steps:
            text = step.message.strip()
            if "?" in text:
                return text
        for step in script.steps:
            text = step.message.strip()
            if text and "daily question" not in text.lower():
                return text
        return script_id

    def _achievements_for(self, memory) -> list[str]:
        achievements: list[str] = []
        if memory.dramatic_messages >= 5:
            achievements.append("Most Dramatic User")
        if memory.late_night_messages >= 5:
            achievements.append("Night Owl")
        if memory.food_messages >= 4:
            achievements.append("Food War Starter")
        if memory.lia_trust >= 12 and memory.lia_trust >= memory.yuna_trust:
            achievements.append("Lia Favorite")
        if memory.yuna_trust >= 12 and memory.yuna_trust >= memory.lia_trust:
            achievements.append("Yuna Favorite")
        if memory.lia_flirt_tension >= 8 or memory.yuna_flirt_tension >= 8:
            achievements.append("Professional Instigator")
        if not achievements:
            achievements.append("Still mysterious")
        return achievements

    def _next_ambient_at(self) -> datetime:
        stored = self.memory.get_runtime_value("next_ambient_at", "")
        parsed = _parse_iso_datetime(stored)
        now = _utc_now()
        if parsed is None or parsed <= now:
            return self._schedule_next_ambient()
        return parsed

    def _schedule_next_ambient(self) -> datetime:
        now = _utc_now()
        six_hours = 6 * 60 * 60
        current_epoch = int(now.timestamp())
        window_start_epoch = (current_epoch // six_hours) * six_hours
        current_window_start = datetime.fromtimestamp(window_start_epoch, tz=timezone.utc)
        current_window_end = current_window_start + timedelta(seconds=six_hours)
        last_window_value = self.memory.get_runtime_value("last_ambient_window_start", "")
        last_window = _parse_iso_datetime(last_window_value)

        target_window_start = current_window_start
        if last_window is not None and last_window >= current_window_start:
            target_window_start = current_window_end

        target_window_end = target_window_start + timedelta(seconds=six_hours)
        earliest = max(now + timedelta(seconds=5), target_window_start)
        if earliest >= target_window_end:
            target_window_start = target_window_end
            target_window_end = target_window_start + timedelta(seconds=six_hours)
            earliest = target_window_start

        delta_seconds = int((target_window_end - earliest).total_seconds())
        next_at = earliest + timedelta(seconds=random.randint(0, max(0, delta_seconds)))
        self.memory.set_runtime_value("next_ambient_at", next_at.isoformat())
        self.memory.set_runtime_value("next_ambient_window_start", target_window_start.isoformat())
        self._debug_print(f"scheduled next ambient for {next_at.isoformat()}")
        return next_at

    def _next_daily_question_at(self) -> datetime:
        stored = self.memory.get_runtime_value("next_daily_question_at", "")
        parsed = _parse_iso_datetime(stored)
        now = _local_now()
        if parsed is None or parsed <= now:
            return self._schedule_next_daily_question(now)
        return parsed

    def _schedule_next_daily_question(self, now: datetime | None = None) -> datetime:
        now = now or _local_now()
        timezone_info = now.tzinfo

        def random_slot(day: date) -> datetime:
            start = datetime(day.year, day.month, day.day, 10, 0, tzinfo=timezone_info)
            end = datetime(day.year, day.month, day.day, 22, 0, tzinfo=timezone_info)
            effective_start = max(start, now + timedelta(minutes=5))
            if effective_start >= end:
                next_day = day + timedelta(days=1)
                return random_slot(next_day)
            delta_seconds = int((end - effective_start).total_seconds())
            return effective_start + timedelta(seconds=random.randint(0, delta_seconds))

        target_day = now.date()
        next_at = random_slot(target_day)
        self.memory.set_runtime_value("next_daily_question_at", next_at.isoformat())
        self._debug_print(f"scheduled next daily question for {next_at.isoformat()}")
        return next_at

    def _select_daily_question_channels(self) -> dict[int, int]:
        channels = self.memory.all_channels()
        if not channels:
            return {}
        per_guild = {}
        for channel in channels:
            existing = per_guild.get(channel.guild_id)
            if existing is None or channel.last_user_message_at > existing.last_user_message_at:
                per_guild[channel.guild_id] = channel
        return {guild_id: channel.channel_id for guild_id, channel in per_guild.items()}

    @staticmethod
    def _engagement_suggestion(quiet_minutes: int | None) -> str:
        if quiet_minutes is None:
            return "Talk naturally for a bit so the bots can learn the room."
        if quiet_minutes >= 90:
            return "Use `/social_event` to restart the room with a higher-energy prompt."
        if quiet_minutes >= 30:
            return "A daily question should wake the channel up automatically, or you can drop a hot take."
        if quiet_minutes >= 10:
            return "The room is cooling off. A direct mention or playful challenge will probably trigger a scene."
        return "The room is active. Let the bots riff naturally or check `/relationship` for progression."

    async def maybe_prompt_missing_counterpart(self, actor: str, guild: discord.Guild) -> None:
        counterpart = YUNA_SPEAKER if actor == LIA_SPEAKER else LIA_SPEAKER
        notice_key = f"invite_prompt:{actor}:{counterpart}"
        if self.memory.guild_notice_sent(guild.id, notice_key):
            return
        counterpart_bot = self._resolve_bot_for_speaker(counterpart)
        if counterpart_bot is not None and not counterpart_bot.is_ready():
            return
        if self._counterpart_present(counterpart, guild.id):
            return

        channel = self._resolve_announcement_channel(guild)
        if channel is None:
            self._debug_print(f"no writable channel to prompt missing counterpart in guild={guild.id}")
            return

        message = self._missing_counterpart_message(actor)
        if not message:
            return

        try:
            await channel.send(message)
        except Exception as exc:
            self._debug_print(f"failed missing counterpart prompt guild={guild.id}: {exc}")
            return

        self.memory.mark_guild_notice_sent(guild.id, notice_key)
        self._debug_print(f"sent missing counterpart prompt actor={actor} guild={guild.id} channel={channel.id}")

    def _counterpart_present(self, actor: str, guild_id: int) -> bool:
        bot = self._resolve_bot_for_speaker(actor)
        if bot is None:
            return False
        return any(guild.id == guild_id for guild in bot.guilds)

    @staticmethod
    def _resolve_announcement_channel(guild: discord.Guild) -> discord.abc.Messageable | None:
        if guild.me is None:
            return None

        candidates: list[discord.abc.GuildChannel] = []
        if guild.system_channel is not None:
            candidates.append(guild.system_channel)
        if guild.public_updates_channel is not None:
            candidates.append(guild.public_updates_channel)
        candidates.extend(guild.text_channels)

        seen: set[int] = set()
        for channel in candidates:
            if channel.id in seen:
                continue
            seen.add(channel.id)
            permissions = channel.permissions_for(guild.me)
            if permissions.send_messages and permissions.view_channel:
                return channel
        return None

    @staticmethod
    def _missing_counterpart_message(actor: str) -> str:
        if actor == LIA_SPEAKER:
            return (
                "okay wait. this feels wrong without Yuna here.\n"
                f"invite her too so i have someone to argue with properly: {YUNA_INVITE_LINK}"
            )
        if actor == YUNA_SPEAKER:
            return (
                "this arrangement is incomplete. Lia should also be here.\n"
                f"invite her with this link: {LIA_INVITE_LINK}"
            )
        return ""

    @staticmethod
    def _inter_message_delay(previous_actor: str | None, current_actor: str) -> float:
        if previous_actor is None:
            return 0.0
        if previous_actor == current_actor:
            return random.uniform(1.2, 4.0)
        return random.uniform(4.0, 11.0)


class PersonaBot(commands.Bot):
    def __init__(self, persona: PersonaConfig, runtime: DualPersonaRuntime, is_command_host: bool) -> None:
        intents = discord.Intents.default()
        intents.message_content = runtime.config.enable_message_content
        intents.members = True
        super().__init__(command_prefix="!", intents=intents)
        self.persona = persona
        self.runtime = runtime
        self.is_command_host = is_command_host
        self._guild_sync_done = False
        self._commands_registered = False

    async def setup_hook(self) -> None:
        if self.is_command_host:
            self._register_commands_once()

    def _register_commands_once(self) -> None:
        if self._commands_registered:
            return
        self.tree.clear_commands(guild=None)
        register_game_commands(self, self.runtime)
        self._commands_registered = True

    async def on_ready(self) -> None:
        logging.getLogger("yuna_lia.runtime").info("[%s] ready as %s", self.persona.name, self.user)
        for guild in self.guilds:
            await self.runtime.maybe_prompt_missing_counterpart(self.persona.name, guild)
        if self.is_command_host and not self._guild_sync_done:
            self.tree.clear_commands(guild=None)
            await self.tree.sync()
            self._commands_registered = False
            self._register_commands_once()
            for guild in self.guilds:
                try:
                    self.tree.clear_commands(guild=guild)
                    self.tree.copy_global_to(guild=guild)
                    await self.tree.sync(guild=guild)
                except Exception as exc:
                    logging.getLogger("yuna_lia.runtime").warning(
                        "[%s] failed guild sync for %s: %s",
                        self.persona.name,
                        guild.id,
                        exc,
                    )
            self._guild_sync_done = True

    async def on_message(self, message: discord.Message) -> None:
        if self.is_command_host:
            await self.runtime.handle_user_message(message)

    async def on_guild_join(self, guild: discord.Guild) -> None:
        await self.runtime.maybe_prompt_missing_counterpart(self.persona.name, guild)

    async def on_member_join(self, member: discord.Member) -> None:
        if self.is_command_host:
            await self.runtime.send_welcome_for_member(member)

    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent) -> None:
        if self.user is not None and payload.user_id == self.user.id:
            return
        actor = self.runtime.memory.record_bot_message_like(payload.message_id)
        if actor:
            self.runtime._debug_print(
                f"reaction tracked for actor={actor} message_id={payload.message_id} emoji={payload.emoji}"
            )


async def run_bots() -> None:
    config: AppConfig = load_config()
    setup_logging(config.log_level)
    if not config.yuna.token:
        raise RuntimeError("DISCORD_TOKEN_YUNA not set")
    if not config.lia.token:
        raise RuntimeError("DISCORD_TOKEN_LIA not set")

    runtime = DualPersonaRuntime(config)
    yuna_bot = PersonaBot(
        PersonaConfig(name=YUNA_SPEAKER, token=config.yuna.token, mention_aliases=("@yuna", "yuna")),
        runtime,
        True,
    )
    lia_bot = PersonaBot(
        PersonaConfig(name=LIA_SPEAKER, token=config.lia.token, mention_aliases=("@lia", "lia")),
        runtime,
        False,
    )
    runtime.bind_bots(yuna_bot, lia_bot)
    await asyncio.gather(yuna_bot.start(yuna_bot.persona.token), lia_bot.start(lia_bot.persona.token))
