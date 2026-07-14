"""
Implements commands for managing World of Tanks related commands.
"""

from datetime import datetime
import random

import discord
from discord.ext import tasks

from constants import CONSTANTS as CONST
from inglewood import Cog, Inglewood

cutoff_start = CONST["low_tier_block_start"].replace(tzinfo=CONST["time_zone"])
cutoff_end = CONST["low_tier_block_end"].replace(tzinfo=CONST["time_zone"])
reset_time = CONST["daily_tier_reset_time"].replace(tzinfo=CONST["time_zone"])


class WorldofTanks(Cog):
    """
    Represents a cog that adds commands for managing World of Tanks
    related commands.
    """
    def __init__(self, bot: Inglewood):
        super().__init__(bot)
        self.last = None
        self.tier1 = False
        self.random_tiers_command_generator(
            "random_tiers_all", "Roll a random tier", False)
        self.random_tiers_command_generator(
            "random_tiers_iv_plus", "Roll a random tier (IV+)", True)
        self.daily_tier_roll_reset.start()

    @tasks.loop(time=reset_time)
    async def daily_tier_roll_reset(self) -> None:
        """
        Performs a daily reset of the tier roll mechanics at
        daily_tier_reset_time each day.
        """
        self.last = None
        self.tier1 = False
        await self.bot.cogs["Helper"].respond(
            "reset daily tier roll variables")
  
    def cutoff_check(self):
        """
        Checks if the current time is within the low tier block period.
        """
        now = datetime.now(CONST["time_zone"]).time()
        if cutoff_start <= cutoff_end:
            return cutoff_start <= now < cutoff_end
        else:
            return now >= cutoff_start or now < cutoff_end

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
        @self.bot.tree.command(
            name=command_name, guild=self.bot.guild,
            description=command_description)
        async def func(interaction: discord.Interaction) -> None:
            await interaction.response.defer()
            tiers = {
                "Wildcard": 2, "I": 1, "II": 1, "III": 1, "IV": 1, "V": 2,
                "VI": 2, "VII": 2, "VIII": 2, "IX": 2, "X": 2, "XI": 2
            }
            if battle_pass or self.cutoff_check():
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
                if draw in ["IV"] and random.random() < 1/2:
                    draw += " Double"
                draw += " Preferential"
            await self.bot.cogs["Helper"].respond(draw, interaction)
        func.__name__ = command_name

    async def cog_unload(self):
        """
        Terminates all looping tasks when unloading this cog.
        """
        self.daily_tier_roll_reset.cancel()


async def setup(bot: Inglewood) -> None:
    """
    The entry point to load this extention.

    Parameter:
        bot : Inglewood
            The bot that loads this extension.
    """
    await bot.add_cog(WorldofTanks(bot))
