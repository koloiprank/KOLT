import json
import discord

async def load_config() -> dict[str, str]:
    with open("config.json", "r") as file:
        data = json.load(file)
    file.close()
    
    return data

async def save_config(data : dict[str, str]) -> None:
    with open("config.json", "w") as file:
        json.dump(data, file)
    file.close()

async def format_message(msg : str, member : discord.Member, guild : discord.Guild) -> str:
    
    if "@user" or "@server" in msg:
        msg = msg.replace("@user", f"{member.mention}")
        msg = msg.replace("@server", f"{guild.name}")
    
    return msg

async def has_permissions(interaction : discord.Interaction, permissions : list[str]) -> bool:
    
    user_perms = [permission[0] for permission in interaction.user.guild_permissions if permission[1]]
    ct = 0
    
    for permission in permissions:
        if permission in user_perms:
            ct+=1
    
    return ct == len(permissions)