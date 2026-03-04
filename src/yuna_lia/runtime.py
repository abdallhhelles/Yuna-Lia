from __future__ import annotations

import asyncio
import random

import discord
from discord.ext import commands

from .config import AppConfig, PersonaConfig, load_config
from .llm import generate_reply
from .logging_store import LogStore
from .lore import LoreStore
from .memory import LongTermMemory, ShortTermMemory
from .mood import MoodState, mood_label, update_mood_from_message
from .premium import load_premium_triggers
from .scenarios import ScenarioLibrary
from .typing_sim import typing_time_seconds


class SharedBrain:
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.logs = LogStore(config.db_path)
        self.short_memory = {"Yuna": ShortTermMemory(max_messages=20), "Lia": ShortTermMemory(max_messages=20)}
        self.long_memory = {
            "Yuna": LongTermMemory(),
            "Lia": LongTermMemory(),
        }
        self.moods = {"Yuna": MoodState(), "Lia": MoodState()}

        self.scenarios = ScenarioLibrary(config.base_dir / "scenarios" / "free" / "scenarios.json")
        self.scenarios.load()

        self.lore = LoreStore(config.base_dir / "scenarios" / "meta")
        self.lore.load()

        self.premium_triggers = load_premium_triggers(config.premium_trigger_file)
        for name in ("Yuna", "Lia"):
            for joke in self.lore.persona(name).inside_jokes:
                self.long_memory[name].remember_joke(joke)
            for event in self.lore.shared().memorable_events:
                self.long_memory[name].remember_event(event)

    def premium_enabled(self) -> bool:
        return bool(self.premium_triggers)

    @staticmethod
    def detect_trigger(content: str) -> str:
        txt = content.lower()
        if "/debate" in txt:
            return "debate"
        if any(k in txt for k in ["prank", "meme", "roast"]):
            return "prank"
        return "general"

    async def compose(self, persona_name: str, user_content: str) -> tuple[str, int | None]:
        mood = update_mood_from_message(self.moods[persona_name], user_content)
        label = mood_label(mood)
        trigger = self.detect_trigger(user_content)
        scenario = self.scenarios.choose(
            bot=persona_name,
            mood=label,
            trigger=trigger,
            premium_enabled=self.premium_enabled(),
        )

        base_line = scenario.text if scenario else f"{persona_name} pauses, thinking of a better comeback."
        scenario_id = scenario.scenario_id if scenario else None
        lore = self.lore.persona(persona_name)

        prompt = (
            f"You are {persona_name}, age {lore.age}, occupation: {lore.occupation}. "
            f"Personality traits: {', '.join(lore.personality[:5])}. "
            f"Communication style: {', '.join(lore.communication_style[:4])}. "
            f"Inside jokes with friends: {', '.join(lore.inside_jokes[:3])}. "
            f"Mood state label={label}, trigger={trigger}. "
            f"Reply naturally, vivid, and in-character; avoid hateful slurs. "
            f"Anchor line: {base_line}. User said: {user_content}."
        )

        llm_text = await generate_reply(self.config.ollama_url, self.config.ollama_model, prompt)
        return (llm_text.strip() or base_line), scenario_id


class PersonaBot(commands.Bot):
    def __init__(self, persona: PersonaConfig, brain: SharedBrain) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)
        self.persona = persona
        self.brain = brain

    async def on_ready(self) -> None:
        print(f"[{self.persona.name}] ready as {self.user}")

    async def on_guild_join(self, guild: discord.Guild) -> None:
        self.brain.logs.log_server_event(f"join:{self.persona.name}", str(guild.id), guild.name)

    async def on_guild_remove(self, guild: discord.Guild) -> None:
        self.brain.logs.log_server_event(f"leave:{self.persona.name}", str(guild.id), guild.name)

    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return

        content = message.content
        self.brain.short_memory[self.persona.name].add(author=str(message.author), content=content)
        self.brain.logs.log_message(channel_id=str(message.channel.id), author=str(message.author), content=content)

        content_lower = content.lower()
        targeted = any(alias in content_lower for alias in self.persona.mention_aliases)
        targeted = targeted or (self.user is not None and self.user.mentioned_in(message))
        spontaneous = random.random() < 0.06

        if targeted or spontaneous:
            reply, scenario_id = await self.brain.compose(self.persona.name, content)
            delay = typing_time_seconds(self.persona.name, reply, self.brain.moods[self.persona.name], device="desktop")
            async with message.channel.typing():
                await asyncio.sleep(min(delay, 8.0))

            await message.reply(reply)
            self.brain.logs.log_message(
                channel_id=str(message.channel.id),
                author=str(self.user),
                content=reply,
                bot=self.persona.name,
                scenario_id=scenario_id,
            )

        await self.process_commands(message)


async def run_bots() -> None:
    config = load_config()
    if not config.yuna.token:
        raise RuntimeError("DISCORD_TOKEN_YUNA not set")
    if not config.lia.token:
        raise RuntimeError("DISCORD_TOKEN_LIA not set")

    brain = SharedBrain(config)
    yuna_bot = PersonaBot(config.yuna, brain)
    lia_bot = PersonaBot(config.lia, brain)

    await asyncio.gather(yuna_bot.start(config.yuna.token), lia_bot.start(config.lia.token))
