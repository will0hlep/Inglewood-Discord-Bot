"""
Implements helper functions.
"""

from hashlib import sha3_512
import json
import os
import pathlib

import discord

from inglewood import Cog, Inglewood


class Helper(Cog):
    """
    Represents a cog that adds helper functions for use in all other
    scripts.
    """
    async def hashcheck(self, load: bool = True) -> None:
        """
        Checks for any changes in the python scripts and, if any are found,
        updates "hash_dict.json" and syncs the commandtree.

        Parameters:
            load: bool
                If true, load any cogs found
        """
        if os.path.exists("hash_dict.json"):
            with open("hash_dict.json", "r", encoding="utf-8") as f:
                last_hash = json.load(f)
        else:
            last_hash = None
        live_hash = {}
        for path in [".", "./cogs"]:
            for file in os.listdir(path):
                if pathlib.PurePosixPath(file).suffix == ".py":
                    filepath = os.path.join(path,file)
                    with open(filepath, "rb") as f:
                        live_hash[filepath] = sha3_512(f.read()).hexdigest()
                    if load and path == "./cogs" and file != "helper.py":
                        await self.bot.load_extension(f"cogs.{file[:-3]}")
        if live_hash != last_hash:
            with open("hash_dict.json", "w", encoding="utf-8") as f:
                json.dump(live_hash, f)
            await self.bot.tree.sync(guild = self.bot.guild)
            await self.respond("command tree updated")

    async def respond(
            self, msg: str, interaction: discord.Interaction = None) -> None:
        """
        Outputs to console and discord.

        Parameters:
            msg : str
                The string to be output
            interaction: discord.Interaction
                The discord interaction to respond to
        """
        try:
            if interaction is not None:
                await interaction.followup.send(msg)
        except discord.HTTPException as e:
            print(f"HTTP error: {e}")
        else:
            print(msg)


async def setup(bot: Inglewood) -> None:
    """
    The entry point to load this extention.

    Parameter:
        bot : Inglewood
            The bot that loads this extension.
    """
    await bot.add_cog(Helper(bot))
