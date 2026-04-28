"""
Implements widely used helper functions.
"""

import hashlib
import json
import os
import pathlib

import discord
from discord.ext import commands


async def respond(msg: str, interaction: discord.Interaction = None) -> None:
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
        print(msg)
    except discord.HTTPException as e:
        print(f"HTTP error: {e}")


async def hashcheck(bot: commands.Bot, load: bool = True) -> None:
    """
    Checks for any changes in the python scripts and, if any are found,
    updates "hash_dict.json" and syncs the commandtree.

    Parameters:
        bot: commands.bot
            The bot whose commandtree is being synced
        load: bool
            If true, load any cogs found
    """
    if os.path.exists("hash_dict.json"):
        with open("hash_dict.json", "r", encoding="utf-8") as f:
            last_hash = json.load(f)
    else:
        last_hash = None
    current_hash = {}
    for path in [".", "./cogs"]:
        for file in os.listdir(path):
            if pathlib.PurePosixPath(file).suffix == ".py":
                with open(os.path.join(path,file), "rb") as file_to_hash:
                    data_to_hash = file_to_hash.read()
                    md5_returned = hashlib.md5(data_to_hash).hexdigest()
                    current_hash[os.path.join(path,file)] = md5_returned
                if load and path == "./cogs":
                    await bot.load_extension(f"cogs.{file[:-3]}")
    if current_hash != last_hash:
        with open("hash_dict.json", "w", encoding="utf-8") as f:
            json.dump(current_hash, f)
        await bot.tree.sync(guild = bot.guild)
        await respond("command tree updated")
