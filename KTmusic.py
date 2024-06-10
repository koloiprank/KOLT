from yt_dlp import YoutubeDL
from youtube_search import YoutubeSearch
import discord
from random import randint
import asyncio
import KTtools


async def searchyt(query : str, loop = None, stream = False) -> dict[str : str]:
    ydloptions = {
    'format': 'bestaudio/',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
    #'quiet': True,
    "filter": "audioonly",
    'skip_download': True,
    }
    
    with YoutubeDL(ydloptions) as ydl:
        loop = loop or asyncio.get_event_loop()
        try:
            info = await loop.run_in_executor(None, lambda: ydl.extract_info("ytsearch:%s" % query, download=False))
            if 'entries' in info:
                info = info["entries"][0]
            filename = info['title'] if stream else ydl.prepare_filename(info)
        except Exception:
            return False
    return {"title": filename, "source": info["url"]}

def get_youtube_search_info(query : str) -> dict[str : str]:
    return YoutubeSearch(query, max_results=1).to_dict()[0]

def create_playlist_embed(playlistconfig : dict) -> discord.Embed:
    upnext_playlist = "" if not playlistconfig["shuffle"] else "***Shuffled! Order may change each time a song plays!***\n"
    for idx in range(1, 12):
        if idx != 11:
            try:
                upnext_playlist += f"- **{idx}.** {playlistconfig['playlist'][idx]}\n" if not playlistconfig["shuffle"] else f"- {playlistconfig['playlist'][idx]}\n"
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

async def repeat_check(playlistconfig) -> list[str]:
    playlist = playlistconfig["playlist"]
    repeat = playlistconfig["repeat"]
    if repeat:
        playlist.append(playlist[0])
        playlist.pop(0)
    elif not repeat:
        playlist.pop(0)
    
    return playlist
async def shuffle_check(playlistconfig) -> list[str]:
    playlist = playlistconfig["playlist"]
    shuffle = playlistconfig["shuffle"]
    
    if shuffle:
        nextsongidx = randint(0, len(playlist) - 1)
        playlist[nextsongidx], playlist[0] = playlist[0], playlist[nextsongidx]

    elif not shuffle or len(playlist) == 1:
        pass
    
    return playlist

async def play_song(interaction : discord.Interaction, song : str) -> None:
    server_id = str(interaction.guild.id)
    playlistconfig = await KTtools.load_playlist(server_id)
    
    loop = asyncio.get_event_loop()
    embed = await loop.run_in_executor(None, lambda: create_playlist_embed(playlistconfig))
    await interaction.channel.send(embed = embed)
    
    playing = await searchyt(playlistconfig["playlist"][0])
    if playing:
        musicurl = playing["source"]
        interaction.guild.voice_client.play(discord.FFmpegPCMAudio(musicurl, before_options = "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5", options = "-vn"))
        
        while interaction.guild.voice_client.is_playing() or interaction.guild.voice_client.is_paused():
            await asyncio.sleep(1)
        
        playlistconfig = await KTtools.load_playlist(server_id)
        playlistconfig["playlist"] = await repeat_check(playlistconfig = playlistconfig)
        playlistconfig["playlist"] = await shuffle_check(playlistconfig = playlistconfig)
        await KTtools.save_playlist(playlistconfig, server_id)
        
        await play_next(interaction = interaction)  
                                         
    else:
        embed = discord.Embed(
            description= f"❌ I couldn't find and play **{song}**\nDeleting from playlist.",
            color = discord.Color.red()
        )
        await interaction.channel.send(embed = embed)
        
        playlistconfig["playlist"].pop(0)
        await KTtools.save_playlist({"playlist": "[]", "isplaying": "False"}, server_id)
        try:
            interaction.guild.voice_client.stop()
        except Exception: ...
        
        embed = discord.Embed(
            description= "## Playlist finished!",
            color = discord.Color.dark_purple()
            )
        await interaction.channel.send(embed = embed)
     
async def play_next(interaction : discord.Interaction) -> None:
    server_id = str(interaction.guild.id)
    playlistconfig = await KTtools.load_playlist(server_id)
    
    if len(playlistconfig["playlist"]) > 0:
        loop = asyncio.get_event_loop()
        embed = await loop.run_in_executor(None, lambda: create_playlist_embed(playlistconfig))
        await interaction.channel.send(embed = embed)
        
        playing = await searchyt(playlistconfig["playlist"][0])
        if playing:
            musicurl = playing["source"]
            interaction.guild.voice_client.play(discord.FFmpegPCMAudio(musicurl, before_options = "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5", options = "-vn"))
                                                        
            while interaction.guild.voice_client.is_playing() or interaction.guild.voice_client.is_paused():
                await asyncio.sleep(1)
            
            playlistconfig = await KTtools.load_playlist(server_id)
            playlistconfig["playlist"] = await repeat_check(playlistconfig = playlistconfig)
            playlistconfig["playlist"] = await shuffle_check(playlistconfig = playlistconfig)
            await KTtools.save_playlist(playlistconfig, server_id)
            
            await play_next(interaction = interaction)
            
        else:
            embed = discord.Embed(
                description= f"❌ I couldn't find and play **{playlistconfig['playlist'][0]}**\nDeleting from playlist.",
                color = discord.Color.red()
            )
            await interaction.channel.send(embed = embed)
            
            playlistconfig["playlist"].pop(0)
            await KTtools.save_playlist(playlistconfig, server_id)
            
            await play_next(interaction)
    else:
        await KTtools.save_playlist({"playlist": "[]", "isplaying": "False"}, server_id)
        embed = discord.Embed(
            description= "## Playlist finished!",
            color = discord.Color.dark_purple()
            )
        await interaction.channel.send(embed = embed)

    
    