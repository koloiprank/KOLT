import json
import discord
import os

def find_file(filename : str, path : str) -> str:
    for root, dirs, files in os.walk(path):
        if filename in files:
            return os.path.join(root, filename)

def get_banned_words_per_server() -> dict[str: dict[str : str]]:
    to_return = {}
    for root, dirs, files in os.walk(".\\banned_words"):
        for file in files:
            with open(f".\\banned_words\{file}", "r") as file:
                data = json.load(file)
            file.close()
            
            filename = str(file.name)[15:].rstrip(".json")
            to_return[filename] = data
    
    return to_return
async def has_banned_word(message : str, banned_words : list) -> bool:

    for strip in " \"',;.:-_/\\()[]{}<>+-*'¡¿!?|@·#$~%€&¬=^`µ§¶µ":
        message = message.replace(strip, "")

    for word in banned_words:
        if word in message.replace(strip, ""):
            return True
    return False

async def create_config(server_id : str):
    with open (f".\\configs\{server_id}.json", "x") as file:
        json.dump({"welcome_channel": "", "welcome_type": "text", "welcome_image": "", "welcome_message": "Welcome @user to @server", "onjoin_roles": [], "react_roles": {}, "autorole_channels": [], "muted_users": [], "max_warns": 3, "max_mutes": 3, "mute_duration": 10, "max_kicks": 3}, file)
    file.close()
    return None
async def load_config(server_id : str) -> dict[str, str]:
    with open (f".\\configs\{server_id}.json", "r") as file:
        data = json.load(file)
    file.close()
    
    return data
async def save_config(data : dict[str, str], server_id : str) -> None:
    with open (f".\\configs\{server_id}.json", "w") as file:
        json.dump(data, file)
    file.close()

async def load_WMK() -> dict:
    with open("countautomod.json", "r") as file:
        data = json.load(file)
    file.close()
    
    return data
async def save_WMK(data : dict) -> None:
    with open("countautomod.json", "w") as file:
        json.dump(data, file)
    file.close()

async def create_banned_words(server_id : str) -> None:
    with open (f".\\banned_words\{server_id}.json", "x") as file:
        json.dump({"bans": []}, file)
    file.close()
    return None
async def load_banned_words(server_id : str) -> dict:
    with open(f".\\banned_words\{server_id}.json", "r") as file:
        data = json.load(file)
    file.close()
    return data
async def save_banned_words(data : dict, server_id : str) -> None:
    with open(f".\\banned_words\{server_id}.json", "w") as file:
        json.dump(data, file)
    file.close()  

async def format_message(msg : str, member : discord.Member, guild : discord.Guild) -> str:
    
    if "@user" or "@server" in msg:
        msg = msg.replace("@user", f"{member.mention}")
        msg = msg.replace("@server", f"{guild.name}")
    
    return msg
async def format_emoji(emoji : str) -> str:
    if "<:" in emoji:
        limits = ":"
        inside_limit = False
        for letter in emoji:
            if letter is limits:
                inside_limit = not inside_limit
            
            if not inside_limit:
                emoji = emoji.replace(letter, "")
    return emoji

async def interactionuser_has_permissions(interaction : discord.Interaction, permissions : list[str]) -> bool:
    
    user_perms = [permission[0] for permission in interaction.user.guild_permissions if permission[1]]
    ct = 0
    
    for permission in permissions:
        if permission in user_perms:
            ct+=1
    
    return ct == len(permissions)
async def user_has_permissions(member : discord.Member, permissions : list[str]) -> bool:
    
    user_perms = [permission[0] for permission in member.guild_permissions if permission[1]]
    ct = 0
    
    for permission in permissions:
        if permission in user_perms:
            ct+=1
    
    return ct == len(permissions)

