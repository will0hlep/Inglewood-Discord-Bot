"""
Implements commands for managing World of Tanks related commands.
"""

import datetime
import random

import discord
from discord.ext import commands, tasks

from constants import CONSTANTS
from helper import respond


class WorldofTanks(commands.Cog):
    """
    Represents a cog that add commands for managing World of Tanks
    related commands.
    """
    def __init__(self, bot):
        self.bot = bot
        self.last = None
        self.tier1 = False
        self.random_tiers_command_generator(
            "random_tiers_all", "Roll a random tier", False)
        self.random_tiers_command_generator(
            "random_tiers_iv_plus", "Roll a random tier (IV+)", True)
        self.daily_tier_roll_reset.start()

    reset_time = CONSTANTS["daily_tier_reset_time"]
    reset_time = reset_time.replace(tzinfo=CONSTANTS["time_zone"])
    @tasks.loop(time=reset_time)
    async def daily_tier_roll_reset(self) -> None:
        """
        Performs a daily reset of the tier roll mechanics at
        daily_tier_reset_time each day.
        """
        self.last = None
        self.tier1 = False
        await respond("reset daily tier roll variables")

    async def cog_unload(self):
        """
        Terminates all looping tasks when unloading this cog.
        """
        self.daily_tier_roll_reset.cancel()

    def random_tiers_command_generator(
            self, command_name: str, command_description: str,
            battle_pass: bool) -> None:
        """
        Builds discord commands to allow users to role random tiers.

        Parameters:
            command_name : str
                the name of the command as it will appear in Discord
            command_description : str
                the description of the command as it will appear in
                Discord
            battle_pass: bool
                if True, command will only select from tier IV and up
        """
        late_cutoff = CONSTANTS["low_tier_block_after"]
        late_cutoff = late_cutoff.replace(tzinfo=CONSTANTS["time_zone"])
        early_cutoff = CONSTANTS["low_tier_block_after"]
        early_cutoff = early_cutoff.replace(tzinfo=CONSTANTS["time_zone"])
        @self.bot.tree.command(
            name=command_name, guild=self.bot.guild,
            description=command_description)
        async def func(interaction: discord.Interaction) -> None:
            await interaction.response.defer()
            tiers = {
                "Wildcard": 2, "I": 1, "II": 1, "III": 1, "IV": 1, "V": 2,
                "VI": 2, "VII": 2, "VIII": 2, "IX": 2, "X": 2, "XI": 2
            }
            now = datetime.datetime.now(CONSTANTS["time_zone"]).time()
            if battle_pass or now > late_cutoff or now < early_cutoff:
                tiers.update({"I": 0, "II": 0, "III": 0})
            elif self.tier1:
                tiers["I"] = 0
            tiers[self.last] = 0
            draw = random.choices(list(tiers.keys()), list(tiers.values()))[0]
            self.last = draw
            if draw == "I":
                self.tier1 = True
            elif (draw in ["II", "IV", "V", "VI", "VII", "VIII"]
                    and random.random() < 1/30):
                if draw == "IV" and random.random() < 1/2:
                    draw += " Double"
                draw += " Preferential"
            await respond(draw, interaction)
        func.__name__ = command_name


async def setup(bot: commands.bot) -> None:
    """
    The entry point to load this extention.

    Parameter:
        bot : commands.bot
            The bot that loads this extension.
    """
    await bot.add_cog(WorldofTanks(bot))
