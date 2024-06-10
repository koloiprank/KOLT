import sqlite3
import discord
import os

def eval_no_error(data : str) -> dict | list:
    try:
        return eval(data)
    except Exception:
        return data
#!REDUNTANT! USE os.path.exists(file)
#TODO replace all find_file with os.path.exists()
def find_file(filename : str, path : str) -> str:
    for root, dirs, files in os.walk(path):
        if filename in files:
            return os.path.join(root, filename)

def get_banned_words_per_server() -> dict[str: list[str]]:
    to_return = {}
    connexion = sqlite3.connect("configs.db")
    cursor = connexion.cursor()

    cursor.execute("SELECT * FROM bannedwords")
    data = cursor.fetchall()
    connexion.close()

    for row in data:
        to_return[row[0]] = eval_no_error(row[1])
    return to_return
async def has_banned_word(message : str, banned_words : list) -> bool:

    for strip in " \"',;.:-_/\\()[]{}<>+-*'¡¿!?|@·#$~%€&¬=^`µ§¶µ":
        message = message.replace(strip, "")

    for word in banned_words:
        if word in message.replace(strip, ""):
            return True
    return False

async def create_config(server_id : str):
    connexion = sqlite3.connect("configs.db")
    cursor = connexion.cursor()
    
    try:
        cursor.execute("""CREATE TABLE serverconfig (
            server_id text PRIMARY KEY,
            welcome_channel text,
            welcome_type text,
            welcome_image text,
            welcome_message text,
            onjoin_roles text,
            react_roles text,
            autorole_channels text,
            muted_users text,
            max_warns integer,
            max_mutes integer,
            mute_duration integer,
            max_kicks integer
            )""")
        connexion.commit()
    except Exception:
        ...
    
    try:
        cursor.execute(f"INSERT INTO serverconfig VALUES('{server_id}', '', 'text', '', 'Welcome @user to @server', '[]', '{{}}', '[]', '[]', 3, 3, 10, 3)")
        connexion.commit()
    except Exception:
        print("[DB.CONFIGS.WARNING]>>>Could not insert into table, server_id already exists!!!")
    
    connexion.close()
async def load_config(server_id : str) -> dict[str, str]:
    connexion = sqlite3.connect("configs.db")
    cursor = connexion.cursor()
    
    cursor.execute("SELECT * FROM serverconfig WHERE server_id=:server_id", {"server_id": server_id})
    data = cursor.fetchone()
    connexion.close()
    config_template = ["server_id", 
                       "welcome_channel", 
                       "welcome_type", 
                       "welcome_image", 
                       "welcome_message", 
                       "onjoin_roles", 
                       "react_roles", 
                       "autorole_channels", 
                       "muted_users", 
                       "max_warns", 
                       "max_mutes", 
                       "mute_duration", 
                       "max_kicks"]
    
    return {config_template[i] : eval_no_error(data[i]) for i in range(len(config_template))}
async def save_config(data : dict[str, str], server_id : str) -> None:
    connexion = sqlite3.connect("configs.db")
    cursor = connexion.cursor()
    
    for key in data:
        cursor.execute(f"UPDATE serverconfig SET {key} = ? WHERE server_id = {server_id}", (f"{data[key]}",))
        connexion.commit()
    
    connexion.close()

async def create_WMK(server_id : str) -> None:
    connexion = sqlite3.connect("configs.db")
    cursor = connexion.cursor()
    
    try:
        cursor.execute("""CREATE TABLE punishcounts (
            server_id text PRIMARY KEY,
            count text)""")
        connexion.commit()
    except Exception:
        ...
    
    try:
        cursor.execute(f"INSERT INTO punishcounts VALUES('{server_id}', '{{}}')")
        connexion.commit()
    except Exception:
        print("[DB.WMK.WARNING]>>>Could not insert into table, server_id already exists!!!")
async def load_WMK(server_id : str) -> dict:
    connexion = sqlite3.connect("configs.db")
    cursor = connexion.cursor()
    
    cursor.execute("SELECT * FROM punishcounts WHERE server_id=:server_id", {"server_id": server_id})
    data = cursor.fetchone()
    connexion.close()
    
    return eval_no_error( eval_no_error(data)[1] )
async def save_WMK(data : dict, server_id : str) -> None:
    connexion = sqlite3.connect("configs.db")
    cursor = connexion.cursor()

    cursor.execute(f"UPDATE punishcounts SET 'count' = ? WHERE server_id = {server_id}", (str(data),))
    connexion.commit()
    
    connexion.close()

async def create_banned_words(server_id : str) -> None:
    connexion = sqlite3.connect("configs.db")
    cursor = connexion.cursor()
    
    try:
        cursor.execute("""CREATE TABLE bannedwords (
            server_id text PRIMARY KEY,
            bans text)""")
        connexion.commit()
    except Exception:
        ...
    
    try:
        cursor.execute(f"INSERT INTO bannedwords VALUES('{server_id}', '[]')")
        connexion.commit()
    except Exception:
        print("[DB.BANNEDWORDS.WARNING]>>>Could not insert into table, server_id already exists!!!")
async def load_banned_words(server_id : str) -> dict:
    connexion = sqlite3.connect("configs.db")
    cursor = connexion.cursor()
    
    cursor.execute("SELECT * FROM bannedwords WHERE server_id=:server_id", {"server_id": server_id})
    data = cursor.fetchone()
    connexion.close()
    
    return eval_no_error(data[1])
async def save_banned_words(data : list, server_id : str) -> None:
    connexion = sqlite3.connect("configs.db")
    cursor = connexion.cursor()
    
    cursor.execute(f"UPDATE bannedwords SET 'bans' = ? WHERE server_id = {server_id}", (str(data),))
    connexion.commit()
    
    connexion.close()

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

async def create_playlist(server_id : str) -> None:
    connexion = sqlite3.connect("configs.db")
    cursor = connexion.cursor()
    
    try:
        cursor.execute("""CREATE TABLE playlist (
            server_id text PRIMARY KEY,
            playlist text,
            isplaying text,
            repeat text,
            shuffle text)""")
        connexion.commit()
    except Exception:
        ...
    
    try:
        cursor.execute(f"INSERT INTO playlist VALUES('{server_id}', '[]', 'False', 'False', 'False')")
        connexion.commit()
    except Exception:
        print("[DB.PLAYLIST.WARNING]>>>Could not insert into table, server_id already exists!!!")
async def load_playlist(server_id : str) -> dict:
    connexion = sqlite3.connect("configs.db")
    cursor = connexion.cursor()
    
    cursor.execute("SELECT * FROM playlist WHERE server_id=:server_id", {"server_id": server_id})
    data = cursor.fetchone()
    connexion.close()
    
    playlist_template = ["server_id", "playlist", "isplaying", "repeat", "shuffle"]
    to_return = {}
    for idx in range (len(playlist_template)):
        to_return[playlist_template[idx]] = eval_no_error(data[idx])
    
    return to_return  
async def save_playlist(data : list, server_id : str) -> None:
    connexion = sqlite3.connect("configs.db")
    cursor = connexion.cursor()
    
    for key in data:
        cursor.execute(f"UPDATE playlist SET {key} = ? WHERE server_id = {server_id}", (f"{data[key]}",))
        connexion.commit()
    
    connexion.close()


#DEV - DO NOT USE
def resetplaylist()-> None:
    connexion = sqlite3.connect("configs.db")
    cursor = connexion.cursor()
    data = {"playlist": "[]", "isplaying": "False", "repeat": "False", "shuffle": "False"}
    server_id = "1067917569161441402"
    
    for key in data:
        cursor.execute(f"UPDATE playlist SET {key} = ? WHERE server_id = {server_id}", (f"{data[key]}",))
        connexion.commit()
    
    connexion.close()
def dropplaylist()-> None:
    connexion = sqlite3.connect("configs.db")
    cursor = connexion.cursor()
    cursor.execute("DROP TABLE playlist")
    connexion.commit()
    connexion.close()

if __name__ == "__main__":
    ...