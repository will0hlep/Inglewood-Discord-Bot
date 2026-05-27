"""
This module implements the inglewood discord bot.
"""

import os
import sys

import discord
from discord.ext import commands

from constants import CONSTANTS

class Inglewood(commands.Bot):
    """
    Represents a Discord bot.
    """
    def __init__(self):
        super().__init__("/",intents=discord.Intents.all())
        self.guild=discord.Object(CONSTANTS["server_id"])

        @self.tree.command(name="restart", guild=self.guild)
        async def restart(interaction: discord.Interaction) -> None:
            await interaction.response.defer()
            if await self.is_owner(interaction.user):
                await self.cogs["Helper"].respond("Restarting...", interaction)
                os.execv(sys.executable, 'python main.py')
            else:
                await self.cogs["Helper"].respond(
                    f"{interaction.user} attempted restricted command",
                    interaction)

    async def setup_hook(self) -> None:
        """     
        Performs asynchronous setup after the bot is logged in but
        before it has connected to the Websocket.
        """
        await self.load_extension("cogs.helper")
        await self.cogs["Helper"].hashcheck()


class Cog(commands.Cog):
    """
    Represents the a Discord cog.
    """
    def __init__(self, bot: Inglewood):
        self.bot = bot


def main():
    """
    Creates and runs the Inglewood Discord bot.
    """
    Inglewood().run(CONSTANTS["token"])


if __name__ == "__main__":
    main()
