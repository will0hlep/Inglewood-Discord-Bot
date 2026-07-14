"""
Implements commands for managing Minecraft server related commands.
"""

import json
import os

import aiohttp
import discord
from discord.ext import tasks

from constants import CONSTANTS
from inglewood import Cog, Inglewood


class Minecraft(Cog):
    """
    Represents a cog that adds commands for managing Minecraft server
    related commands.
    """
    def __init__(self, bot: Inglewood):
        super().__init__(bot)
        self.message = None
        self.server_msg_content = None
        for server, ports in CONSTANTS["minecraft_servers"].items():
            self.ping_server_command_generator(server, ports)
        self.game_servers_messages_update_loop.start()

    async def minecraft_server_query(
            self, server_dictionary: dict,
            measure_latency: bool = True) -> str:
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
        response = []
        for server_name, ports in server_dictionary.items():
            server_string = f"**{server_name}**"
            for server_type, port_dict in ports.items():
                port = port_dict["port"]
                domain = CONSTANTS["domain"]
                client = CONSTANTS["server_types"][server_type]
                server = server_type(domain, port)
                try:
                    server_response = await server.async_status()
                except OSError as e:
                    if not isinstance(e, TimeoutError):
                        await self.bot.cogs["Helper"].respond(
                            f"OSError: {server_name} ({client} {version}): "
                            f"{domain}:{port}, {e}")
                    server_string += f"\n{client}: Unavailable"
                else:
                    version = server_response.version.name
                    version = port_dict.get("Version", version)
                    server_string += (
                        f"\n{client} {version}: {domain}:{port}")
                    if measure_latency:
                        server_string += (
                            f" ({server_response.latency:.1f} ms)")
            response.append(server_string)
        return "\n\n".join(response)

    @tasks.loop(seconds=CONSTANTS["server_msg_period"])
    async def game_servers_messages_update_loop(self) -> None:
        """
        Updates the message in the relavent channel every
        server_msg_period seconds with live online status and web
        address information of all specified Minecraft servers
        """
        server_msg = await self.minecraft_server_query(
            CONSTANTS["minecraft_servers"], False)
        if self.server_msg_content != server_msg:
            try:
                await self.message.edit(content=server_msg)
            except (discord.HTTPException,
                    aiohttp.client_exceptions.ClientConnectorDNSError) as e:
                await self.bot.cogs["Helper"].respond(
                    f"discord.HTTPException: {e}")
            else:
                self.server_msg_content = server_msg
                await self.bot.cogs["Helper"].respond(
                    "server message updated")

    @game_servers_messages_update_loop.before_loop
    async def pre_game_servers_messages_update_loop(self) -> None:
        """
        Checkes for an existing game server message, and if one is found
        updates the current_server_msg and message properties, otherwise
        creates a placeholder.
        """
        await self.bot.wait_until_ready()
        channel = self.bot.get_channel(CONSTANTS["channel_id"])
        while True:
            try:
                if os.path.exists("message_id.json"):
                    with open("message_id.json", "r", encoding="utf-8") as f:
                        message_id = json.load(f)
                    try:
                        self.message = await channel.fetch_message(message_id)
                    except discord.errors.NotFound as e:
                        await self.bot.cogs["Helper"].respond(
                            f"discord.errors.NotFound: {e}")
                        os.remove("message_id.json")
                        await self.bot.cogs["Helper"].respond(
                            "previous server message not found")
                    else:
                        break
                else:
                    self.message = await channel.send("placeholder")
                    await self.message.pin()
                    with open("message_id.json", "w", encoding="utf-8") as f:
                        json.dump(self.message.id, f)
                    break
            except discord.HTTPException as e:
                await self.bot.cogs["Helper"].respond(
                    f"discord.HTTPException: {e}")
        self.server_msg_content = self.message.content

    async def cog_unload(self):
        """
        Terminates all looping tasks when unloading this cog.
        """
        self.game_servers_messages_update_loop.cancel()

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
        @self.bot.tree.command(
            name=command_name, guild=self.bot.guild,
            description=f"Pings {server}.")
        async def func(interaction: discord.Interaction) -> None:
            await interaction.response.defer()
            response_string = (
                await self.minecraft_server_query({server: ports}))
            await self.bot.cogs["Helper"].respond(response_string, interaction)
        func.__name__ = command_name


async def setup(bot: Inglewood) -> None:
    """
    The entry point to load this extention.

    Parameter:
        bot : Inglewood
            The bot that loads this extension.
    """
    await bot.add_cog(Minecraft(bot))
