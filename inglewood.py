"""
This module implements the inglewood discord bot.
"""

import asyncio
from collections.abc import Callable
import datetime
import hashlib
import os
import pathlib
import json
import random

import discord

from constants import CONSTANTS

def retry() -> Callable:
    """
    Constructs a retry decorator which calls a function again if it
    raises an Error.

    Parameters:
        delay : int
            number of seconds to wait before retrying the function after
            failure.

    Returns:
        decorator : Callable
            the retry decorator function.
    """
    def decorator(func):
        def retry_func(*args, **kwargs):
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e: #pylint: disable=W0718
                    print(e)
        return retry_func
    return decorator


def seconds_since_midnight() -> float:
    """
    Returns the current time of day in seconds.

    Returns:
        time : float
            time of day in seconds
    """
    now = datetime.datetime.now(CONSTANTS["time_zone"])
    timedelta = now - now.replace(hour=0, minute=0, second=0, microsecond=0)
    time = timedelta.total_seconds()
    return time


def minecraft_server_query(measure_latency: bool) -> str:
    """
    Checks live online status of all specified Minecraft servers and
    returns either version, address information, and latency
    information.
    
    Parameters:
        measure_latency : object
            if True, latency information will be returned.
    
    Returns:
        response_string : string
            version, address information, and latency information for
            specified Minecraft servers.
    """
    response_string = ""
    for server_name, ports in CONSTANTS["minecraft_servers"].items():
        response_string += f"**{server_name}**"
        for server_type, port_dict in ports.items():
            port = port_dict["port"]
            client = CONSTANTS["server_types"][server_type]
            server = server_type(CONSTANTS["domain"], port)
            try:
                server_response = server.status()
                version = server_response.version.name
                version = port_dict.get("Version", version)
                if measure_latency:
                    latency = server_response.latency
                    response_string += (
                        f"\n{client} {version}: {CONSTANTS["domain"]}:{port}"
                        f" ({latency:.1f} ms)")
                else:
                    response_string += (
                        f"\n{client} {version}: {CONSTANTS["domain"]}:{port}")
            except OSError:
                response_string += f"\n{client}: Unavailable"
        response_string += "\n\n"
    return response_string.rstrip("\n")


async def toggle_role(
    interaction: object, user: object, role_name: str,
    allow_remove: bool) -> None:
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
    if role is None:
        response_string = (
            f"Role '{role_name}' not found <@{CONSTANTS["user_id"]}>")
    elif role not in user.roles:
        try:
            await user.add_roles(role)
            response_string = f"{role_name} role added to {user.name}"
        except discord.HTTPException:
            response_string = (
                f"couldn't assign the {role_name} role to {user.name}, <@"
                f"{CONSTANTS["user_id"]}>")
    elif allow_remove:
        try:
            await user.remove_roles(role)
            response_string = f"{role_name} role removed from {user.name}"
        except discord.HTTPException:
            response_string = (
                f"couldn't remove the {role_name} role from {user.name}, <@"
                f"{CONSTANTS["user_id"]}>")
    else:
        response_string = f"{user.name} already has {role_name} role"
    print(response_string)
    await interaction.followup.send(response_string)


class Inglewood(discord.Client):
    """
    Represents a bot that connects to Discord and interacts with the
    Discord WebSocket and API.
    """
    def __init__(self):
        super().__init__(intents=discord.Intents.all())
        self.last = None
        self.tier1 = False
        self.last_ping = 0
        self.guild = discord.Object(CONSTANTS["server_id"])
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
        
        @self.tree.command(
            name="ping_minecraft_servers", guild=self.guild,
            description="Ping Minecraft servers.")
        async def ping(interaction: object):
            await interaction.response.defer()
            response_string = minecraft_server_query(True)
            try:
                await interaction.followup.send(response_string)
                print(f"{interaction.user.name} pinged Minecraft servers")
            except discord.HTTPException:
                print(
                    f"{interaction.user.name}"
                    "could not ping Minecraft servers")

    async def setup_hook(self) -> None:
        """     
        Syncs the application commands to the Discord guild (server) and
        adds tasks to the event loop used for asynchronous operations,
        after the bot is logged in but before it has connected to the
        Websocket.
        """
        if os.path.exists("hash_dict.json"):
            with open("hash_dict.json", "r", encoding="utf-8") as f:
                last_hash = json.load(f)
        else:
            last_hash = None
        current_hash = {}
        for file in os.listdir():
            if pathlib.PurePosixPath(file).suffix == ".py":
                with open(file, "rb") as file_to_hash:
                    data_to_hash = file_to_hash.read()
                    md5_returned = hashlib.md5(data_to_hash).hexdigest()
                    current_hash[file] = md5_returned
        if current_hash != last_hash:
            with open("hash_dict.json", "w", encoding="utf-8") as f:
                json.dump(current_hash, f)
            await self.tree.sync(guild = self.guild)
            print("command tree updated")
        self.loop.create_task(self.game_servers_messages_update_loop())
        self.loop.create_task(self.daily_tier_roll_reset())

    @retry()
    async def game_servers_messages_update_loop(self) -> None:
        """
        Updates the message in the relavent channel every
        server_msg_period seconds with live online status and web
        address information of all specified Minecraft servers
        """
        await self.wait_until_ready()
        channel = self.get_channel(CONSTANTS["channel_id"])
        while True:
            try:
                if os.path.exists("message_id.json"):
                    with open("message_id.json", "r", encoding="utf-8") as f:
                        message_id = json.load(f)
                    try:
                        message = await channel.fetch_message(message_id)
                        break
                    except discord.errors.NotFound:
                        os.remove("message_id.json")
                        print("previous server message not found")
                else:
                    message = await channel.send("placeholder")
                    await message.pin()
                    message_id = message.id
                    with open("message_id.json", "w", encoding="utf-8") as f:
                        json.dump(message_id, f)
                    break
            except discord.HTTPException:
                print("HTTP error")
        current_server_msg = message.content
        while True:
            server_msg = minecraft_server_query(False)
            if current_server_msg != server_msg:
                try:
                    await message.edit(content=server_msg)
                    current_server_msg = server_msg
                    print("server message updated")
                except discord.HTTPException:
                    print("HTTP error")
            await asyncio.sleep(CONSTANTS["server_msg_period"])

    @retry()
    async def daily_tier_roll_reset(self) -> None:
        """
        Performs a daily reset of the tier roll mechanics at
        daily_tier_reset_time each day.
        """
        await self.wait_until_ready()
        while True:
            time = (CONSTANTS["daily_tier_reset_time"]
                    - seconds_since_midnight())
            if time <= 0:
                time += 24*60*60
            await asyncio.sleep(time)
            self.last = None
            self.tier1 = False
            print("reset daily tier roll variables")

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
        @self.tree.command(
            name=command_name, guild=self.guild,
            description=f"Toggle {role_name} role.")
        async def func(interaction: object):
            await interaction.response.defer()
            await toggle_role(
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
        @self.tree.command(
            name=command_name, guild=self.guild,
            description=f"Assign {role_name} role.")
        @discord.app_commands.describe(
            username = (
                f"The user you want to assign the {role_name} role to (case "
                "sensitive)."))
        async def func(interaction: object, username: str):
            await interaction.response.defer()
            role = discord.utils.get(
                interaction.guild.roles, name=required_role)
            if role is None:
                print(
                    f"Role '{role_name}' not found <@{CONSTANTS["user_id"]}>")
                await interaction.followup.send(
                    f"Role '{role_name}' not found <@{CONSTANTS["user_id"]}>")
            elif role in interaction.user.roles:
                user = interaction.guild.get_member_named(username)
                await toggle_role(interaction, user, role_name, False)
            else:
                print(
                    f"you do not have permission to assign the {role_name} "
                    "role")
                await interaction.followup.send((
                    f"{interaction.user.name} does not have permission to "
                    f"assign the {role_name} role"))
        func.__name__ = command_name

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
        @self.tree.command(
            name=command_name, guild=self.guild,
            description=command_description)
        async def func(interaction: object) -> None:
            await interaction.response.defer()
            tiers = [
                "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X",
                "XI", "Wildcard", "V", "VI", "VII", "VIII", "IX", "X", "XI", 
                "Wildcard"
                ]
            timestamp = seconds_since_midnight()
            if (battle_pass
                    or timestamp > CONSTANTS["low_tier_block_after"]
                    or timestamp < CONSTANTS["low_tier_block_before"]):
                tiers.remove("I")
                tiers.remove("II")
                tiers.remove("III")
            elif self.tier1:
                tiers.remove("I")
            if self.last in tiers:
                tiers.remove(self.last)
                if self.last in tiers:
                    tiers.remove(self.last)
            draw = random.choice(tiers)
            self.last = draw
            if draw == "I":
                self.tier1 = True
            elif (draw in ["II","V","VI","VII","VIII"]
                    and random.randint(1, 30) == 1):
                draw += " Preferential"
            elif draw == "IV" and random.randint(1, 30) == 1:
                if random.randint(0, 1) == 1:
                    draw += " Preferential"
                else:
                    draw += " Double Preferential"
            await interaction.followup.send(draw)
            print(
                f"{command_name} command rolled {draw} for "
                f"{interaction.user.name}")
        func.__name__ = command_name


def main():
    """
    This creates and starts the inglewood discord bot.
    """
    Inglewood().run(CONSTANTS["token"])


if __name__ == "__main__":
    main()
