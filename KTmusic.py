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

async def play_next(interaction : discord.Interaction, song : str) -> None:
    server_id = str(interaction.guild.id)
    playlistconfig = await KTtools.load_playlist(server_id)
    playing = searchyt(playlistconfig["playlist"][0])
    
    try:
        playlistconfig["isplaying"] = True
        await KTtools.save_playlist(playlistconfig, server_id)
        musicurl = playing["source"]

        interaction.guild.voice_client.play(discord.FFmpegPCMAudio(musicurl, before_options = "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5", options = "-vn"))
        #Wait for end
        while interaction.guild.voice_client.is_playing() or interaction.guild.voice_client.is_paused():
            await asyncio.sleep(1)
        #Repeat check
        playlistconfig = await KTtools.load_playlist(server_id)
        if not playlistconfig["repeat"] and len(playlistconfig["playlist"]) != 0:
            new_playlist = playlistconfig["playlist"].remove(song) if song in playlistconfig["playlist"] else playlistconfig["playlist"]
            playlistconfig["playlist"] = new_playlist
            await KTtools.save_playlist(playlistconfig, server_id)
        else:
            if len(playlistconfig["playlist"]) != 0 and song in playlistconfig["playlist"]:
                new_playlist = playlistconfig["playlist"]
                new_playlist.append(song)
                new_playlist.remove(song)
                playlistconfig["playlist"] = new_playlist
                await KTtools.save_playlist(playlistconfig, server_id)
    except Exception:
        embed = discord.Embed(
            description= f"❌ I couldn't find and play **{song}**\nIf you used a link, try fetching a new one and try again",
            color = discord.Color.red()
        )
        await interaction.channel.send(embed = embed)
        playlistconfig["playlist"].pop(0)
        await KTtools.save_playlist(playlistconfig, server_id)
    
    playlistconfig = await KTtools.load_playlist(server_id)
    if len(playlistconfig["playlist"]) != 0:
        #Shuffle check
        if not playlistconfig["shuffle"]:
            await play_next(interaction, playlistconfig["playlist"][0])
        else:
            idxnext = randint(0, len(playlistconfig["playlist"])-1)
            playlistconfig["playlist"][0], playlistconfig["playlist"][idxnext] = playlistconfig["playlist"][idxnext], playlistconfig["playlist"][0]
            await KTtools.save_playlist(playlistconfig, server_id)
            
            playlistconfig = await KTtools.load_playlist(server_id)
            await play_next(interaction, playlistconfig["playlist"][0])
    else:
        await KTtools.save_playlist({"playlist": "[]", "isplaying": "False"}, server_id)
        embed = discord.Embed(
            description= "Playlist finished!",
            color = discord.Color.dark_purple()
        )
        await interaction.channel.send(embed = embed)
