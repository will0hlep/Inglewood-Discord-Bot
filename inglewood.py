import discord
import asyncio
import datetime
import pytz
import random
from constants import (DOMAIN, SUR_PORT, SUR_BED, RED_PORT,
                       RED_BED, ADV_PORT, FAIL_OVER_VER, token,
                       server_id, channel_id, message_id,
                       server_msg_period, tier_reset_check_period)
from server_status_check import server_status_check
from assign_roles import assign_role_command_generator, assign_role


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
            message = await channel.fetch_message(message_id) # type: ignore
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


client = MyClient(intents=discord.Intents.all())
tree = discord.app_commands.CommandTree(client)


assign_role_command_generator("toggle_ark_role", "Ark Server", tree)
assign_role_command_generator("toggle_minecraft_role", "Minecraft Server", tree)
assign_role_command_generator("toggle_free_games_role", "Free Games", tree)
assign_role_command_generator("toggle_archive_role", "Archive", tree)


@tree.command(name = "edit_member_roles",
              description = "Assign Member role, and optionally the Outings and/or Gaming+Nightmarefuel roles, to a selected user. Requires the member role.",
              guild=discord.Object(id=server_id))
@discord.app_commands.describe(username = "The username of the user you want to assign roles to (case sensitive, discriminator is optional, nicknames only work for users with old style usernames).",
                               gaming_and_nightmarefuel = "Enter True if you want to assign the gaming+nightmarefuel role, otherwise put False. Requires the gaming+nightmarefuel role.",
                               outings = "Enter True if you want to assign the outings role, otherwise put False. Requires the outings role.")
async def third_command(interaction, username: str, gaming_and_nightmarefuel: bool, outings: bool):
    await interaction.response.defer()
    print('running third_command function')
    role = discord.utils.get(interaction.guild.roles, name="Member")
    if role in interaction.user.roles:
        discord_string, console_string = await assign_role(interaction, "Member")
        if gaming_and_nightmarefuel:
            discord_string += '\n'
            console_string += '\n'
            discord_string, console_string += await assign_role(interaction, "Gaming+Nightmarefuel")
        if outings:
            discord_string += '\n'
            console_string += '\n'
            discord_string, console_string += await assign_role(interaction, "Outings")
        print(console_string)
        await interaction.followup.send(discord_string)
    else:
        print(f'{interaction.user.name}: you do not have permission to assign the member, gaming+nightmarefuel and outings roles to {username}')
        await interaction.followup.send(f"you do not have permission to assign the member, gaming+nightmarefuel or outings roles")
    return None


@tree.command(name = "random_tiers_all", description = "Roll a random tier", guild=discord.Object(id=server_id))
@discord.app_commands.describe()
async def fifth_command(interaction):
    await interaction.response.defer()
    tiers = ['I','II','III','IV','V','VI','VII','VIII','IX','X','XI','Wildcard','V','VI','VII','VIII','IX','X','XI','Wildcard']
    if values.last != '':
        tiers.remove(values.last)
        if values.last in tiers:
            tiers.remove(values.last)
    now = datetime.datetime.now(values.Amsterdam)
    timestamp = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
    if timestamp > 82800 or timestamp < 28800:
        if 'I' in tiers:
            tiers.remove('I')
        if 'II' in tiers:
            tiers.remove('II')
        if 'III' in tiers:
            tiers.remove('III')
    if values.tier1 and 'I' in tiers:
        tiers.remove('I')
    draw = random.choice(tiers)
    if draw == 'I':
        values.tier1 = True
    pref = ''
    if draw in ['II','V','VI','VII','VIII']:
        if random.randint(1, 30) == 1:
            pref = ' Preferential'
    elif draw in ['IV']:
        if random.randint(1, 30) == 1:
            if random.randint(0, 1) == 1:
                pref = ' Double Preferential'
            else:
                pref = ' Preferential'
    await interaction.followup.send(draw+pref)
    values.last = draw
    print(f'random_tiers_all command rolled {draw} for {interaction.user.name}')
    return None


@tree.command(name = "random_tiers_IV+", description = "Roll a random tier (IV+)", guild=discord.Object(id=server_id))
@discord.app_commands.describe()
async def sixth_command(interaction):
    await interaction.response.defer()
    tiers = ['IV','V','VI','VII','VIII','IX','X','XI','Wildcard','V','VI','VII','VIII','IX','X','XI','Wildcard']
    if values.last != '':
        if values.last in tiers:
            tiers.remove(last)
    draw = random.choice(tiers)
    pref = ''
    if draw in ['II','V','VI','VII','VIII']:
        if random.randint(1, 30) == 1:
            pref = ' Preferential'
    elif draw in ['IV']:
        if random.randint(1, 30) == 1:
            if random.randint(0, 1) == 1:
                pref = ' Double Preferential'
            else:
                pref = ' Preferential'
    await interaction.followup.send(draw+pref)
    values.last = draw
    print(f'random_tiers_battle_pass command rolled {draw} for {interaction.user.name}')
    return None


class variables():
    def __init__(self):
        self.last = ''
        self.tier1 = False
        self.London = pytz.timezone('Europe/London')
        self.Amsterdam = pytz.timezone('Europe/Amsterdam')


values = variables()
client.run(token)