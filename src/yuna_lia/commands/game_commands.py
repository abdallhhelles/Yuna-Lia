from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands


class BirthdayModal(discord.ui.Modal, title="Save your birthday"):
    birthday = discord.ui.TextInput(
        label="Birthday",
        placeholder="YYYY-MM-DD",
        min_length=10,
        max_length=10,
    )

    def __init__(self, runtime: object) -> None:
        super().__init__()
        self.runtime = runtime

    async def on_submit(self, interaction: discord.Interaction) -> None:
        try:
            await self.runtime.command_birthday(interaction, str(self.birthday))
        except ValueError as exc:
            await interaction.response.send_message(str(exc), ephemeral=True)


class DailyAnswerModal(discord.ui.Modal, title="Private daily answer"):
    answer = discord.ui.TextInput(
        label="Your answer",
        style=discord.TextStyle.paragraph,
        placeholder="Write your answer here",
        min_length=2,
        max_length=400,
    )

    def __init__(self, runtime: object) -> None:
        super().__init__()
        self.runtime = runtime

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await self.runtime.command_answer(interaction, str(self.answer))


def register_game_commands(bot: commands.Bot, runtime: object) -> None:
    @bot.tree.command(name="about", description="Explain Lia and Yuna's simulation system")
    async def about(interaction) -> None:
        await runtime.command_about(interaction)

    @bot.tree.command(name="status", description="Show persona moods, activity, and loaded content state")
    async def status(interaction) -> None:
        await runtime.command_status(interaction)

    @bot.tree.command(name="stats", description="Show fun simulation stats and trigger discovery leaders")
    async def stats(interaction) -> None:
        await runtime.command_stats(interaction)

    @bot.tree.command(name="memory", description="Inspect tracked memory for a user")
    @app_commands.describe(user="User to inspect")
    async def memory(interaction: discord.Interaction, user: discord.Member | discord.User) -> None:
        await runtime.command_memory(interaction, user)

    @bot.tree.command(name="reload_personas", description="Reload trigger and script files from disk")
    async def reload_personas(interaction) -> None:
        await runtime.command_reload(interaction)

    @bot.tree.command(name="birthday", description="Privately save your birthday for future features")
    async def birthday(interaction: discord.Interaction) -> None:
        await interaction.response.send_modal(BirthdayModal(runtime))

    @bot.tree.command(name="answer", description="Submit a private answer to today's daily question")
    async def answer(interaction: discord.Interaction) -> None:
        await interaction.response.send_modal(DailyAnswerModal(runtime))

    @bot.tree.command(name="relationship", description="Inspect your relationship progression with Lia and Yuna")
    @app_commands.describe(user="Optional user to inspect")
    async def relationship(
        interaction: discord.Interaction,
        user: discord.Member | discord.User | None = None,
    ) -> None:
        await runtime.command_relationship(interaction, user)

    @bot.tree.command(name="achievements", description="Show passive activity achievements")
    @app_commands.describe(user="Optional user to inspect")
    async def achievements(
        interaction: discord.Interaction,
        user: discord.Member | discord.User | None = None,
    ) -> None:
        await runtime.command_achievements(interaction, user)

    @bot.tree.command(name="social_event", description="Start a shared social event for the room")
    @app_commands.describe(category="Type of social event to drop into chat")
    @app_commands.choices(
        category=[
            app_commands.Choice(name="Pick A Side", value="pick_a_side"),
            app_commands.Choice(name="Mini Poll", value="mini_poll"),
            app_commands.Choice(name="Hot Take", value="hot_take"),
            app_commands.Choice(name="Confession", value="confession"),
            app_commands.Choice(name="Late Night", value="late_night"),
        ]
    )
    async def social_event(interaction: discord.Interaction, category: app_commands.Choice[str]) -> None:
        await runtime.command_social_event(interaction, category.value)

    @bot.tree.command(name="roompulse", description="Show channel activity, mood, and an engagement suggestion")
    async def roompulse(interaction: discord.Interaction) -> None:
        await runtime.command_roompulse(interaction)

    @bot.tree.command(name="level", description="Show your slow-burn server level progress")
    @app_commands.describe(user="Optional user to inspect")
    async def level(interaction: discord.Interaction, user: discord.Member | discord.User | None = None) -> None:
        await runtime.command_level(interaction, user)

    @bot.tree.command(name="leaderboard", description="Show the server level leaderboard")
    async def leaderboard(interaction: discord.Interaction) -> None:
        await runtime.command_leaderboard(interaction)
