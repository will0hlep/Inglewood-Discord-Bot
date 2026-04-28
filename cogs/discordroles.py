"""
Implements commands for managing discord roles
"""

import discord
from discord.ext import commands

from constants import CONSTANTS


class DiscordRoles(commands.Cog):
    """
    Represents a cog that adds commands for managing discord roles.
    """
    def __init__(self, bot):
        self.bot = bot
        for command, role in CONSTANTS["toggle_roles"].items():
            self.toggle_role_command_generator(command, role)
        for command, role in CONSTANTS["assign_roles"].items():
            self.assign_role_command_generator(command, role[0], role[1])

    async def toggle_role(
        self, interaction: discord.Interaction, user: discord.Member,
        role_name: str, allow_remove: bool) -> None:
        """
        Assigns or removes role_name from user in guild and handles
        interaction response and console output.

        Parameters:
            interaction : discord.Interaction
                represents a Discord interaction
            user : discord.Member
                represents a Discord user
            role_name: str
                the name of the role to be assigned or removed from the user
            allow_remove: bool
                sets if removing roles is allowed
        """
        role = discord.utils.get(interaction.guild.roles, name=role_name)
        if role is None:
            response_string = (
                f"Role '{role_name}' not found <@{CONSTANTS["user_id"]}>")
        elif role not in user.roles:
            try:
                await user.add_roles(role)
                response_string = f"{role_name} role added to {user.name}"
            except discord.HTTPException as e:
                await self.bot.cogs["Helper"].respond(
                    f"discord.HTTPException: {e}")
                response_string = (
                    f"couldn't assign the {role_name} role to {user.name}, <@"
                    f"{CONSTANTS["user_id"]}>")
        elif allow_remove:
            try:
                await user.remove_roles(role)
                response_string = f"{role_name} role removed from {user.name}"
            except discord.HTTPException as e:
                await self.bot.cogs["Helper"].respond(
                    f"discord.HTTPException: {e}")
                response_string = (
                    f"couldn't remove the {role_name} role from {user.name}, "
                    f"<@{CONSTANTS["user_id"]}>")
        else:
            response_string = f"{user.name} already has {role_name} role"
        await self.bot.cogs["Helper"].respond(response_string, interaction)

    def toggle_role_command_generator(
            self, command_name: str, role_name: str) -> None:
        """
        Builds discord commands to allow users to toggle roles.

        Parameters:
            command_name : str
                the name of the command as it will appear in Discord
            role_name: str
                the name of the role to be assigned or removed from the
                user
        """
        @self.bot.tree.command(
            name=command_name, guild=self.bot.guild,
            description=f"Toggle {role_name} role.")
        async def func(interaction: discord.Interaction) -> None:
            await interaction.response.defer()
            await self.toggle_role(
                interaction, interaction.user, role_name, True)
        func.__name__ = command_name

    def assign_role_command_generator(
            self, command_name: str, required_role: str,
            role_name: str) -> None:
        """
        Builds discord commands to allow users to assign roles to other
        users.

        Parameters:
            command_name : str
                the name of the command as it will appear in Discord
            required_role : str
                the name of the role the user requires to assign
                role_name
            role_name: str
                the name of the role to be assigned to the targeted user
        """
        @self.bot.tree.command(
            name=command_name, guild=self.bot.guild,
            description=f"Assign {role_name} role.")
        @discord.app_commands.describe(
            username = (
                f"The user you want to assign the {role_name} role to (case "
                "sensitive)."))
        async def func(
            interaction: discord.Interaction, username: str) -> None:
            await interaction.response.defer()
            role = discord.utils.get(
                interaction.guild.roles, name=required_role)
            if role is None:
                await self.bot.cogs["Helper"].respond(
                    f"Role '{role_name}' not found <@{CONSTANTS["user_id"]}>",
                    interaction)
            elif role in interaction.user.roles:
                user = interaction.guild.get_member_named(username)
                await self.toggle_role(interaction, user, role_name, False)
            else:
                await self.bot.cogs["Helper"].respond(
                    f"{interaction.user.name} does not have permission to "
                    f"assign the {role_name} role", interaction)
        func.__name__ = command_name


async def setup(bot: commands.bot) -> None:
    """
    The entry point to load this extention.

    Parameter:
        bot : commands.bot
            The bot that loads this extension.
    """
    await bot.add_cog(DiscordRoles(bot))
