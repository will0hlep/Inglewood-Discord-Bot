"""
Implements commands for managing cogs.
"""

from collections.abc import Callable

import discord
from discord.ext import commands


class CogControl(commands.Cog):
    """
    Represents a cog that adds commands for managing cogs.
    """
    def __init__(self, bot):
        self.bot = bot
        self.required = True
        self.cog_control_command_generator("", self.bot.load_extension)
        self.cog_control_command_generator("re", self.bot.reload_extension)
        self.cog_control_command_generator("un", self.bot.unload_extension)

    def cog_control_command_generator(
            self, prefix: str, function: Callable[[str, str], None]) -> None:
        """
        Builds discord commands to allow the loading and reloading of
        cogs.

        Parameters:
            prefix : str
                modifier for the command name
            function: Callable[[str, str], None]
                function to be applied to cog
        """
        @self.bot.tree.command(
            name=f"{prefix}load_cog", guild=self.bot.guild)
        async def func(
            interaction: discord.Interaction, cog: str) -> None:
            await interaction.response.defer()
            if await self.bot.is_owner(interaction.user):
                if prefix == "un" and self.bot.cogs[cog].required:
                    await self.bot.cogs["Helper"].respond(
                    f"{cog} cannot be unloaded", interaction)
                else:
                    try:
                        await function(f"cogs.{cog}")
                        await self.bot.cogs["Helper"].hashcheck(False)
                        await self.bot.cogs["Helper"].respond(
                            f"{cog} cog {prefix}loaded", interaction)
                    except (commands.ExtensionNotLoaded,
                            commands.ExtensionNotFound,
                            commands.NoEntryPointError,
                            commands.ExtensionFailed) as e:
                        await self.bot.cogs["Helper"].respond(
                            f"Extension not {prefix}loaded: {e}",
                            interaction)
            else:
                await self.bot.cogs["Helper"].respond(
                    f"{interaction.user} attempted restricted command",
                    interaction)
        func.__name__ = f"{prefix}load_cog"


async def setup(bot: commands.bot) -> None:
    """
    The entry point to load this extention.

    Parameter:
        bot : commands.bot
            The bot that loads this extension.
    """
    await bot.add_cog(CogControl(bot))
