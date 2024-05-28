
#*Discord
import discord

#*Tools
from KTtools import load_WMK, save_WMK, load_config, save_config  # noqa: F401

#Adders
async def add_user(member : discord.Member) -> None:
    warns_mutes_kicks = await load_WMK()
    warns_mutes_kicks[str(member.id)] = [0,0,0]
    await save_WMK(warns_mutes_kicks)

async def add_warn(member : discord.Member) -> None:
    warns_mutes_kicks = await load_WMK()
    warns_mutes_kicks[str(member.id)][0] += 1
    await save_WMK(warns_mutes_kicks)
async def remove_warn(member : discord.Member) -> None:
    warns_mutes_kicks = await load_WMK()
    warns_mutes_kicks[str(member.id)][0] -= 1
    await save_WMK(warns_mutes_kicks)
    
async def add_mute(member : discord.Member) -> None:
    warns_mutes_kicks = await load_WMK()
    warns_mutes_kicks[str(member.id)][1] += 1
    await save_WMK(warns_mutes_kicks)
async def remove_mute(member : discord.Member) -> None:
    warns_mutes_kicks = await load_WMK()
    warns_mutes_kicks[str(member.id)][1] -= 1
    await save_WMK(warns_mutes_kicks)  

async def add_kick(member : discord.Member) -> None:
    warns_mutes_kicks = await load_WMK()
    warns_mutes_kicks[str(member.id)] = [0,0,1]
    await save_WMK(warns_mutes_kicks)
async def remove_kick(member : discord.Member) -> None:
    warns_mutes_kicks = await load_WMK()
    warns_mutes_kicks[str(member.id)][2] -= 1
    await save_WMK(warns_mutes_kicks)
    
#Manual commands
async def manual_warn(interaction : discord.Interaction, member : discord.Member, reason : str) -> None:
    warns_mutes_kicks = await load_WMK()
    config = await load_config()
    member_id = str(member.id)
        
    if warns_mutes_kicks[member_id][0] < config["max_warns"]:
        await add_warn(member)
        
        embed = discord.Embed(
            description= f"{member.mention} has been warned for reason:\n\n **{reason}.**",
            colour = discord.Color.dark_gray()
        )
        await interaction.response.send_message(embed = embed)
    else:
        embed = discord.Embed(
            description= f"❌ {member.mention} has reached the maximum number of warns.",
            colour = discord.Color.red()
        )
        await interaction.response.send_message(embed = embed)
async def manual_remove_warn(interaction : discord.Interaction, member : discord.Member) -> None:
    warns_mutes_kicks = await load_WMK()
    member_id = str(member.id)
    
    if warns_mutes_kicks[member_id][0] > 0:
        await remove_warn(member)
        
        embed = discord.Embed(
            description= f"✅ {member.mention} has been removed a warned.",
            colour = discord.Color.green()
        )
        await interaction.response.send_message(embed = embed)
    else:
        embed = discord.Embed(
            description= f"❌ {member.mention} has no warns.",
            colour = discord.Color.red()
        )
        await interaction.response.send_message(embed = embed)
async def manual_remove_all_warns(interaction : discord.Interaction, member : discord.Member) -> None:
    warns_mutes_kicks = await load_WMK()
    member_id = str(member.id)
    
    warns_mutes_kicks[member_id][0] = 0
    await save_WMK(warns_mutes_kicks)
    
    embed = discord.Embed(
        description= f"✅ {member.mention} has been removed all warns.",
        colour = discord.Color.green()
    )
    await interaction.response.send_message(embed = embed)
    
#TODO: Manual mutes, Manual kicks and Manual bans
#TODO: Automatic versions