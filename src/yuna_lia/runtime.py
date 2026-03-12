from __future__ import annotations

import asyncio
import random
from pathlib import Path
from datetime import datetime

import discord
from discord.ext import commands

from .commands.game_commands import register_game_commands
from .config import AppConfig, PersonaConfig, load_config
from .personas import MemoryStore, PersonaContentStore, PersonaSimulationEngine
from .systems.conversation_pacing import ConversationPacingSystem

YUNA_SPEAKER = "Yuna"
LIA_SPEAKER = "Lia"
LIA_INVITE_LINK = "https://discord.com/oauth2/authorize?client_id=1478877587026739220"
YUNA_INVITE_LINK = "https://discord.com/oauth2/authorize?client_id=1478877501169209424"


def _debug_timestamp() -> str:
    return datetime.now().strftime("%H:%M:%S")


class DualPersonaRuntime:
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.content = PersonaContentStore(config.content_dir)
        self.memory = MemoryStore(config.data_dir / "persona_state.json")
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

    def bind_bots(self, yuna_bot: commands.Bot, lia_bot: commands.Bot) -> None:
        self.yuna_bot = yuna_bot
        self.lia_bot = lia_bot
        self.pacing = ConversationPacingSystem(self._resolve_bot_for_speaker)
        self.content.ensure_loaded()
        self._ambient_task = asyncio.create_task(self._ambient_loop(), name="persona-ambient-loop")

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
            "",
            f"Content root: {self.config.content_dir}",
            "Use `/status` to inspect persona state.",
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
            f"Loaded content files: {status['content_files']}",
            f"Loaded scripts: {status['script_count']}",
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
            f"Messages seen: {stats['messages_seen']}",
            f"Trigger matches found: {stats['trigger_matches']}",
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

    async def handle_user_message(self, message: discord.Message) -> None:
        if message.guild is None or message.author.bot or not message.content.strip():
            return
        self._debug_print(
            f'message guild={message.guild.id} channel={message.channel.id} '
            f'user={message.author.display_name}: "{message.content}"'
        )
        await self._maybe_react(message)
        events = self.engine.handle_message(
            user_id=str(message.author.id),
            display_name=message.author.display_name,
            guild_id=message.guild.id,
            channel_id=message.channel.id,
            content=message.content,
        )
        if not events:
            self._debug_print("no outbound events scheduled")
            return
        if not self.config.persona_test_mode and random.random() < 0.25:
            pause = random.uniform(3.0, 12.0)
            self._debug_print(f"adding pre-send pause of {pause:.1f}s")
            await asyncio.sleep(pause)
        await self._send_scripted_events(message.channel.id, events)

    async def _maybe_react(self, message: discord.Message) -> None:
        lowered = message.content.lower()
        reaction = None
        actor = None
        if any(token in lowered for token in ("lol", "lmao", "💀")):
            actor, reaction = LIA_SPEAKER, "💀"
        elif any(token in lowered for token in ("coffee", "tea")):
            actor, reaction = YUNA_SPEAKER, "☕"
        elif any(token in lowered for token in ("pizza", "pasta", "food")):
            actor, reaction = LIA_SPEAKER, "🍝"
        elif any(token in lowered for token in ("lie", "cap", "dishonest")):
            actor, reaction = YUNA_SPEAKER, "👀"
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
                return
        try:
            target = await channel.fetch_message(message.id)
            await target.add_reaction(reaction)
        except Exception:
            return

    async def _ambient_loop(self) -> None:
        while True:
            await asyncio.sleep(random.randint(self.config.ambient_min_seconds, self.config.ambient_max_seconds))
            if self.yuna_bot is None:
                continue
            for channel_state in self.memory.all_channels()[-12:]:
                events = self.engine.maybe_ambient_event(
                    guild_id=channel_state.guild_id,
                    channel_id=channel_state.channel_id,
                )
                try:
                    await self._send_scripted_events(channel_state.channel_id, events)
                except Exception:
                    continue

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

    def _debug_print(self, message: str) -> None:
        if self.config.debug_persona:
            print(f"[{_debug_timestamp()}] [runtime] {message}")

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

        channel = self._resolve_announcement_channel(actor, guild)
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

    def _resolve_announcement_channel(
        self,
        actor: str,
        guild: discord.Guild,
    ) -> discord.abc.Messageable | None:
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
        print(f"[{self.persona.name}] ready as {self.user}")
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
                    print(f"[{self.persona.name}] failed guild sync for {guild.id}: {exc}")
            self._guild_sync_done = True

    async def on_message(self, message: discord.Message) -> None:
        if self.is_command_host:
            await self.runtime.handle_user_message(message)

    async def on_guild_join(self, guild: discord.Guild) -> None:
        await self.runtime.maybe_prompt_missing_counterpart(self.persona.name, guild)

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
