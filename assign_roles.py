import discord
from constants import user_id, server_id


async def assign_role(interaction, role_name):
    role = discord.utils.get(interaction.guild.roles, name=role_name)
    if role not in interaction.user.roles:
        try: 
            await interaction.user.add_roles(role)
            discord_string = f"{role_name} role added."
            console_string = f"{interaction.user.name}: toggled on the {role_name} role"
        except:
            discord_string = f"couldn't assign the {role_name} role, <@{user_id}>"
            console_string = f"{interaction.user.name}: couldn't assign the {role_name} role"
    else:
        try:
            await interaction.user.remove_roles(role)
            discord_string = f"{role_name} role removed."
            console_string = f"{interaction.user.name}: toggled off the {role_name} role"
        except:
            discord_string = f"couldn't remove the {role_name} role, <@{user_id}>"
            console_string = f"{interaction.user.name}: couldn't remove the {role_name} role"
    return discord_string, console_string


async def assign_role_message(interaction, role_name):
    discord_string, console_string = await assign_role(interaction, role_name)
    print(console_string)
    await interaction.followup.send(discord_string)
    return None


def assign_role_command_generator(func_name, role_name, tree):
    @tree.command(name = f"{func_name}",
                  description = f"Toggle {role_name} role.",
                  guild=discord.Object(id=server_id))
    @discord.app_commands.describe()
    async def func(interaction):
        await interaction.response.defer()
        await assign_role(interaction, role_name)
        return None
    return func