"""
This module implements the inglewood discord bot.
"""

import asyncio
import datetime

import discord

from hash_check import hash_check
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
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.last = None
        self.tier1 = False
        self.tree = discord.app_commands.CommandTree(self)


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
            try:
                channel = self.get_channel(CHANNEL_ID)
                message = await channel.fetch_message(MESSAGE_ID)
                await message.edit(content=server_msg)
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


client = MyClient(intents=discord.Intents.all())
random_tiers_command_generator(
    client, "random_tiers_all", "Roll a random tier", False)
random_tiers_command_generator(
    client, "random_tiers_iv_plus", "Roll a random tier (IV+)", True)
assign_role_command_generator(
    client, "assign_outings_role", "Member", "Outings")
assign_role_command_generator(
    client, "assign_gaming_plus_nmfuel_role", "Member", "Gaming+Nightmarefuel")
toggle_role_command_generator(client, "toggle_ark_role", "Ark Server")
toggle_role_command_generator(
    client, "toggle_minecraft_role", "Minecraft Server")
toggle_role_command_generator(client, "toggle_free_games_role", "Free Games")
toggle_role_command_generator(client, "toggle_archive_role", "Archive")
client.run(TOKEN)
