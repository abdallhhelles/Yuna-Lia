from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands


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
