import random
import datetime
import discord
from constants import server_id

def tier_roll(battle_pass, values):
    tiers = ['I','II','III','IV',
             'V','VI','VII','VIII','IX','X','XI','Wildcard',
             'V','VI','VII','VIII','IX','X','XI','Wildcard']
    now = datetime.datetime.now(values.Amsterdam)
    timestamp = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
    if battle_pass or timestamp > 23*60*60 or timestamp < 8*60*60:
        tiers.remove('I')
        tiers.remove('II')
        tiers.remove('III')
    elif values.tier1:
        tiers.remove('I')
    if values.last in tiers:
        tiers.remove(values.last)
        if values.last in tiers:
            tiers.remove(values.last)
    draw = random.choice(tiers)
    values.last = draw
    if draw == 'I':
        values.tier1 = True
    elif draw in ['II','V','VI','VII','VIII'] and random.randint(1, 30) == 1:
        draw += ' Preferential'
    elif draw in ['IV'] and random.randint(1, 30) == 1:
        if random.randint(0, 1) == 1:
            draw += ' Preferential'
        else:
            draw += ' Double Preferential'
    return draw

def random_tiers_command_generator(func_name, func_description, battle_pass, tree, values):
    @tree.command(name = func_name, description = func_description, guild=discord.Object(id=server_id))
    @discord.app_commands.describe()
    async def func(interaction):
        await interaction.response.defer()
        draw = tier_roll(battle_pass, values)
        await interaction.followup.send(draw)
        print(f'{func_name} command rolled {draw} for {interaction.user.name}')
        return None
    return func