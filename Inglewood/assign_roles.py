"""
This module implements role related interactions and command
generation.
"""

import discord

from Inglewood.constants import USER_ID


async def toggle_role(
        interaction: object, user: object, role_name: str,
        allow_remove: bool) -> tuple[bool, str]:
    """
    Assigns or removes role_name from user in guild and handles
    interaction response and console output.

    Parameters:
        interaction : object
            represents a Discord interaction
        user : object
            represents a Discord user
        role_name: str
            the name of the role to be assigned or removed from the user
        allow_remove: bool
            sets if removing roles is allowed
    """
    role = discord.utils.get(interaction.guild.roles, name=role_name)
    if role not in user.roles:
        try:
            await user.add_roles(role)
            discord_string = f"{role_name} role added"
            console_string = f"{role_name} role added to {user.name}"
        except discord.HTTPException:
            discord_string = (
                f"couldn't assign the {role_name} role to {user.name}, <@"
                f"{USER_ID}>")
            console_string = (
                f"couldn't assign the {role_name} role to {user.name}")
    elif allow_remove:
        try:
            await user.remove_roles(role)
            discord_string = f"{role_name} role removed"
            console_string = f"{role_name} role removed from {user.name}"
        except discord.HTTPException:
            discord_string = (
                f"couldn't remove the {role_name} role from {user.name}, <@"
                f"{USER_ID}>")
            console_string = (
                f"couldn't remove the {role_name} role from {user.name}")
    else:
        discord_string = f"{user.name} already has {role_name} role"
        console_string = f"{user.name} already has {role_name} role"
    print(console_string)
    await interaction.followup.send(discord_string)
