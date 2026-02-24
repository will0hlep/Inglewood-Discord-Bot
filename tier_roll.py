"""
This module implements tier roll related interactions and command
generation
"""

import random
from collections.abc import Callable

import discord

from wot_time import get_timestamp
from constants import (SERVER_ID, LOW_TIER_BLOCK_BEFORE, LOW_TIER_BLOCK_AFTER)


def tier_roll(battle_pass: bool, values: object) -> str:
    """
    Chooses a random tier (from I to XI or Wildcard) without repeats.
    Tier I will only be selected at most once per day. Tier I to III
    will only be selected if not battle_pass and if the time is between
    LOW_TIER_BLOCK_BEFORE and LOW_TIER_BLOCK_AFTER.

    When tiers II, IV, V, VI, VII, and VIII are selected there is a
    chance to roll preferential. When tier IV is selected there is a
    chance to roll double preferential.

    Parameters:
        guild : object
            represents a Discord guild (server)
        user : object
            represents a Discord user
        role_name: str
            the name of the role to be assigned or removed from the user
        allow_remove: bool
            sets if removing roles is allowed
    
    Returns:
        draw : str
            interaction response
    """
    tiers = ['I','II','III','IV',
             'V','VI','VII','VIII','IX','X','XI','Wildcard',
             'V','VI','VII','VIII','IX','X','XI','Wildcard']
    timestamp = get_timestamp()
    if (battle_pass or timestamp > LOW_TIER_BLOCK_AFTER
        or timestamp < LOW_TIER_BLOCK_BEFORE):
        tiers.remove('I')
        tiers.remove('II')
        tiers.remove('III')
    elif values.tier1:
        tiers.remove('I')
    if values.last in tiers:
        tiers.remove(values.last)
        if values.last in tiers:
            tiers.remove(values.last)
    draw = random.choice(tiers)
    values.last = draw
    if draw == 'I':
        values.tier1 = True
    elif draw in ['II','V','VI','VII','VIII'] and random.randint(1, 30) == 1:
        draw += ' Preferential'
    elif draw in ['IV'] and random.randint(1, 30) == 1:
        if random.randint(0, 1) == 1:
            draw += ' Preferential'
        else:
            draw += ' Double Preferential'
    return draw


def random_tiers_command_generator(
        command_name: str, command_description: str, battle_pass: bool,
        tree: object, values: object) -> Callable:
    """
    Builds discord commands to allow users to role random tiers.

    Parameters:
        command_name : str
            the name of the command as it will appear in Discord
        command_description : str
            the description of the command as it will appear in Discord
        battle_pass: bool
            if True, command will only select from tier IV and up
        tree: object
            The command tree responsible for handling the application
            commands in this bot
    """
    @tree.command(
            name = command_name, description = command_description,
            guild=discord.Object(id=SERVER_ID))
    @discord.app_commands.describe()
    async def func(interaction: object) -> None:
        await interaction.response.defer()
        draw = tier_roll(battle_pass, values)
        await interaction.followup.send(draw)
        print(f"{command_name} command rolled {draw} for "
              f"{interaction.user.name}")
        return None
    return None
