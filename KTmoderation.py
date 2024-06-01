
#*Discord
import discord


#*Tools
from KTtools import load_WMK, save_WMK, load_config, save_config  # noqa: F401
import asyncio
import time

#List adders + unofficial actions
async def add_user(member : discord.Member) -> None:
    warns_mutes_kicks = await load_WMK()
    warns_mutes_kicks[str(member.id)] = [0,0,0]
    await save_WMK(warns_mutes_kicks)

async def add_warn(member : discord.Member) -> None:
    warns_mutes_kicks = await load_WMK()
    warns_mutes_kicks[str(member.id)][0] += 1
    await save_WMK(warns_mutes_kicks)
async def remove_warnlist(member : discord.Member) -> None:
    warns_mutes_kicks = await load_WMK()
    warns_mutes_kicks[str(member.id)][0] -= 1
    await save_WMK(warns_mutes_kicks)
    
async def add_mute(member : discord.Member) -> None:
    warns_mutes_kicks = await load_WMK()
    warns_mutes_kicks[str(member.id)][1] += 1
    await save_WMK(warns_mutes_kicks)
async def remove_mutelist(member : discord.Member) -> None:
    warns_mutes_kicks = await load_WMK()
    warns_mutes_kicks[str(member.id)][1] -= 1
    await save_WMK(warns_mutes_kicks)  
async def muteaction(member : discord.Member) -> None:
    for channel in member.guild.channels:
        await channel.set_permissions(member, send_messages = False, send_messages_in_threads = False, send_voice_messages = False)
async def unmuteaction(member : discord.Member) -> None:
    for channel in member.guild.channels:
        await channel.set_permissions(member, send_messages = True, send_messages_in_threads = True, send_voice_messages = True)

async def add_kick(member : discord.Member) -> None:
    warns_mutes_kicks = await load_WMK()
    warns_mutes_kicks[str(member.id)][2] += 1
    await save_WMK(warns_mutes_kicks)
async def remove_kick(member : discord.Member) -> None:
    warns_mutes_kicks = await load_WMK()
    warns_mutes_kicks[str(member.id)][2] -= 1
    await save_WMK(warns_mutes_kicks)
    
#Moderation commands
async def warn(interaction : discord.Interaction, member : discord.Member, reason : str) -> None:
    warns_mutes_kicks = await load_WMK()
    config = await load_config()
    member_id = str(member.id)
    warn_count = warns_mutes_kicks[member_id][0]
    
    embed = discord.Embed(
        description= f"{member.mention} has been warned for reason:\n\n **{reason}.**",
        colour = discord.Color.dark_gray()
    )
    if warn_count == config["max_warns"]:
        embed.set_footer(text = f"Reached max warns of {config['max_warns']}.\nNot adding to counter.")
    else:
        await add_warn(member)
    
    await interaction.response.send_message(embed = embed)
async def remove_warn(interaction : discord.Interaction, member : discord.Member) -> None:
    warns_mutes_kicks = await load_WMK()
    member_id = str(member.id)
    warn_count = warns_mutes_kicks[member_id][0]
    
    if warn_count > 0:
        await remove_warnlist(member)
        
        embed = discord.Embed(
            description= f"✅ {member.mention} has been removed a warn.",
            colour = discord.Color.green()
        )
        await interaction.response.send_message(embed = embed)
    else:
        embed = discord.Embed(
            description= f"❌ {member.mention} has no warns.",
            colour = discord.Color.red()
        )
        await interaction.response.send_message(embed = embed)
async def remove_all_warns(interaction : discord.Interaction, member : discord.Member) -> None:
    warns_mutes_kicks = await load_WMK()
    member_id = str(member.id)
    
    warns_mutes_kicks[member_id][0] = 0
    await save_WMK(warns_mutes_kicks)
    
    embed = discord.Embed(
        description= f"✅ {member.mention} has been cleared of all warns.",
        colour = discord.Color.green()
    )
    await interaction.response.send_message(embed = embed)

async def mute(interaction : discord.Interaction, member : discord.Member, reason : str, duration : int) -> None:
    warns_mutes_kicks = await load_WMK()
    config = await load_config()
    member_id = str(member.id)
    mute_count = warns_mutes_kicks[member_id][1]
    
    if member_id in config["muted_users"]:
        embed= discord.Embed(
            description= f"{member.mention} is already muted.",
            colour = discord.Color.dark_gray()
        )
        return await interaction.response.send_message(embed = embed, ephemeral=True)
        
    embed= discord.Embed(
            description= f"{member.mention} has been muted for **{duration}** minutes for reason:\n\n **{reason}**.\n\nUnmuted <t:{int(time.time()) + (duration * 60)}:R>**",
            colour = discord.Color.dark_gray()
        )
    if mute_count == config["max_mutes"]:
        embed.set_footer(text="User has reached max mute count. Muting but not adding to counter.")
    else:
        await add_mute(member)
    
    config["muted_users"].append(member_id)
    await save_config(config)
    await interaction.response.send_message(embed = embed)
    await muteaction(member)
    
    await asyncio.sleep(duration * 60)
    
    if member_id in config["muted_users"]:
        await unmuteaction(member)
        config["muted_users"].remove(member_id)
        await save_config(config)
async def unmute(interaction : discord.Interaction, member : discord.Member) -> None:
    config = await load_config()
    member_id = str(member.id)
    
    if member_id in config["muted_users"]:
        config["muted_users"].remove(member_id)
        await save_config(config)
        
        embed = discord.Embed(
            description= f"✅ {member.mention} has been unmuted.",
            colour = discord.Color.green()
        )
        await interaction.response.send_message(embed = embed)
        await unmuteaction(member)
    
    else:
        embed = discord.Embed(
            description= f"❌ {member.mention} is not muted.",
            colour = discord.Color.red()
        )
        await interaction.response.send_message(embed = embed, ephemeral=True)
async def remove_mute(interaction : discord.Interaction, member : discord.Member) -> None:
    warns_mutes_kicks = await load_WMK()
    member_id = str(member.id)
    mute_count = warns_mutes_kicks[member_id][1]
    
    if mute_count > 0:
        await remove_mutelist(member)
        
        embed = discord.Embed(
            description= f"✅ {member.mention} has been removed a mute.",
            colour = discord.Color.green()
        )
        await interaction.response.send_message(embed = embed)
    else:
        embed = discord.Embed(
            description= f"❌ {member.mention} has no mutes.",
            colour = discord.Color.red()
        )
        await interaction.response.send_message(embed = embed)
async def remove_all_mutes(interaction : discord.Interaction, member : discord.Member) -> None:
    warns_mutes_kicks = await load_WMK()
    member_id = str(member.id)
    
    warns_mutes_kicks[member_id][1] = 0
    await save_WMK(warns_mutes_kicks)
    
    embed = discord.Embed(
        description= f"✅ {member.mention} has been cleared of all mutes.",
        colour = discord.Color.green()
    )
    await interaction.response.send_message(embed = embed)

async def kick(interaction : discord.Interaction, member : discord.Member, reason : str) -> None:
    config = await load_config()
    member_id = str(member.id)
    warns_mutes_kicks = await load_WMK()
    kick_count = warns_mutes_kicks[member_id][2]
    
    embed = discord.Embed(
        description= f" {member.mention} has been kicked for reason:\n\n**{reason}**",
        colour = discord.Color.dark_gray()
    )
    if kick_count == config["max_kicks"]:
        embed.set_footer(text="User has reached max kick count. Kicking but not adding to counter.")
    else:
        await add_kick(member)
    
    await interaction.response.send_message(embed = embed)
    await member.kick(reason = reason)