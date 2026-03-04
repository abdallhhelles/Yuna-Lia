from __future__ import annotations

import asyncio
import random

import discord
from discord.ext import commands

from .config import LIA, YUNA, load_config
from .llm import generate_reply
from .logging_store import LogStore
from .memory import LongTermMemory, ShortTermMemory
from .mood import MoodState, mood_label, update_mood_from_message
from .premium import load_premium_triggers
from .scenarios import ScenarioLibrary
from .typing_sim import typing_time_seconds


class DualBotBrain:
    def __init__(self) -> None:
        self.config = load_config()
        self.short_memory = ShortTermMemory(max_messages=20)
        self.long_memory = LongTermMemory(
            inside_jokes=["April prank disaster", "Roast me challenge", "Hallway trip"]
        )
        self.moods = {YUNA.name: MoodState(), LIA.name: MoodState()}
        self.logs = LogStore(self.config.db_path)

        self.scenarios = ScenarioLibrary(self.config.base_dir / "scenarios" / "free" / "scenarios.json")
        self.scenarios.load()
        self.premium_triggers = load_premium_triggers(self.config.premium_trigger_file)

    def premium_enabled(self) -> bool:
        return len(self.premium_triggers) > 0

    def detect_trigger(self, content: str) -> str:
        txt = content.lower()
        if "/debate" in txt:
            return "debate"
        if any(k in txt for k in ["prank", "meme", "roast"]):
            return "prank"
        return "general"

    async def compose(self, bot_name: str, user_content: str) -> tuple[str, int | None]:
        mood = update_mood_from_message(self.moods[bot_name], user_content)
        label = mood_label(mood)
        trigger = self.detect_trigger(user_content)
        sc = self.scenarios.choose(bot=bot_name, mood=label, trigger=trigger, premium_enabled=self.premium_enabled())

        if sc:
            base_line = sc.text
            scenario_id = sc.scenario_id
        else:
            base_line = f"{bot_name} has no scenario for this moment, improv time."
            scenario_id = None

        memory_hint = ", ".join(self.long_memory.inside_jokes[:2])
        prompt = (
            f"You are {bot_name}. Keep a playful friend-to-friend tone and avoid hateful slurs. "
            f"Mood={label}. Trigger={trigger}. Inside-jokes={memory_hint}. "
            f"Base line: {base_line}. User said: {user_content}."
        )

        llm_text = await generate_reply(self.config.ollama_url, self.config.ollama_model, prompt)
        final_text = llm_text.strip() or base_line
        return final_text, scenario_id


intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
brain = DualBotBrain()


@bot.event
async def on_ready() -> None:
    print(f"Logged in as {bot.user}")


@bot.event
async def on_guild_join(guild: discord.Guild) -> None:
    brain.logs.log_server_event("join", str(guild.id), guild.name)


@bot.event
async def on_guild_remove(guild: discord.Guild) -> None:
    brain.logs.log_server_event("leave", str(guild.id), guild.name)


@bot.event
async def on_message(message: discord.Message) -> None:
    if message.author.bot:
        return

    content = message.content
    brain.short_memory.add(author=str(message.author), content=content)
    brain.logs.log_message(channel_id=str(message.channel.id), author=str(message.author), content=content)

    selected = None
    if YUNA.mention.lower() in content.lower() or "yuna" in content.lower():
        selected = YUNA.name
    elif LIA.mention.lower() in content.lower() or "lia" in content.lower():
        selected = LIA.name
    elif random.random() < 0.07:
        selected = random.choice([YUNA.name, LIA.name])

    if selected:
        reply, scenario_id = await brain.compose(selected, content)
        t = typing_time_seconds(selected, reply, brain.moods[selected], device="desktop")
        async with message.channel.typing():
            await asyncio.sleep(min(t, 8.0))
        await message.reply(reply)
        brain.logs.log_message(
            channel_id=str(message.channel.id),
            author=str(bot.user),
            content=reply,
            bot=selected,
            scenario_id=scenario_id,
        )

    await bot.process_commands(message)


def run() -> None:
    token = brain.config.discord_token
    if not token:
        raise RuntimeError("DISCORD_BOT_TOKEN not set")
    bot.run(token)


if __name__ == "__main__":
    run()
