"""
This module implements the inglewood discord bot.
"""

import asyncio
import datetime
from dataclasses import dataclass

import discord

from server_status_check import server_status_check
from assign_roles import (toggle_role_command_generator,
    assign_role_command_generator)
from tier_roll import random_tiers_command_generator
from wot_time import get_timestamp
from constants import (DOMAIN, SUR_PORT, SUR_BED, RED_PORT, RED_BED, ADV_PORT,
    FAIL_OVER_VER, TOKEN, SERVER_ID, CHANNEL_ID, MESSAGE_ID, SERVER_MSG_PERIOD,
    DAILY_TIER_RESET_TIME, TIME_ZONE)


class MyClient(discord.Client):
    """
    Represents a client connection that connects to Discord.
    This class is used to interact with the Discord WebSocket and API.
    """

    async def setup_hook(self) -> None:
        """     
        Syncs the application commands to the Discord guild (server) and
        adds tasks to the event loop used for asynchronous operations,
        after the bot is logged in but before it has connected to the
        Websocket.
        """
        await tree.sync(guild=discord.Object(SERVER_ID))
        self.loop.create_task(self.game_servers_messages_update_loop())
        self.loop.create_task(self.daily_tier_roll_reset())
        return None

    async def game_servers_messages_update_loop(self) -> None:
        """
        Updates the message in the relavent channel every
        server_msg_period seconds with live online status and web
        address information of all three Minecraft servers
        """
        await self.wait_until_ready()
        while True:
            server_msg = server_status_check(
                "Survival Server", DOMAIN, SUR_PORT, bed_port = SUR_BED)
            server_msg += server_status_check(
                "Redstone Server", DOMAIN, RED_PORT, bed_port = RED_BED)
            server_msg += server_status_check(
                "Adventure Server", DOMAIN, ADV_PORT,
                fail_over_ver = FAIL_OVER_VER)
            current_time = datetime.datetime.now(TIME_ZONE)
            server_msg += f'Last Updated: {current_time}'
            channel = self.get_channel(CHANNEL_ID)
            message = await channel.fetch_message(MESSAGE_ID)
            await message.edit(content=server_msg)
            print('server message updated')
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
            values.last = None
            values.tier1 = False
            print('reset daily tier roll variables')


@dataclass
class Variables():
    """
    A class containing frequently used non constant variables.

    Attributes:
        last : str
            the most recently draw tier
        tier1 : bool
            True if tier I has been already drawn today
    """
    last: str | None = 1
    tier1: bool = False


client = MyClient(intents=discord.Intents.all())
tree = discord.app_commands.CommandTree(client)
values = Variables()
random_tiers_command_generator(
    "random_tiers_all", "Roll a random tier", False, tree, values)
random_tiers_command_generator(
    "random_tiers_iv_plus", "Roll a random tier (IV+)", True, tree, values)
assign_role_command_generator("assign_outings_role", "Member", "Outings", tree)
assign_role_command_generator(
    "assign_gaming_plus_nmfuel_role", "Member", "Gaming+Nightmarefuel", tree)
toggle_role_command_generator("toggle_ark_role", "Ark Server", tree)
toggle_role_command_generator(
    "toggle_minecraft_role", "Minecraft Server", tree)
toggle_role_command_generator("toggle_free_games_role", "Free Games", tree)
toggle_role_command_generator("toggle_archive_role", "Archive", tree)
client.run(TOKEN)
