"""
This module implements the inglewood discord bot.
"""

import asyncio
import datetime
import hashlib
import json
import os
import pathlib
import random

import discord

from constants import CONSTANTS


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


async def minecraft_server_query(
        server_dictionary: dict, measure_latency: bool) -> str:
    """
    Checks live online status of all specified Minecraft servers and
    returns either version, address information, and latency
    information.
    
    Parameters:
        server_dictionary : dict
            dictionary containing details of minecraft servers to be
            queried.
        measure_latency : bool
            if True, latency information will be returned.
    
    Returns:
        response_string : string
            version, address information, and latency information for
            specified Minecraft servers.
    """
    response_string = ""
    for server_name, ports in server_dictionary.items():
        response_string += f"**{server_name}**"
        for server_type, port_dict in ports.items():
            port = port_dict["port"]
            client = CONSTANTS["server_types"][server_type]
            server = server_type(CONSTANTS["domain"], port)
            try:
                server_response = server.status()
                version = server_response.version.name
                version = port_dict.get("Version", version)
                response_string += (
                    f"\n{client} {version}: {CONSTANTS["domain"]}:{port}")
                if measure_latency:
                    response_string += f" ({server_response.latency:.1f} ms)"
            except OSError as e:
                await respond(f"OSError: {e}")
                response_string += f"\n{client}: Unavailable"
        response_string += "\n\n"
    return response_string.rstrip("\n")


async def toggle_role(
    interaction: discord.Interaction, user: discord.Member, role_name: str,
    allow_remove: bool) -> None:
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
            await respond(f"discord.HTTPException: {e}")
            response_string = (
                f"couldn't assign the {role_name} role to {user.name}, <@"
                f"{CONSTANTS["user_id"]}>")
    elif allow_remove:
        try:
            await user.remove_roles(role)
            response_string = f"{role_name} role removed from {user.name}"
        except discord.HTTPException as e:
            await respond(f"discord.HTTPException: {e}")
            response_string = (
                f"couldn't remove the {role_name} role from {user.name}, <@"
                f"{CONSTANTS["user_id"]}>")
    else:
        response_string = f"{user.name} already has {role_name} role"
    await respond(response_string, interaction)


class Inglewood(discord.Client):
    """
    Represents a bot that connects to Discord and interacts with the
    Discord WebSocket and API.
    """
    def __init__(self):
        super().__init__(intents=discord.Intents.all())
        self.last = None
        self.tier1 = False
        self.guild = discord.Object(CONSTANTS["server_id"])
        self.tree = discord.app_commands.CommandTree(self)

        self.random_tiers_command_generator(
            "random_tiers_all", "Roll a random tier", False)
        self.random_tiers_command_generator(
            "random_tiers_iv_plus", "Roll a random tier (IV+)", True)
        
        for command, role in CONSTANTS["toggle_roles"].items():
            self.toggle_role_command_generator(command, role)

        for command, role in CONSTANTS["assign_roles"].items():
            self.assign_role_command_generator(command, role[0], role[1])
        
        for server, ports in CONSTANTS["minecraft_servers"].items():
            self.ping_server_command_generator(server, ports)

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
            await respond("command tree updated")
        self.loop.create_task(self.game_servers_messages_update_loop())
        self.loop.create_task(self.daily_tier_roll_reset())

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
                    except discord.errors.NotFound as e:
                        await respond(f"discord.errors.NotFound: {e}")
                        os.remove("message_id.json")
                        await respond("previous server message not found")
                else:
                    message = await channel.send("placeholder")
                    await message.pin()
                    message_id = message.id
                    with open("message_id.json", "w", encoding="utf-8") as f:
                        json.dump(message_id, f)
                    break
            except discord.HTTPException as e:
                await respond(f"discord.HTTPException: {e}")
        current_server_msg = message.content
        while True:
            server_msg = await minecraft_server_query(
                CONSTANTS["minecraft_servers"], False)
            if current_server_msg != server_msg:
                try:
                    await message.edit(content=server_msg)
                    current_server_msg = server_msg
                    await respond("server message updated")
                except discord.HTTPException as e:
                    await respond(f"discord.HTTPException: {e}")
            await asyncio.sleep(CONSTANTS["server_msg_period"])

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
            await respond("reset daily tier roll variables")

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
        async def func(interaction: discord.Interaction) -> None:
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
        async def func(interaction: discord.Interaction, username: str) -> None:
            await interaction.response.defer()
            role = discord.utils.get(
                interaction.guild.roles, name=required_role)
            if role is None:
                await respond(
                    f"Role '{role_name}' not found <@{CONSTANTS["user_id"]}>",
                    interaction)
            elif role in interaction.user.roles:
                user = interaction.guild.get_member_named(username)
                await toggle_role(interaction, user, role_name, False)
            else:
                await respond(
                    f"{interaction.user.name} does not have permission to "
                    f"assign the {role_name} role", interaction)
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
        async def func(interaction: discord.Interaction) -> None:
            await interaction.response.defer()
            tiers = {
                "Wildcard" : 2, "I" : 1, "II" : 1, "III" : 1, "IV" : 1,
                "V" : 2, "VI" : 2, "VII" : 2, "VIII" : 2, "IX" : 2, "X" : 2,
                "XI" : 2
            }
            timestamp = seconds_since_midnight()
            if (battle_pass or
                timestamp > CONSTANTS["low_tier_block_after"] or
                timestamp < CONSTANTS["low_tier_block_before"]):
                for t in {"I", "II", "III"}:
                    tiers[t] = 0
            elif self.tier1:
                tiers["I"] = 0
            tiers[self.last] = 0
            draw = random.choices(list(tiers.keys()), list(tiers.values()))[0]
            self.last = draw
            if draw == "I":
                self.tier1 = True
            elif (draw in ["II", "IV", "V", "VI", "VII", "VIII"] and
                  random.random() < 1/30):
                if draw == "IV" and random.random() < 0.5:
                    draw += " Double"
                draw += " Preferential"
            await respond(draw, interaction)
        func.__name__ = command_name

    def ping_server_command_generator(self, server: str, ports: dict) -> None:
        """
        Builds discord commands to allow users to ping minecraft servers.

        Parameters:
            server : str
                the name of the minecraft server to be pinged
            ports : str
                the port information
        """
        command_name = "ping_" + server.lower().replace(" ", "_")
        @self.tree.command(
            name=command_name, guild=self.guild,
            description="Pings {server}.")
        async def func(interaction: discord.Interaction) -> None:
            await interaction.response.defer()
            response_string = (
                await minecraft_server_query({server: ports} ,True))
            await respond(response_string, interaction)
        func.__name__ = command_name


def main():
    """
    This creates and starts the inglewood discord bot.
    """
    Inglewood().run(CONSTANTS["token"])


if __name__ == "__main__":
    main()
