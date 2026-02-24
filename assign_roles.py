"""
This module implements role related interactions and command
generation.
"""

from collections.abc import Callable

import discord

from constants import USER_ID, SERVER_ID


async def toggle_role(
        guild: object, user: object, role_name: str,
        allow_remove: bool) -> tuple[bool, str]:
    """
    Assigns or removes role_name from user in guild.

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
        discord_string : str
            interaction response
        console_string : str
            console output
    """
    role = discord.utils.get(guild.roles, name=role_name)
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
    return discord_string, console_string


async def toggle_role_message_send(
        interaction: object, user: object, role_name: str,
        allow_remove: bool) -> None:
    """
    Calls toggle_role and handles interaction response and console
    output.

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
    discord_string, console_string = await toggle_role(
        interaction.guild, user, role_name, allow_remove)
    print(console_string)
    await interaction.followup.send(discord_string)
    return None


def toggle_role_command_generator(
        command_name: str, role_name: str, tree: object) -> Callable:
    """
    Builds discord commands to allow users to toggle roles.

    Parameters:
        command_name : str
            the name of the command as it will appear in Discord
        role_name: str
            the name of the role to be assigned or removed from the user
        tree: object
            The command tree responsible for handling the application
            commands in this bot
    """
    @tree.command(
        name = command_name, description = f"Toggle {role_name} role.",
        guild = discord.Object(id=SERVER_ID))
    @discord.app_commands.describe()
    async def func(interaction: object):
        await interaction.response.defer()
        await toggle_role_message_send(
            interaction, interaction.user, role_name, True)
        return None
    return None


def assign_role_command_generator(
        command_name: str, required_role: str, role_name: str,
        tree: object) -> Callable:
    """
    Builds discord commands to allow users to assign roles to other
    users.

    Parameters:
        command_name : str
            the name of the command as it will appear in Discord
        required_role : str
            the name of the role the user requires to assign role_name
        role_name: str
            the name of the role to be assigned to the targeted user
        tree: object
            The command tree responsible for handling the application
            commands in this bot
    """
    @tree.command(name = command_name,
                  description = f"Assign {role_name} role.",
                  guild=discord.Object(id=SERVER_ID))
    @discord.app_commands.describe(
        username = (
            f"The user you want to assign the {role_name} role to (case"
            " sensitive)."))
    async def func(interaction: object, username: str):
        await interaction.response.defer()
        role = discord.utils.get(interaction.guild.roles, name=required_role)
        if role in interaction.user.roles:
            user = interaction.guild.get_member_named(username)
            await toggle_role_message_send(interaction, user, role_name, False)
        else:
            print(f'you do not have permission to assign the {role_name} role')
            await interaction.followup.send((
                f"{interaction.user.name} does not have permission to assign "
                f"the {role_name} role"))
        return None
    return None
