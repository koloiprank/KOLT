from yt_dlp import YoutubeDL
import KTtools
import discord
from random import randint
import asyncio
from youtube_search import YoutubeSearch


def searchyt(query : str) -> dict[str : str]:
    with YoutubeDL({"format": "bestaudio", "noplaylist" : "True"}) as ydl:
        try:
            info = ydl.extract_info("ytsearch:%s" % query, download=False)["entries"][0]
        except Exception:
            return False
    
    return {"title": info["title"], "source": info["url"]}

def get_youtube_search_info(query : str) -> dict[str : str]:
    return YoutubeSearch(query, max_results=1).to_dict()[0]

def create_playlist_embed(playlistconfig : dict) -> discord.Embed:
    upnext_playlist = ""
    for idx in range(1, 12):
        if idx != 11:
            try:
                upnext_playlist += f"- **{idx}.** {playlistconfig['playlist'][idx]}\n"
            except Exception:
                break
        elif idx == 11:
            upnext_playlist += "And more..."
    
    embed = discord.Embed(
        title = "**CURRENTLY PLAYING**",
        description = f"### **Now playing:**\n{playlistconfig['playlist'][0]}\n### **By:**\n{get_youtube_search_info(playlistconfig['playlist'][0])['channel']}\n\n### **Up next:**\n{upnext_playlist}",
        color = discord.Color.dark_purple(),
        url = f"https://youtube.com{get_youtube_search_info(playlistconfig['playlist'][0])['url_suffix']}"
    )
    embed.set_footer(text = f"Repeat: {'on' if playlistconfig['repeat'] else 'off'}\nShuffle: {'on' if playlistconfig['shuffle'] else 'off'}")
    try:
        embed.set_thumbnail(url = get_youtube_search_info(playlistconfig["playlist"][0])["thumbnails"][0])
    except Exception: ...
    return embed

async def play_next(interaction : discord.Interaction, song : str) -> None:
    server_id = str(interaction.guild.id)
    playlistconfig = await KTtools.load_playlist(server_id)
    playlistconfig["isplaying"] = True
    playing = searchyt(playlistconfig["playlist"][0])
    
    if playing:
        #Create embed
        embed = create_playlist_embed(playlistconfig)
        await interaction.channel.send(embed = embed)
        musicurl = playing["source"]
        
        #Play
        interaction.guild.voice_client.play(discord.FFmpegPCMAudio(musicurl, before_options = "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5", options = "-vn"))
        #Wait for end
        while interaction.guild.voice_client.is_playing() or interaction.guild.voice_client.is_paused():
            await asyncio.sleep(1)
        #Repeat check
        playlistconfig = await KTtools.load_playlist(server_id)
        if not playlistconfig["repeat"]:
            playlistconfig["playlist"].remove(song)
            await KTtools.save_playlist(playlistconfig, server_id)
        else:
            new_playlist = playlistconfig["playlist"]
            new_playlist.append(song)
            new_playlist.remove(song)
            
            playlistconfig["playlist"] = new_playlist
            await KTtools.save_playlist(playlistconfig, server_id)
    else:
        embed = discord.Embed(
            description= f"❌ I couldn't find and play **{song}**\nDeleting from playlist, you may retry again",
            color = discord.Color.red()
        )
        await interaction.channel.send(embed = embed)
        playlistconfig["playlist"].remove(song)
        await KTtools.save_playlist(playlistconfig, server_id)

    playlistconfig = await KTtools.load_playlist(server_id)
    if len(playlistconfig["playlist"]) > 0:
        #Shuffle check
        if not playlistconfig["shuffle"] or len(playlistconfig["playlist"]) == 1:
            await play_next(interaction, playlistconfig["playlist"][0])
        else:
            idxnext = randint(0, len(playlistconfig["playlist"])) if not playlistconfig["repeat"] else randint(0, len(playlistconfig["playlist"]) - 1)
            await play_next(interaction, playlistconfig["playlist"][idxnext])
    else:
        embed = discord.Embed(
            description= "### Playlist finished!",
            color = discord.Color.dark_purple()
        )
        await interaction.channel.send(embed = embed)
        await KTtools.save_playlist({"playlist": "[]", "isplaying": "False", "next_song": ""}, server_id)
