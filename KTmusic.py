from yt_dlp import YoutubeDL
import KTtools
import discord
from random import randint
import asyncio


def searchyt(query : str) -> dict[str : str]:
    with YoutubeDL({"format": "bestaudio", "noplaylist" : "True"}) as ydl:
        try:
            info = ydl.extract_info("ytsearch:%s" % query, download=False)["entries"][0]
        except Exception:
            return False
    
    return {"title": info["title"], "source": info["url"]}

#TODO ARREGLAR SHUFFLE
async def play_next(interaction : discord.Interaction, song : str, nextidx : int) -> None:
    server_id = str(interaction.guild.id)
    playlistconfig = await KTtools.load_playlist(server_id)
    playing = searchyt(playlistconfig["playlist"][nextidx])
    
    playlistconfig["isplaying"] = True
    await KTtools.save_playlist(playlistconfig, server_id)

    musicurl = playing["source"]

    #Repeat
    if not playlistconfig["repeat"]:
        new_playlist = playlistconfig["playlist"].remove(song)
        await KTtools.save_playlist(playlistconfig, server_id)
    else:
        new_playlist = playlistconfig["playlist"]
        new_playlist.append(song)
        new_playlist.remove(song)
        playlistconfig["playlist"] = new_playlist
        await KTtools.save_playlist(playlistconfig, server_id)
    
    interaction.guild.voice_client.play(discord.FFmpegPCMAudio(musicurl, before_options = "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5", options = "-vn"))
    
    while interaction.guild.voice_client.is_playing() or interaction.guild.voice_client.is_paused():
        await asyncio.sleep(1)
    
    playlistconfig = await KTtools.load_playlist(server_id)
    if len(playlistconfig["playlist"]) != 0:
        if not playlistconfig["shuffle"]:
            await play_next(interaction, playlistconfig["playlist"][0], 0)
        else:
            idxnext = randint(0, len(playlistconfig["playlist"])-1)
            await play_next(interaction, playlistconfig["playlist"][idxnext], idxnext)
    else:
        await KTtools.save_playlist({"playlist": "[]", "isplaying": "False"}, server_id)
        embed = discord.Embed(
            description = "Playlist ended!",
            color = discord.Color.dark_purple()
        )
        await interaction.channel.send(embed = embed)

