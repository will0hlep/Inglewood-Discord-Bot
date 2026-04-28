"""
This module implements the inglewood discord bot.
"""

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

    async def setup_hook(self) -> None:
        """     
        Performs asynchronous setup after the bot is logged in but
        before it has connected to the Websocket.
        """
        await self.load_extension("cogs.helper")
        await self.cogs["Helper"].hashcheck()


def main():
    """
    Creates and runs the Inglewood Discord bot.
    """
    Inglewood().run(CONSTANTS["token"])


if __name__ == "__main__":
    main()
