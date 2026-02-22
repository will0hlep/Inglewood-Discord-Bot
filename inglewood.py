import discord
import asyncio
import datetime
import pytz
from constants import (DOMAIN, SUR_PORT, SUR_BED, RED_PORT,
                       RED_BED, ADV_PORT, FAIL_OVER_VER, token,
                       server_id, channel_id, message_id,
                       server_msg_period, tier_reset_check_period)
from server_status_check import server_status_check
from assign_roles import toggle_role_command_generator, assign_role_command_generator
from tier_roll import random_tiers_command_generator

class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_ready(self):
        await tree.sync(guild=discord.Object(id=server_id))

    async def setup_hook(self) -> None:
        self.bg_task1 = self.loop.create_task(self.game_servers_messages_update_loop())
        self.bg_task2 = self.loop.create_task(self.daily_tier_roll_reset())

    async def game_servers_messages_update_loop(self):
        await self.wait_until_ready()
        while True:
            server_msg = server_status_check("Survival Server", DOMAIN, SUR_PORT, bed_port = SUR_BED)
            server_msg += server_status_check("Redstone Server", DOMAIN, RED_PORT, bed_port = RED_BED)
            server_msg += server_status_check("Adventure Server", DOMAIN, ADV_PORT, fail_over_ver = FAIL_OVER_VER)
            current_time = datetime.datetime.now(values.London)
            server_msg += f'Last Updated: {current_time}'
            channel = self.get_channel(channel_id)
            message = await channel.fetch_message(message_id)
            await message.edit(content=server_msg)
            print('server message updated')
            await asyncio.sleep(server_msg_period)

    async def daily_tier_roll_reset(self):
        await self.wait_until_ready()
        now = (datetime.datetime.now(values.London)-datetime.timedelta(hours = tier_reset_check_period))
        day = now.day
        while True:
            now = (datetime.datetime.now(values.London)-datetime.timedelta(hours = tier_reset_check_period))
            day_ = now.day
            if day_ != day:
                values.last = ''
                values.tier1 = False
                day = day_
                print('reset daily tier roll variables')
            await asyncio.sleep(tier_reset_check_period*60*60)

class variables():
    def __init__(self):
        self.last = None
        self.tier1 = False
        self.London = pytz.timezone('Europe/London')
        self.Amsterdam = pytz.timezone('Europe/Amsterdam')

def main():
    client = MyClient(intents=discord.Intents.all())
    tree = discord.app_commands.CommandTree(client)
    values = variables()
    random_tiers_command_generator("random_tiers_all", "Roll a random tier", False, tree, values)
    random_tiers_command_generator("random_tiers_iv_plus", "Roll a random tier (IV+)", True, tree, values)
    assign_role_command_generator("assign_outings_role", "Member", "Outings", tree)
    assign_role_command_generator("assign_gaming_plus_nmfuel_role", "Member", "Gaming+Nightmarefuel", tree)
    toggle_role_command_generator("toggle_ark_role", "Ark Server", tree)
    toggle_role_command_generator("toggle_minecraft_role", "Minecraft Server", tree)
    toggle_role_command_generator("toggle_free_games_role", "Free Games", tree)
    toggle_role_command_generator("toggle_archive_role", "Archive", tree)
    client.run(token)
    return None

main()