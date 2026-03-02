"""
This module implements tier roll related interactions and command
generation
"""

import random

import discord

from Inglewood.wot_time import get_timestamp
from Inglewood.constants import LOW_TIER_BLOCK_BEFORE, LOW_TIER_BLOCK_AFTER


def tier_roll(client: discord.Client, battle_pass: bool) -> str:
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
    elif client.tier1:
        tiers.remove('I')
    if client.last in tiers:
        tiers.remove(client.last)
        if client.last in tiers:
            tiers.remove(client.last)
    draw = random.choice(tiers)
    client.last = draw
    if draw == 'I':
        client.tier1 = True
    elif draw in ['II','V','VI','VII','VIII'] and random.randint(1, 30) == 1:
        draw += ' Preferential'
    elif draw in ['IV'] and random.randint(1, 30) == 1:
        if random.randint(0, 1) == 1:
            draw += ' Preferential'
        else:
            draw += ' Double Preferential'
    return draw
