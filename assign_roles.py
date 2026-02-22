import discord
from constants import user_id, server_id
   
async def toggle_role(guild, user, role_name, allow_remove):
    role = discord.utils.get(guild.roles, name=role_name)
    if role not in user.roles:
        try: 
            await user.add_roles(role)
            discord_string = f"{role_name} role added"
            console_string = f"{role_name} role added to {user.name}"
        except:
            discord_string = f"couldn't assign the {role_name} role to {user.name}, <@{user_id}>"
            console_string = f"couldn't assign the {role_name} role to {user.name}"
    elif allow_remove:
        try:
            await user.remove_roles(role)
            discord_string = f"{role_name} role removed"
            console_string = f"{role_name} role removed from {user.name}"
        except:
            discord_string = f"couldn't remove the {role_name} role from {user.name}, <@{user_id}>"
            console_string = f"couldn't remove the {role_name} role from {user.name}"
    else:
        discord_string = f"{user.name} already has {role_name} role"
        console_string = f"{user.name} already has {role_name} role"
    return discord_string, console_string

async def toggle_role_message_send(interaction, user, role_name, allow_remove):
    discord_string, console_string = await toggle_role(interaction.guild, user, role_name, allow_remove)
    print(console_string)
    await interaction.followup.send(discord_string)
    return None

def toggle_role_command_generator(func_name, role_name, tree):
    @tree.command(name = func_name,
                  description = f"Toggle {role_name} role.",
                  guild=discord.Object(id=server_id))
    @discord.app_commands.describe()
    async def func(interaction):
        await interaction.response.defer()
        await toggle_role_message_send(interaction, interaction.user, role_name, True)
        return None
    return func

def assign_role_command_generator(func_name, required_role, role_name, tree):
    @tree.command(name = func_name,
                  description = f"Assign {role_name} role.",
                  guild=discord.Object(id=server_id))
    @discord.app_commands.describe(username = f"The user you want to assign the {role_name} role to (case sensitive).")
    async def func(interaction, username: str):
        await interaction.response.defer()
        role = discord.utils.get(interaction.guild.roles, name=required_role)
        if role in interaction.user.roles:
            user = interaction.guild.get_member_named(username)
            await toggle_role_message_send(interaction, user, role_name, False)
        else:
            print(f'you do not have permission to assign the {role_name} role')
            await interaction.followup.send(f"{interaction.user.name} does not have permission to assign the {role_name} role")
    return func