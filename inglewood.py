"""
This module implements the inglewood discord bot.
"""

import asyncio
from collections.abc import Callable

import discord

from Inglewood.hash_check import hash_check
from Inglewood.server_status_check import server_status_check, initialisation
from Inglewood.assign_roles import toggle_role
from Inglewood.tier_roll import tier_roll
from Inglewood.wot_time import get_timestamp
from Inglewood.constants import (
    TOKEN, SERVER_ID, CHANNEL_ID, DOMAIN, MINECRAFT_SERVERS, SERVER_MSG_PERIOD,
    DAILY_TIER_RESET_TIME)


class Inglewood(discord.Client):
    """
    Represents a bot that connects to Discord and interacts with the Discord
    WebSocket and API.
    """
    def __init__(self):
        super().__init__(intents=discord.Intents.all())
        self.last = None
        self.tier1 = False
        self.tree = discord.app_commands.CommandTree(self)
        self.random_tiers_command_generator(
            "random_tiers_all", "Roll a random tier", False)
        self.random_tiers_command_generator(
            "random_tiers_iv_plus", "Roll a random tier (IV+)", True)
        self.assign_role_command_generator(
            "assign_outings_role", "Member", "Outings")
        self.assign_role_command_generator(
            "assign_gaming_plus_nmfuel_role", "Member", "Gaming+Nightmarefuel")
        self.toggle_role_command_generator(
            "toggle_ark_role", "Ark Server")
        self.toggle_role_command_generator(
            "toggle_minecraft_role", "Minecraft Server")
        self.toggle_role_command_generator(
            "toggle_free_games_role", "Free Games")
        self.toggle_role_command_generator(
            "toggle_archive_role", "Archive")

    async def setup_hook(self) -> None:
        """     
        Syncs the application commands to the Discord guild (server) and
        adds tasks to the event loop used for asynchronous operations,
        after the bot is logged in but before it has connected to the
        Websocket.
        """
        if hash_check():
            await self.tree.sync(guild=discord.Object(SERVER_ID))
            print('command tree updated')
        self.loop.create_task(self.game_servers_messages_update_loop())
        self.loop.create_task(self.daily_tier_roll_reset())

    async def game_servers_messages_update_loop(self) -> None:
        """
        Updates the message in the relavent channel every
        server_msg_period seconds with live online status and web
        address information of all three Minecraft servers
        """
        await self.wait_until_ready()
        channel = self.get_channel(CHANNEL_ID)
        message = await initialisation(channel)
        current_server_msg = message.content
        while True:
            server_msg = ''
            for server, ports in MINECRAFT_SERVERS.items():
                server_msg += server_status_check(
                    server, DOMAIN, ports)
            if current_server_msg != server_msg[:-2]:
                try:
                    await message.edit(content=server_msg)
                    current_server_msg = server_msg
                    print('server message updated')
                except discord.HTTPException:
                    pass
            await asyncio.sleep(SERVER_MSG_PERIOD)

    async def daily_tier_roll_reset(self) -> None:
        """
        Performs a daily reset of the tier roll mechanics at
        DAILY_TIER_RESET_TIME each day.
        """
        await self.wait_until_ready()
        while True:
            time = DAILY_TIER_RESET_TIME - get_timestamp()
            if time <= 0:
                time += 24*60*60
            await asyncio.sleep(time)
            self.last = None
            self.tier1 = False
            print('reset daily tier roll variables')

    def toggle_role_command_generator(
            self, command_name: str, role_name: str) -> Callable:
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
        @self.tree.command(
            name = command_name, description = f"Toggle {role_name} role.",
            guild = discord.Object(id=SERVER_ID))
        @discord.app_commands.describe()
        async def func(interaction: object):
            await interaction.response.defer()
            await toggle_role(
                interaction, interaction.user, role_name, True)

    def assign_role_command_generator(
            self, command_name: str, required_role: str,
            role_name: str) -> Callable:
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
        @self.tree.command(name = command_name,
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
                await toggle_role(interaction, user, role_name, False)
            else:
                print(f'you do not have permission to assign the {role_name} role')
                await interaction.followup.send((
                    f"{interaction.user.name} does not have permission to assign "
                    f"the {role_name} role"))

    def random_tiers_command_generator(
            self, command_name: str, command_description: str,
            battle_pass: bool) -> Callable:
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
        @self.tree.command(
                name = command_name, description = command_description,
                guild=discord.Object(id=SERVER_ID))
        @discord.app_commands.describe()
        async def func(interaction: object) -> None:
            await interaction.response.defer()
            draw = tier_roll(self, battle_pass)
            await interaction.followup.send(draw)
            print(f"{command_name} command rolled {draw} for "
                f"{interaction.user.name}")

Inglewood().run(TOKEN)
