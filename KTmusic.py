from youtube_dl import YoutubeDL
import KTtools
import discord
from random import randint

def searchyt(query : str) -> dict[str : str]:
    with YoutubeDL({"format": "bestaudio"}) as ydl:
        try:
            info = ydl.extract_info(f"ytsearch:{query}", download=False)["entries"][0]
        except Exception:
            return False
    
    return {"source": info["formats"[0]["url"]], "title": info["title"]}

async def play_next(interaction : discord.Interaction) -> None:
    server_id = str(interaction.guild.id)
    if len(KTtools.load_playlist[server_id]) > 0:
        await KTtools.save_playlist({"isplaying": "True"}, str(interaction.guild.id))
        
        if await KTtools.load_playlist(server_id)["shuffle"] is True:
            musicurl = await KTtools.load_playlist[server_id][randint(0, len(await KTtools.load_playlist[server_id]["playlist"]))]["source"]
        else:
            musicurl = await KTtools.load_playlist[server_id][0]["source"]
        if await KTtools.load_playlist(server_id)["repeat"] is False:
            await KTtools.save_playlist({"playlist": await KTtools.load_playlist[server_id][1:]}, str(interaction.guild.id))
        
        interaction.guild.voice_client.play(discord.FFmpegPCMAudio(musicurl), after=lambda e: play_next(interaction))
    else:
        await KTtools.save_playlist({"playlist": "[]", "isplaying": "False"}, str(interaction.guild.id))