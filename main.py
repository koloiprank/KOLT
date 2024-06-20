
#*Discord
import discord
from discord import Intents, app_commands
from discord.ext import commands, tasks

#*OS+tools
from typing import Final
import os
from dotenv import load_dotenv
import logging
import time
import asyncio
from unidecode import unidecode
from pytube import Playlist
from random import choice

#*Custom modules
import KTwelcome
import KTtools
import KTautorole
import KTmoderation
import KTmusic
import KTmisc
from reset_config_playlist import reset_all_playlists

#!TOKEN
load_dotenv()
TOKEN : Final[str] = os.getenv('DISCORD_TOKEN')
intents = Intents.all()
client = commands.Bot(command_prefix = "!" ,intents = intents)
#tree = app_commands.CommandTree(client)


#!FUNC
#*On first join
@client.event
async def on_guild_join(guild):
    general = discord.utils.find(lambda x: x.name == 'general',  guild.text_channels)
    if general and general.permissions_for(guild.me).send_messages:
        embed=discord.Embed(title="**--- Hello everyone!! ---**", description=f"""
        Thanks for adding me to **{guild.name}**!
        You can use the `/help` command to get started!
        """, color=discord.Color.dark_purple())
        await general.send(embed=embed)
    
    await KTtools.create_config(str(guild.id))
    await KTtools.create_WMK(str(guild.id))
    await KTtools.create_banned_words(str(guild.id))
    await KTtools.create_playlist(str(guild.id))
    
    global banned_words_per_server
    banned_words_per_server = KTtools.get_banned_words_per_server()


#*Chat logging + Automod
if os.path.exists("configs.db"):
    banned_words_per_server = KTtools.get_banned_words_per_server()
@client.event
async def on_message(message: discord.Message):
    author = message.author
    channel = message.channel
    content = message.content
    
    if message.author != client.user:
        print(f">>> [{channel}]{author}: {content}")
        
        formated_content = unidecode(content.lower())
        
        if not (message.author.bot or message.author == message.guild.owner or await KTtools.user_has_permissions(message.author, ["administrator"])):
            if await KTtools.has_banned_word(formated_content, banned_words_per_server[str(message.guild.id)]):
                
                wmk = await KTtools.load_WMK(str(message.guild.id))
                config = await KTtools.load_config(str(message.guild.id))
                
                member = message.author
                max_warns = config["max_warns"]
                max_mutes = config["max_mutes"]
                max_kicks = config["max_kicks"]
                mute_duration = config["mute_duration"]
                
                await message.delete()
                
                if str(member.id) not in wmk:
                    await KTmoderation.add_user(member)
                    wmk = await KTtools.load_WMK(str(message.guild.id))
                
                if wmk[str(member.id)][0] < config["max_warns"]:
                    await KTmoderation.add_warn(member)
                    embed = discord.Embed(
                    description= f"{member.mention} has been warned for reason:\n\n **Using one/various banned word/s**",
                    colour = discord.Color.dark_gray()
                    )
                    embed.set_footer(text = f"Warnings left until mute: {max_warns - wmk[str(member.id)][0]-1}")
                    await channel.send(embed = embed)
                elif wmk[str(member.id)][1] < config["max_mutes"]:
                    await KTmoderation.add_mute(member)
                    embed = discord.Embed(
                    description= f"{member.mention} has been muted for **{mute_duration}** minutes for reason:\n\n **Using one/various banned word/s**\n\nUnmuted <t:{int(time.time()) + (mute_duration * 60)}:R>",
                    colour = discord.Color.dark_gray()
                    )
                    embed.set_footer(text = f"Mutes left until kick: {max_mutes - wmk[str(member.id)][1]-1}")
                    await channel.send(embed = embed)
                    
                    config["muted_users"].append(str(member.id))
                    await KTtools.save_config(config, str(message.guild.id))
                    await KTmoderation.muteaction(member)
                    
                    await asyncio.sleep(config["mute_duration"] * 60)

                    if str(member.id) in config["muted_users"]:
                        await KTmoderation.unmuteaction(member)
                        config["muted_users"].remove(str(member.id))
                        await KTtools.save_config(config, str(message.guild.id))
                elif wmk[str(member.id)][2] < config["max_kicks"]:
                    await KTmoderation.add_kick(member)
                    embed = discord.Embed(
                    description= f"{member.mention} has been kicked for reason:\n\n **Using one/various banned word/s**",
                    colour = discord.Color.dark_gray()
                    )
                    embed.set_footer(text = f"Kicks left until ban: {max_kicks - wmk[str(member.id)][2]-1}")
                    await channel.send(embed = embed)
                    await member.kick(reason="Using one/various banned word/s after reaching max warns and max mutes")
                else:
                    embed = discord.Embed(
                    description= f"{member.mention} has been banned for reason:\n\n **Using one/various banned word/s**",
                    colour = discord.Color.dark_gray()
                    )
                    await channel.send(embed = embed)
                    await member.ban(reason="Using one/various banned word/s after reaching max warns, max mutes and max kicks")


#*React event
@client.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    user = payload.member
    config = await KTtools.load_config(str(payload.guild_id))
    reaction = str(payload.emoji.name) 
    
    if reaction in config["react_roles"] and str(payload.channel_id) in config["autorole_channels"]:
        role = config["react_roles"][reaction]
        
        if not user.bot:
            await user.add_roles(discord.Object(id = role))
            print(f"{user} has been given the role {role} from reaction {reaction}")
@client.event
async def on_raw_reaction_remove(payload: discord.RawReactionActionEvent):
    guild_id = payload.guild_id
    guild = discord.utils.find(lambda g : g.id == guild_id, client.guilds)
    
    user = guild.get_member(payload.user_id)
    config = await KTtools.load_config(str(payload.guild_id))
    reaction = str(payload.emoji.name) 
    
    if reaction in config["react_roles"] and str(payload.channel_id) in config["autorole_channels"]:
        role = config["react_roles"][reaction]
        
        if not user.bot:
            await user.remove_roles(discord.Object(id = role))
            print(f"{user} has been cleared of the role {role} from reaction {reaction}")
 
 
#*Member join event  
@client.event
async def on_member_join(member: discord.Member):
    config = await KTtools.load_config(str(member.guild.id))
    channel = member.guild.get_channel(int(config["welcome_channel"]))
    
    if config["welcome_channel"]:
        if config["welcome_type"] == "message":
            
            embed = discord.Embed(
                title="**WELCOME!!**",
                description= await KTwelcome.create_welcome_message(member, config),
                color=discord.Color.dark_gold()
            )
            await channel.send(embed = embed)
        
        elif config["welcome_type"] == "image":
            
            if await KTwelcome.create_welcome_image(member, config) is not None:
                await channel.send(file = await KTwelcome.create_welcome_image(member, config))
            
            else:
                embed = discord.Embed(
                description= "❌ Couldn't send image.\nTry checking the image link is valid and setting it up again with /setwelcome .",
                colour = discord.Color.red()
                )
            
                await channel.send(embed = embed)
        
        elif config["welcome_type"] == "both":
            embed = discord.Embed(
                title="**WELCOME!!**",
                description= await KTwelcome.create_welcome_message(member, config),
                color=discord.Color.dark_gold()
            )
            
            await channel.send(embed = embed)
            
            if await KTwelcome.create_welcome_image(member, config) is not None:
                
                await channel.send(file = await KTwelcome.create_welcome_image(member, config))
            
            else:
                embed = discord.Embed(
                description= "❌ Couldn't send image.\nTry checking the image link is valid and setting it up again with /setwelcome .",
                colour = discord.Color.red()
                )
            
                await channel.send(embed = embed)
    
    role_list = config["onjoin_roles"]
    for role in role_list:
        await member.add_roles(discord.Object(role))


#*Command Cogs
#Welcome
class Welcomer(commands.Cog):
    def __init__(self, client):
        self.client = client
 
    @app_commands.command(name = "setwelcomechannel", description = "Opens a dropdown menu to set your automatic welcome and goodbye channel")
    async def set_welcome_channel(self, interaction : discord.Interaction) -> None:
        
        permissions = ["manage_channels", "manage_messages"]
        has_perms = await KTtools.interactionuser_has_permissions(interaction, permissions) or await KTtools.interactionuser_has_permissions(interaction, ["administrator"])
        
        if has_perms:
            await KTwelcome.select_welcome_channel(interaction)
        else:
            embed = discord.Embed(
                description = "❌ You don't have permission to use this command.",
                color = discord.Color.red()
            )
            await interaction.response.send_message(embed = embed, ephemeral=True)

    @app_commands.command(name = "setwelcome", description= "Opens an embed with buttons to set your automatic welcome and goodbye message")
    async def set_welcome_message(self, interaction : discord.Interaction) -> None:
        permissions = ["manage_channels", "manage_messages"]
        has_perms = await KTtools.interactionuser_has_permissions(interaction, permissions) or await KTtools.interactionuser_has_permissions(interaction, ["administrator"])
        
        if has_perms:
            await KTwelcome.select_welcome(interaction)
        else:
            embed = discord.Embed(
                description = "❌ You don't have permission to use this command.",
                color = discord.Color.red()
            )
            await interaction.response.send_message(embed = embed, ephemeral=True)

    @app_commands.command(name = "testwelcome", description = "Test the welcome message")
    async def testwelcome(self, interaction : discord.Interaction) -> None:
        permissions = ["manage_channels", "manage_messages"]
        has_perms = await KTtools.interactionuser_has_permissions(interaction, permissions) or await KTtools.interactionuser_has_permissions(interaction, ["administrator"])
        
        if has_perms:
            config = await KTtools.load_config(str(interaction.guild.id))
            
            try: 
                interaction.guild.get_channel(int(config["welcome_channel"]))
            except Exception:
                embed = discord.Embed(
                    description = "❌ Welcome channel not set.",
                    color = discord.Color.red()
                )
                await interaction.response.send_message(embed = embed, ephemeral=True)
                return
            
            if config["welcome_type"] == "message":
                
                embed = discord.Embed(
                    title="**WELCOME!!**",
                    description= await KTwelcome.create_welcome_message(interaction.user, config),
                    color=discord.Color.dark_gold()
                )
                
                await interaction.response.send_message("Done!\nCheck the set welcome channel.", ephemeral = True)
                await interaction.guild.get_channel(int(config["welcome_channel"])).send(embed = embed)

            elif config["welcome_type"] == "image":
                
                if await KTwelcome.create_welcome_image(interaction.user, config) is not None:
                    
                    await interaction.response.send_message("Done!\nCheck the set welcome channel.", ephemeral = True)
                    await interaction.guild.get_channel(int(config["welcome_channel"])).send(file = await KTwelcome.create_welcome_image(interaction.user, config))
                
                else:
                    
                    embed = discord.Embed(
                    description= "❌ Couldn't send image.\nTry checking the image link is valid and setting it up again with /setwelcome .",
                    colour = discord.Color.red()
                    )
                    
                    await interaction.response.send_message("ERROR", ephemeral = True)
                    await interaction.guild.get_channel(int(config["welcome_channel"])).send(embed = embed)

            elif config["welcome_type"] == "both":
                
                embed = discord.Embed(
                    title="**WELCOME!!**",
                    description= str(await KTwelcome.create_welcome_message(interaction.user, config)),
                    color=discord.Color.dark_gold()
                )
                
                await interaction.response.send_message("Done!\nCheck the set welcome channel.", ephemeral = True)
                await interaction.guild.get_channel(int(config["welcome_channel"])).send(embed = embed)
                
                if await KTwelcome.create_welcome_image(interaction.user, config) is not None:
                    
                    await interaction.guild.get_channel(int(config["welcome_channel"])).send(file = await KTwelcome.create_welcome_image(interaction.user, config))
                
                else:
                    
                    embed = discord.Embed(
                    description= "❌ Couldn't send image.\nTry checking the image link is valid and setting it up again with /setwelcome .",
                    colour = discord.Color.red()
                    )
                
                    await interaction.guild.get_channel(int(config["welcome_channel"])).send(embed = embed)
        else:
            embed = discord.Embed(
                description = "❌ You don't have permission to use this command.",
                color = discord.Color.red()
            )
            await interaction.response.send_message(embed = embed, ephemeral=True)
#Autorole
async def is_member_punishable(interaction : discord.Interaction, member : discord.Member, mode : str) -> bool:
    
    if str(member.id) == str(interaction.user.id):
        embed = discord.Embed(
            description= f"❌ You can't {mode} yourself.",
            color = discord.Color.red()
        )
        await interaction.response.send_message(embed = embed, ephemeral=True)
        return False
    elif str(member.id) == str(interaction.guild.owner_id):
        embed = discord.Embed(
            description= f"❌ You can't {mode} the server owner.",
            color = discord.Color.red()
        )
        await interaction.response.send_message(embed = embed, ephemeral=True)
        return False
    elif str(member.id) == str(client.user.id):
        embed = discord.Embed(
            description= f"❌ You can't {mode} me!!",
            color = discord.Color.red()
        )
        await interaction.response.send_message(embed = embed, ephemeral=True)
        return False
    elif member.bot:
        embed = discord.Embed(
            description= f"❌ You can't {mode} a bot.",
            color = discord.Color.red()
        )
        await interaction.response.send_message(embed = embed, ephemeral=True)
        return False
    elif await KTtools.user_has_permissions(member, ["administrator"]):
        embed = discord.Embed(
            description= f"❌ You can't {mode} an administrator.",
            color = discord.Color.red()
        )
        await interaction.response.send_message(embed = embed, ephemeral=True)
        return False
    elif member.top_role.position > client.get_guild(interaction.guild.id).me.top_role.position:
        embed = discord.Embed(
            description= f"❌ You can't {mode} someone with a higher or equal role to me!",
            color= discord.Color.red()
        )
        await interaction.response.send_message(embed = embed, ephemeral=True)
        return False
    elif interaction.user.top_role.position <= member.top_role.position:
        embed = discord.Embed(
            description= f"❌ You can't {mode} someone with a higher or equal role.",
            color = discord.Color.red()
        )
        await interaction.response.send_message(embed = embed, ephemeral=True)
        return False
    
    return True
class Autorole(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    @app_commands.command(name = "addautorolechannel", description= "Adds the channel to the autorole list. Allows autorole react to work here.")
    async def addautorolechannel(self, interaction : discord.Interaction) -> None:
        
        permissions = ["manage_channels", "manage_messages", "manage_roles"]
        has_perms = await KTtools.interactionuser_has_permissions(interaction, permissions) or await KTtools.interactionuser_has_permissions(interaction, ["administrator"])
        
        if has_perms:
            config = await KTtools.load_config(str(interaction.guild.id))
            
            if str(interaction.channel.id) not in config["autorole_channels"]:
                config["autorole_channels"].append(str(interaction.channel.id))
                await KTtools.save_config(config, str(interaction.guild.id))

                embed = discord.Embed(
                    title = "Channel added",
                    description = f"✅Added {interaction.channel.mention} to autorole list",
                    color = discord.Color.green()
                )
                await interaction.response.send_message(embed = embed, ephemeral=True)
            else:
                embed = discord.Embed(
                    description= "❌ This channel is already in the autorole list.",
                    color = discord.Color.red()
                )
                await interaction.response.send_message(embed = embed, ephemeral=True)
        
        else:
            embed = discord.Embed(
                description= "❌ You don't have permission to use this command.",
                color = discord.Color.red()
            )
            await interaction.response.send_message(embed = embed, ephemeral=True)
        
    @app_commands.command(name = "removeautorolechannel", description= "Removes the channel from the autorole-allowed channel list")
    async def removeautorolechannel(self, interaction : discord.Interaction) -> None:
        
        permissions = ["manage_channels", "manage_messages", "manage_roles"]
        has_perms = await KTtools.interactionuser_has_permissions(interaction, permissions) or await KTtools.interactionuser_has_permissions(interaction, ["administrator"])
        
        if has_perms:
            config = await KTtools.load_config(str(interaction.guild.id))

            if str(interaction.channel.id) in config["autorole_channels"]:
                
                config["autorole_channels"].remove(str(interaction.channel.id))
                await KTtools.save_config(config, str(interaction.guild.id))
                
                embed = discord.Embed(
                    title = "Channel removed",
                    description = f"✅Removed {interaction.channel.mention} from autorole list",
                    color = discord.Color.green()
                )
                await interaction.response.send_message(embed = embed, ephemeral=True)
            
            else:
                embed = discord.Embed(
                    title = "Channel removed",
                    description = f"❌{interaction.channel.mention} not in autorole list!",
                    color = discord.Color.green()
                )
                await interaction.response.send_message(embed = embed, ephemeral=True)
        else:
            embed = discord.Embed(
                description= "❌ You don't have permission to use this command.",
                color = discord.Color.red()
            )
            await interaction.response.send_message(embed = embed, ephemeral=True)

    @app_commands.command(name = "autoroleonjoin", description= "Opens an embed with a dropdown to select automatic roles upon joining")
    async def autoroleonjoin(self, interaction : discord.Interaction) -> None:
        
        permissions = ["manage_channels", "manage_messages", "manage_roles"]
        has_perms = await KTtools.interactionuser_has_permissions(interaction, permissions) or await KTtools.interactionuser_has_permissions(interaction, ["administrator"])
        
        if has_perms:
            await KTautorole.automatic_onjoin(interaction)
        else:
            embed = discord.Embed(
                description = "❌ You don't have permission to use this command.",  
                color = discord.Color.red()
            )
            await interaction.response.send_message(embed = embed, ephemeral=True)

    @app_commands.command(name = "autoroleonreact", description= "Reacts to the **LAST MESSAGE ON CHANNEL**. Sets roles for an emoji react.")
    async def autoroleonreact(self, interaction : discord.Interaction, emoji : str, role : str) -> None:
        
        permissions = ["manage_channels", "manage_messages", "manage_roles"]
        has_perms = await KTtools.interactionuser_has_permissions(interaction, permissions) or await KTtools.interactionuser_has_permissions(interaction, ["administrator"])
        config = await KTtools.load_config(str(interaction.guild.id))
        
        if has_perms:
            try:
                message = interaction.channel.last_message 
            except Exception:
                embed = discord.Embed(
                    description= "❌ Message error. Try deleting and sending a new message.",
                    color=discord.Color.red())
                
                await interaction.response.send_message(embed = embed, ephemeral = True)
                return

            if "<@" in str(role) and str(role).strip("<@&>") not in [str(member.id) for member in interaction.guild.members]:
                if str(interaction.channel_id) in config["autorole_channels"]:
                    try:
                        await message.add_reaction(emoji)
                    except Exception:
                        embed = discord.Embed(
                            description= "❌ Invalid emoji! If you are sure the emoji was correct, try deleting the message and sending a new one.",
                            color=discord.Color.red()
                            )
                        await interaction.response.send_message(embed = embed, ephemeral = True)
                        return

                    config["react_roles"][await KTtools.format_emoji(str(emoji))] = str(role).strip("<@&>")
                    await KTtools.save_config(config, str(interaction.guild.id))
                    await interaction.response.send_message("Done!", ephemeral = True)
                else:
                    embed = discord.Embed(
                        description= "❌ This channel is not in autorole list.\nUse ``` /addautorolechannel ``` to add it, then try again.",
                        color=discord.Color.red()
                        )
                    await interaction.response.send_message(embed = embed, ephemeral = True)
            else:
                embed = discord.Embed(
                description= "❌ Invalid role!",
                color=discord.Color.red())
                await interaction.response.send_message(embed = embed, ephemeral = True)
        else:
            embed = discord.Embed(
                description= "❌ You don't have permission to use this command.",
                color = discord.Color.red()
            )
            await interaction.response.send_message(embed = embed, ephemeral=True)
#Automod
class Automod(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    #Warns
    @app_commands.command(name = "warn", description= "Warns a user")
    async def warn(self, interaction : discord.Interaction, member : discord.Member, reason : str) -> None:
        
        permissions = ["moderate_members"]
        has_perms = await KTtools.interactionuser_has_permissions(interaction, permissions) or await KTtools.interactionuser_has_permissions(interaction, ["administrator"])
        warns_mutes_kicks = await KTtools.load_WMK(str(interaction.guild.id))
        
        if has_perms:
            if await is_member_punishable(interaction, member, "warn"):
                if str(member.id) not in warns_mutes_kicks:
                    await KTmoderation.add_user(member)
                    await KTmoderation.warn(interaction, member, reason)
                else:
                    await KTmoderation.warn(interaction, member, reason)
        else:
            embed = discord.Embed(
                description= "❌ You don't have permission to use this command.",
                color = discord.Color.red()
            )
            await interaction.response.send_message(embed = embed, ephemeral=True)

    @app_commands.command(name = "removewarn", description= "Removes 1 warn from a user")
    async def removewarn(self, interaction : discord.Interaction, member : discord.Member) -> None:
        
        permissions = ["moderate_members"]
        has_perms = await KTtools.interactionuser_has_permissions(interaction, permissions) or await KTtools.interactionuser_has_permissions(interaction, ["administrator"])
        warns_mutes_kicks = await KTtools.load_WMK(str(interaction.guild.id))
        
        if has_perms:
            if await is_member_punishable(interaction, member, "warn/unwarn"):
                if str(member.id) not in warns_mutes_kicks:
                    await KTmoderation.add_user(member)
                    await KTmoderation.remove_warn(interaction, member,)
                else:
                    await KTmoderation.remove_warn(interaction, member)
        else:
            embed = discord.Embed(
                description= "❌ You don't have permission to use this command.",
                color = discord.Color.red()
            )
            await interaction.response.send_message(embed = embed, ephemeral=True)

    @app_commands.command(name = "removeallwarns", description= "Removes all warn counts from a user")
    async def removeallwarns(self, interaction : discord.Interaction, member : discord.Member) -> None:
        
        permissions = ["moderate_members"]
        has_perms = await KTtools.interactionuser_has_permissions(interaction, permissions) or await KTtools.interactionuser_has_permissions(interaction, ["administrator"])
        warns_mutes_kicks = await KTtools.load_WMK(str(interaction.guild.id))
        
        if has_perms:
            
            if await is_member_punishable(interaction, member, "warn/unwarn"):
                if str(member.id) not in warns_mutes_kicks:
                    await KTmoderation.add_user(member)
                    await KTmoderation.remove_all_warns(interaction, member,)
                else:
                    await KTmoderation.remove_all_warns(interaction, member)
        else:
            embed = discord.Embed(
                description= "❌ You don't have permission to use this command.",
                color = discord.Color.red()
            )
            await interaction.response.send_message(embed = embed, ephemeral=True)

    #Mutes
    @app_commands.command(name = "mute", description= "Mutes a user for x minutes")
    async def mute(self, interaction : discord.Interaction, member : discord.Member, reason : str, duration : int) -> None:
        
        permissions = ["moderate_members"]
        has_perms = await KTtools.interactionuser_has_permissions(interaction, permissions) or await KTtools.interactionuser_has_permissions(interaction, ["administrator"])
        warns_mutes_kicks = await KTtools.load_WMK(str(interaction.guild.id))
        
        if has_perms:
            if await is_member_punishable(interaction, member, "mute/unmute"):
                if str(member.id) not in warns_mutes_kicks:
                    await KTmoderation.add_user(member)
                    await KTmoderation.mute(interaction, member, reason, duration)
                else:
                    await KTmoderation.mute(interaction, member, reason, duration)
        else:
            embed = discord.Embed(
                description= "❌ You don't have permission to use this command.",
                color = discord.Color.red()
            )
            await interaction.response.send_message(embed = embed, ephemeral=True)

    @app_commands.command(name = "unmute", description= "Unmutes a user")
    async def unmute(self, interaction : discord.Interaction, member : discord.Member) -> None:

        permissions = ["moderate_members"]
        has_perms = await KTtools.interactionuser_has_permissions(interaction, permissions) or await KTtools.interactionuser_has_permissions(interaction, ["administrator"])
        warns_mutes_kicks = await KTtools.load_WMK(str(interaction.guild.id))
        
        if has_perms:
            if await is_member_punishable(interaction, member, "mute/unmute"):
                if str(member.id) not in warns_mutes_kicks:
                    await KTmoderation.add_user(member)
                    await KTmoderation.unmute(interaction, member)
                else:
                    await KTmoderation.unmute(interaction, member)
        else:
            embed = discord.Embed(
                description= "❌ You don't have permission to use this command.",
                color = discord.Color.red()
            )
            await interaction.response.send_message(embed = embed, ephemeral=True)

    @app_commands.command(name = "removemute", description= "Removes 1 mute count from a user, does NOT unmute")
    async def removemute(self, interaction : discord.Interaction, member : discord.Member) -> None:
        
        permissions = ["moderate_members"]
        has_perms = await KTtools.interactionuser_has_permissions(interaction, permissions) or await KTtools.interactionuser_has_permissions(interaction, ["administrator"])
        warns_mutes_kicks = await KTtools.load_WMK(str(interaction.guild.id))
        
        if has_perms:
            if await is_member_punishable(interaction, member, "mute/unmute"):
                if str(member.id) not in warns_mutes_kicks:
                    await KTmoderation.add_user(member)
                    await KTmoderation.remove_mute(interaction, member)
                else:
                    await KTmoderation.remove_mute(interaction, member)
        else:
            embed = discord.Embed(
                description= "❌ You don't have permission to use this command.",
                color = discord.Color.red()
            )
            await interaction.response.send_message(embed = embed, ephemeral=True)

    @app_commands.command(name = "removeallmutes", description= "Removes all mute counts from a user, does NOT unmute")
    async def removeallmutes(self, interaction : discord.Interaction, member : discord.Member) -> None:
        
        permissions = ["moderate_members"]
        has_perms = await KTtools.interactionuser_has_permissions(interaction, permissions) or await KTtools.interactionuser_has_permissions(interaction, ["administrator"])
        warns_mutes_kicks = await KTtools.load_WMK(str(interaction.guild.id))
        
        if has_perms:
            if await is_member_punishable(interaction, member, "mute/unmute"):
                if str(member.id) not in warns_mutes_kicks:
                    await KTmoderation.add_user(member)
                    await KTmoderation.remove_all_mutes(interaction, member)
                else:
                    await KTmoderation.remove_all_mutes(interaction, member)
        else:
            embed = discord.Embed(
                description= "❌ You don't have permission to use this command.",
                color = discord.Color.red()
            )
            await interaction.response.send_message(embed = embed, ephemeral=True)

    #Kicks
    @app_commands.command(name = "kick", description= "Kicks a user")
    async def kick(self, interaction : discord.Interaction, member : discord.Member, reason : str) -> None:

        permissions = ["kick_members"]
        has_perms = await KTtools.interactionuser_has_permissions(interaction, permissions) or await KTtools.interactionuser_has_permissions(interaction, ["administrator"])
        warns_mutes_kicks = await KTtools.load_WMK(str(interaction.guild.id))
        
        if has_perms:
            if await is_member_punishable(interaction, member, "kick"):
                if str(member.id) not in warns_mutes_kicks:
                    await KTmoderation.add_user(member)
                    await KTmoderation.kick(interaction, member, reason) 
                else:
                    await KTmoderation.kick(interaction, member, reason)
        else:
            embed = discord.Embed(
                description= "❌ You don't have permission to use this command.",
                color = discord.Color.red()
            )
            await interaction.response.send_message(embed = embed, ephemeral=True)

    @app_commands.command(name = "removekick", description= "Removes 1 kick count from a user, does NOT kick")
    async def removekick(self, interaction : discord.Interaction, member : discord.Member) -> None:
        
        permissions = ["kick_members"]
        has_perms = await KTtools.interactionuser_has_permissions(interaction, permissions) or await KTtools.interactionuser_has_permissions(interaction, ["administrator"])
        warns_mutes_kicks = await KTtools.load_WMK(str(interaction.guild.id))
        
        if has_perms:
            if await is_member_punishable(interaction, member, "kick"):
                embed = discord.Embed(
                    description= f"✅ {member.mention} has been cleared of 1 kick count.",
                    color = discord.Color.green()
                )
                await interaction.response.send_message(embed = embed)
                
                if str(member.id) not in warns_mutes_kicks:
                    await KTmoderation.add_user(member)
                    await KTmoderation.remove_kick(member)
                else:
                    await KTmoderation.remove_kick(member)

        else:
            embed = discord.Embed(
                description= "❌ You don't have permission to use this command.",
                color = discord.Color.red()
            )
            await interaction.response.send_message(embed = embed, ephemeral=True)

    @app_commands.command(name="removeallkicks", description= "Removes all kick counts from a user, does NOT kick")
    async def removeallkicks(self, interaction : discord.Interaction, member : discord.Member) -> None:
        
        permissions = ["kick_members"]
        has_perms = await KTtools.interactionuser_has_permissions(interaction, permissions) or await KTtools.interactionuser_has_permissions(interaction, ["administrator"])
        warns_mutes_kicks = await KTtools.load_WMK(str(interaction.guild.id))
        
        if has_perms:
            if await is_member_punishable(interaction, member, "kick"):
                embed = discord.Embed(
                    description= f"✅ {member.mention} has been cleared of all kicks.",
                    color = discord.Color.green()
                )
                await interaction.response.send_message(embed = embed)
                
                if str(member.id) not in warns_mutes_kicks:
                    await KTmoderation.add_user(member)
                    warns_mutes_kicks[str(member.id)][2] = 0
                else:
                    warns_mutes_kicks[str(member.id)][2] = 0
                
                await KTtools.save_WMK(warns_mutes_kicks, str(interaction.guild_id))
        else:
            embed = discord.Embed(
                description= "❌ You don't have permission to use this command.",
                color = discord.Color.red()
            )
            await interaction.response.send_message(embed = embed, ephemeral=True)

    #Ban
    @app_commands.command(name = "ban", description= "Bans a user")
    async def ban(self, interaction : discord.Interaction, member : discord.Member, reason : str) -> None:

        permissions = ["ban_members"]
        has_perms = await KTtools.interactionuser_has_permissions(interaction, permissions) or await KTtools.interactionuser_has_permissions(interaction, ["administrator"])
        
        if has_perms:
            if await is_member_punishable(interaction, member, "ban"):
                await member.ban(reason = reason)
                
                embed = discord.Embed(
                    description= f"{member.mention} has been banned for reason:\n\n**{reason}**",
                    color = discord.Color.dark_gray()
                )
                await interaction.response.send_message(embed = embed)     
        else:
            embed = discord.Embed(
                description= "❌ You don't have permission to use this command.",
                color = discord.Color.red()
            )
            await interaction.response.send_message(embed = embed, ephemeral=True)

    #Automoderation
    @app_commands.command(name = "maxwarncount", description= "Sets the max warn count")
    async def setmaxwarncount(self, interaction : discord.Interaction,count : int) -> None:
        
        permissions = ["administrator"]
        has_perms = await KTtools.interactionuser_has_permissions(interaction, permissions)
        
        if has_perms:
            if count < 0:
                embed = discord.Embed(
                    description= "❌ Count must be greater than 0.",
                    color = discord.Color.red()
                )
                return await interaction.response.send_message(embed = embed, ephemeral=True)
            config = await KTtools.load_config(str(interaction.guild.id))
            config["max_warns"] = count
            await KTtools.save_config(config, str(interaction.guild.id))
            
            embed = discord.Embed(
                description= f"✅ Set max warns to {count}.",
                color = discord.Color.green()
            )
            await interaction.response.send_message(embed = embed)
        
        
        else:
            embed = discord.Embed(
                description= "❌ You don't have permission to use this command.",
                color = discord.Color.red()
            )
            await interaction.response.send_message(embed = embed, ephemeral=True)

    @app_commands.command(name = "maxmutecount", description= "Sets the max mute count")
    async def maxmutecount(self, interaction : discord.Interaction,count : int) -> None:
        
        permissions = ["administrator"]
        has_perms = await KTtools.interactionuser_has_permissions(interaction, permissions)
        
        if has_perms:
            if count < 0:
                embed = discord.Embed(
                    description= "❌ Count must be greater than 0.",
                    color = discord.Color.red()
                )
                return await interaction.response.send_message(embed = embed, ephemeral=True)
            config = await KTtools.load_config(str(interaction.guild.id))
            config["max_mutes"] = count
            await KTtools.save_config(config, str(interaction.guild.id))
            
            embed = discord.Embed(
                description= f"✅ Set max mutes to {count}.",
                color = discord.Color.green()
            )
            await interaction.response.send_message(embed = embed)
        
        
        else:
            embed = discord.Embed(
                description= "❌ You don't have permission to use this command.",
                color = discord.Color.red()
            )
            await interaction.response.send_message(embed = embed, ephemeral=True)

    @app_commands.command(name = "muteduration", description = "Sets automod mute duration in minutes")
    async def muteduration(self, interaction : discord.Interaction, duration : int) -> None:
        
        permissions = ["administrator"]
        has_perms = await KTtools.interactionuser_has_permissions(interaction, permissions)
        
        if has_perms:
            if duration < 0:
                embed = discord.Embed(
                    description= "❌ Duration must be greater than 0.",
                    color = discord.Color.red()
                )
                return await interaction.response.send_message(embed = embed, ephemeral=True)
            config = await KTtools.load_config(str(interaction.guild.id))
            config["mute_duration"] = duration
            await KTtools.save_config(config, str(interaction.guild.id))
            
            embed = discord.Embed(
                description= f"✅ Set mute duration to {duration} minutes.",
                color = discord.Color.green()
            )
            await interaction.response.send_message(embed = embed)
        else:
            embed = discord.Embed(
                description= "❌ You don't have permission to use this command.",
                color = discord.Color.red()
            )
            await interaction.response.send_message(embed = embed, ephemeral=True)

    @app_commands.command(name="maxkickcount", description= "Sets the max kick count")
    async def maxkickcount(self, interaction : discord.Interaction,count : int) -> None:
        
        permissions = ["administrator"]
        has_perms = await KTtools.interactionuser_has_permissions(interaction, permissions)
        
        if has_perms:
            if count < 0:
                embed = discord.Embed(
                    description= "❌ Count must be greater than 0.",
                    color = discord.Color.red()
                )
                return await interaction.response.send_message(embed = embed, ephemeral=True)
            config = await KTtools.load_config(str(interaction.guild.id))
            config["max_kicks"] = count
            await KTtools.save_config(config, str(interaction.guild.id))
            
            embed = discord.Embed(
                description= f"✅ Set max kicks to {count}.",
                color = discord.Color.green()
            )
            await interaction.response.send_message(embed = embed)
        else:
            embed = discord.Embed(
                description= "❌ You don't have permission to use this command.",
                color = discord.Color.red()
            )
            await interaction.response.send_message(embed = embed, ephemeral=True)

    @app_commands.command(name = "banword", description= "Ban a word for the automod system to work on")
    async def banword(self, interaction : discord.Interaction, word : str) -> None:
        
        permissions = ["administrator"]
        has_perms = await KTtools.interactionuser_has_permissions(interaction, permissions)
        
        if has_perms:
            server_id = str(interaction.guild_id)
            word = unidecode(word.lower())
            banned_words = await KTtools.load_banned_words(server_id)
            
            if word in banned_words:
                embed = discord.Embed(
                    description= f"❌ '**{word}**' is already banned.",
                    color = discord.Color.red()
                )
                return await interaction.response.send_message(embed = embed)
            banned_words.append(word)
            await KTtools.save_banned_words(banned_words, server_id)
            global banned_words_per_server
            banned_words_per_server = KTtools.get_banned_words_per_server()
            
            embed = discord.Embed(
                description= f"✅ Banned word **{word}**.",
                color = discord.Color.green()
            )
            await interaction.response.send_message(embed = embed)
            
        else:
            embed = discord.Embed(
                description= "❌ You don't have permission to use this command.",
                color = discord.Color.red()
            )
            return await interaction.response.send_message(embed = embed, ephemeral=True)

    @app_commands.command(name = "unbanword", description= "Remove a banned word")
    async def unbanword(self, interaction : discord.Interaction, word : str) -> None:
        
        permissions = ["administrator"]
        has_perms = await KTtools.interactionuser_has_permissions(interaction, permissions)
        
        if has_perms:
            server_id = str(interaction.guild_id)
            word = unidecode(word.lower())
            banned_words = await KTtools.load_banned_words(server_id)
            
            if word not in banned_words:
                embed = discord.Embed(
                    description= f"❌ **'{word}'** is not banned.",
                    color = discord.Color.red()
                )
                return await interaction.response.send_message(embed = embed)
            banned_words.remove(word)
            await KTtools.save_banned_words(banned_words, server_id)
            global banned_words_per_server
            banned_words_per_server = KTtools.get_banned_words_per_server()
            
            embed = discord.Embed(
                description= f"✅Unbanned **{word}** from word list.",
                color = discord.Color.green()
            )
            await interaction.response.send_message(embed = embed)
        
        else:
            embed = discord.Embed(  
                description= "❌ You don't have permission to use this command.",
                color = discord.Color.red()
            )
            return await interaction.response.send_message(embed = embed, ephemeral=True)

    @app_commands.command(name = "cleareveryone", description= "Clears everyone's warn, mute and kick counts")
    async def cleareveryone(self, interaction : discord.Interaction) -> None:

        permissions = ["administrator"]
        has_perms = await KTtools.interactionuser_has_permissions(interaction, permissions)
        
        if has_perms:
            wmk = await KTtools.load_WMK(str(interaction.guild_id))
            wmk = {"USER_TEMPLATE" : [0, 0, 0]}
            await KTtools.save_WMK(wmk, str(interaction.guild_id))
            
            embed = discord.Embed(
                description= "✅ Cleared everyone's warn, mute and kick counts.",
                color = discord.Color.green()
            )
            return await interaction.response.send_message(embed = embed)
        
        else:
            embed = discord.Embed(
                description= "❌ You don't have permission to use this command.",
                color = discord.Color.red()
            )
            return await interaction.response.send_message(embed = embed, ephemeral=True)

    @app_commands.command(name = "clearbannedwords", description= "Removes all banned words")
    async def clearbannedwords(self, interaction : discord.Interaction) -> None:

        permissions = ["administrator"]
        has_perms = await KTtools.interactionuser_has_permissions(interaction, permissions)
        
        if has_perms:
            banned_words = await KTtools.load_banned_words(str(interaction.guild_id))
            banned_words = []
            await KTtools.save_banned_words(banned_words, str(interaction.guild_id))
            
            embed = discord.Embed(
                description= "✅ Cleared all banned words.",
                color = discord.Color.green()
            )
            return await interaction.response.send_message(embed = embed)
        
        else:
            embed = discord.Embed(
                description= "❌ You don't have permission to use this command.",
                color = discord.Color.red()
            )
            return await interaction.response.send_message(embed = embed, ephemeral=True)

    @app_commands.command(name = "resetconfig", description= "Resets the config to default")
    async def resetconfig(self, interaction : discord.Interaction) -> None:

        permissions = ["administrator"]
        has_perms = await KTtools.interactionuser_has_permissions(interaction, permissions)
        
        if has_perms:
            config = await KTtools.load_config(str(interaction.guild_id))
            config = {"server_id" : str(interaction.guild_id), "welcome_channel": "", "welcome_type": "text", "welcome_image": "", "welcome_message": "Welcome @user to @server", "onjoin_roles": "[]", "react_roles": "{}", "autorole_channels": "[]", "muted_users": "[]", "max_warns": 3, "max_mutes": 3, "mute_duration": 10, "max_kicks": 3}
            await KTtools.save_config(config, str(interaction.guild_id))
            
            embed = discord.Embed(
                description= "✅ Reset the config.",
                color = discord.Color.green()
            )
            return await interaction.response.send_message(embed = embed)
        
        else:
            embed = discord.Embed(
                description= "❌ You don't have permission to use this command.",
                color = discord.Color.red()
            )
            return await interaction.response.send_message(embed = embed, ephemeral=True)
#Music
lastactive = {}
@tasks.loop(seconds = 45)
async def inactivity_check():
    global lastactive
    for guild in client.guilds:
        voice = discord.utils.get(client.voice_clients, guild=guild)
        
        if voice:
            voice_playing = voice.is_playing() or voice.is_paused()
            voice_alone = len([connectedmember for connectedmember in voice.channel.members if not connectedmember.bot]) == 0
            if not voice_playing or voice_alone:
                None
            else:
                lastactive[guild.id] = float(time.time())
            
            if guild.id in lastactive:
                if float(time.time()) - lastactive[guild.id] > 450:
                    await voice.disconnect()
            
class Music(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name = "connect", description= "Connect to voice channel")
    async def connect(self, interaction : discord.Interaction) -> None:
        voice = discord.utils.get(client.voice_clients, guild=interaction.guild)
        global lastactive
        lastactive[interaction.guild.id] = float(time.time())
        
        if not interaction.user.voice:
            embed = discord.Embed(
                description= "❌ You are not connected to a voice channel.",
                color = discord.Color.red()
            )
            return await interaction.response.send_message(embed = embed)
        elif voice:
            embed = discord.Embed(
                description= "❌ I am already connected to a voice channel. Use /move to move me to your channel.",
                color = discord.Color.red()
            )
            return await interaction.response.send_message(embed = embed)   
        
        await interaction.user.voice.channel.connect()
        embed = discord.Embed(
            description= "✅ Connected to voice channel.",
            color = discord.Color.green()
        )
        return await interaction.response.send_message(embed = embed)

    @app_commands.command(name = "disconnect", description= "Disconnect from voice channel")
    async def disconnect(self, interaction : discord.Interaction) -> None:
        voice = discord.utils.get(client.voice_clients, guild=interaction.guild)
        playlistconfig = await KTtools.load_playlist(str(interaction.guild.id))
        
        if playlistconfig["isplaying"]:
            embed = discord.Embed(
                description= "❌ I am currently playing music, please stop it before disconnecting.",
                color = discord.Color.red()
            )
            return await interaction.response.send_message(embed = embed)
        elif not voice:
            embed = discord.Embed(
                description= "❌ I am not connected to a voice channel.",
                color = discord.Color.red()
            )
            return await interaction.response.send_message(embed = embed)
        elif interaction.user.voice.channel != interaction.guild.me.voice.channel:
            embed = discord.Embed(
                description= "❌ You are not in my voice channel.",
                color = discord.Color.red()
            )
            return await interaction.response.send_message(embed = embed)

        await voice.disconnect()
        embed = discord.Embed(
            description= "✅ Disconnected from voice channel.",
            color = discord.Color.green()
        )
        return await interaction.response.send_message(embed = embed)

    @app_commands.command(name = "forcedisconnect", description= "Disconnect from voice channel by force")
    async def forcedisconnect(self, interaction : discord.Interaction) -> None:
        if not await KTtools.interactionuser_has_permissions(interaction, ["administrator"]) or interaction.guild.owner_id != interaction.user.id:
            if "dj" not in [role.name.lower() for role in interaction.user.roles]:
                embed = discord.Embed(
                    description= "You need to have the 'DJ' role or be an admin to use this command!",
                    color = discord.Color.dark_purple()
                )
                return await interaction.response.send_message(embed = embed, ephemeral=True)
        
        voice = discord.utils.get(client.voice_clients, guild=interaction.guild)
        if voice:
            voice.stop()
            await voice.disconnect()
            embed = discord.Embed(
                description= "✅ Disconnected from voice channel.",
                color = discord.Color.green()
            )
            return await interaction.response.send_message(embed = embed)
        else:
            embed = discord.Embed(
                description= "❌ I am not connected to a voice channel.",
                color = discord.Color.red()
            )
            return await interaction.response.send_message(embed = embed)

    @app_commands.command(name = "move", description= "Move to new voice channel")
    async def move(self, interaction : discord.Interaction) -> None:
        playlistconfig = await KTtools.load_playlist(str(interaction.guild.id))
        
        if not interaction.user.voice:
            embed = discord.Embed(
                description= "❌ You are not connected to a voice channel.",
                color = discord.Color.red()
            )
            return await interaction.response.send_message(embed = embed)
        elif not interaction.guild.me.voice:
            embed = discord.Embed(
                description= "❌ I am not connected to a voice channel.",
                color = discord.Color.red()
            )
            return await interaction.response.send_message(embed = embed)
        elif interaction.user.voice.channel == interaction.guild.me.voice.channel:
            embed = discord.Embed(
                description= "❌ I am already in your voice channel.",
                color = discord.Color.red()
            )
            return await interaction.response.send_message(embed = embed)
        elif playlistconfig["isplaying"]:
            embed = discord.Embed(
                description= "❌ You cant move me to a voice channel while playing a song.",
                color = discord.Color.red()
            )
            return await interaction.response.send_message(embed = embed)
        
        """ if not await KTtools.interactionuser_has_permissions(interaction, ["administrator"]) or interaction.guild.owner_id != interaction.user.id:
            if "dj" not in [role.name.lower() for role in interaction.user.roles]:
                embed = discord.Embed(
                    description= "You need to have the 'DJ' role or be an admin to use this command!",
                    color = discord.Color.dark_purple()
                )
                return await interaction.response.send_message(embed = embed, ephemeral=True) """
        
        await interaction.guild.voice_client.move_to(interaction.user.voice.channel)
        embed = discord.Embed(
            description= "✅ Moved to new voice channel.",
            color = discord.Color.green()
        )
        await interaction.response.send_message(embed = embed)
    
    @app_commands.command(name = "play", description= "Play or queue a song into the playlist")
    async def play(self, interaction : discord.Interaction, song : str) -> None:
        voice = discord.utils.get(client.voice_clients, guild=interaction.guild)
        
        if not interaction.user.voice:
            embed = discord.Embed(
                description= "❌ You are not connected to a voice channel.",
                color = discord.Color.red()
            )
            return await interaction.response.send_message(embed = embed)
        
        if voice:
            if interaction.user.voice.channel != interaction.guild.me.voice.channel:
                embed = discord.Embed(
                    description= "❌ You are not in my voice channel.",
                    color = discord.Color.red()
                )
                return await interaction.response.send_message(embed = embed)
        elif not voice:
            global lastactive
            lastactive[interaction.guild.id] = float(time.time())
            await interaction.user.voice.channel.connect()
        
        playlistconfig = await KTtools.load_playlist(server_id = str(interaction.guild.id))
        if "https://" in song:
            if ("youtube.com" in song or "youtu.be" in song) and "playlist" in song:
                playlist_urls = Playlist(song).video_urls
                playlist_title = Playlist(song).title
                print(playlist_urls, "\n", playlist_title)
                
                if playlist_urls:
                    for url in playlist_urls:
                        playlistconfig["playlist"].append(url)
                else:
                    embed = discord.Embed(
                        description = "❌ I couldn't find any songs in the playlist. Maybe the playlist is private, or wrong link?",
                        color = discord.Color.dark_purple()
                    )
                    embed.set_footer(text = "Tip: Link should look like https://youtube.com/playlist?list=SOMETHING...")
                    return await interaction.response.send_message(embed = embed)
                await KTtools.save_playlist(playlistconfig, server_id = str(interaction.guild.id))
                
                embed = discord.Embed(
                    description = "Added **" + playlist_title + "** to playlist.",
                    color = discord.Color.dark_purple()
                )
                await interaction.response.send_message(embed = embed)
                
                if not playlistconfig["isplaying"]:
                    playlistconfig["isplaying"] = True
                    await KTtools.save_playlist(playlistconfig, server_id = str(interaction.guild.id))
                    await KTmusic.play_song(interaction = interaction, song = song)
            
            elif "open.spotify.com" in song:
                if "track" in song:
                    loop = asyncio.get_event_loop()
                    song = await loop.run_in_executor(None, lambda: KTmusic.get_spotify_info(query = song))
                    
                    playlistconfig["playlist"].append(song)
                    await KTtools.save_playlist(playlistconfig, server_id = str(interaction.guild.id))
                    
                    embed = discord.Embed(
                        description = "Added **" + song + "** to playlist.",
                        color = discord.Color.dark_purple()
                    )
                    await interaction.response.send_message(embed = embed)
                    if not playlistconfig["isplaying"]:
                        playlistconfig["isplaying"] = True
                        await KTtools.save_playlist(playlistconfig, server_id = str(interaction.guild.id))
                        await KTmusic.play_song(interaction = interaction, song = song)
            
                elif "playlist" in song:
                    loop = asyncio.get_event_loop()
                    playlist_name = await loop.run_in_executor(None, lambda: KTmusic.get_spotify_info(query = song)[0])
                    playlist_songs = await loop.run_in_executor(None, lambda: KTmusic.get_spotify_info(query = song)[1])

                    embed = discord.Embed(
                        description = "Added **" + playlist_name + "** to playlist.",
                        color = discord.Color.dark_purple()
                    )
                    await interaction.response.send_message(embed = embed)
                    
                    for track in playlist_songs:
                        playlistconfig["playlist"].append(track)
                    await KTtools.save_playlist(playlistconfig, server_id = str(interaction.guild.id))
                    if not playlistconfig["isplaying"]:
                        playlistconfig["isplaying"] = True
                        await KTtools.save_playlist(playlistconfig, server_id = str(interaction.guild.id))
                        await KTmusic.play_song(interaction = interaction, song = playlistconfig["playlist"][0])
            
            else:
                playlistconfig["playlist"].append(song)
                await KTtools.save_playlist(playlistconfig, server_id = str(interaction.guild.id))
                
                embed = discord.Embed(
                    description = "Added **" + KTmusic.get_youtube_search_info(song)['title'] + "** to playlist.",
                    color = discord.Color.dark_purple()
                )
                await interaction.response.send_message(embed = embed)
                if not playlistconfig["isplaying"]:
                    playlistconfig["isplaying"] = True
                    await KTtools.save_playlist(playlistconfig, server_id = str(interaction.guild.id))
                    await KTmusic.play_song(interaction = interaction, song = song)
        
        else:
            embed = discord.Embed(
                description= f"Added **{KTmusic.get_youtube_search_info(query = song)['title']}** to playlist.",
                color = discord.Color.dark_purple()
                )
            await interaction.response.send_message(embed = embed)
            
            playlistconfig["playlist"].append(KTmusic.get_youtube_search_info(song)['title'])
            await KTtools.save_playlist(playlistconfig, server_id = str(interaction.guild.id))
            
            if not playlistconfig["isplaying"]:
                playlistconfig["isplaying"] = True
                await KTtools.save_playlist(playlistconfig, server_id = str(interaction.guild.id))
                await KTmusic.play_song(interaction = interaction, song = song)
    
    @app_commands.command(name = "stop", description = "Stop playing music and clear playlist")
    async def stop(self, interaction : discord.Interaction) -> None:
        server_id = str(interaction.guild.id)
        voice = discord.utils.get(client.voice_clients, guild=interaction.guild)
        
        if not voice:
            embed = discord.Embed(
                description= "❌ I am not connected to a voice channel.",
                color = discord.Color.red()
            )
            return await interaction.response.send_message(embed = embed)
        elif interaction.user.voice.channel != interaction.guild.me.voice.channel:
            embed = discord.Embed(
                description= "❌ You are not in my voice channel.",
                color = discord.Color.red()
            )
            return await interaction.response.send_message(embed = embed)
        elif not voice.is_playing():
            embed = discord.Embed(
                description= "❌ I am not playing anything.",
                color = discord.Color.red()
            )
            return await interaction.response.send_message(embed = embed)
        
        """ if not await KTtools.interactionuser_has_permissions(interaction, ["administrator"]) or interaction.guild.owner_id != interaction.user.id:
            if "dj" not in [role.name.lower() for role in interaction.user.roles]:
                embed = discord.Embed(
                    description= "You need to have the 'DJ' role or be an admin to use this command!",
                    color = discord.Color.dark_purple()
                )
                return await interaction.response.send_message(embed = embed, ephemeral=True) """
        
        embed = discord.Embed(
            description= "✅ Stopped the music",
            color = discord.Color.dark_purple()
        )
        await interaction.response.send_message(embed = embed)
        
        voice.stop()
        await KTtools.save_playlist({"playlist": "[]", "isplaying": "False"}, server_id)

    @app_commands.command(name = "pause", description = "Pause/resume the playing")
    async def pause(self, interaction : discord.Interaction) -> None:
        server_id = str(interaction.guild.id)
        voice = discord.utils.get(client.voice_clients, guild=interaction.guild)
        playlistconfig = await KTtools.load_playlist(server_id)
        
        if not voice:
            embed = discord.Embed(
                description= "❌ I am not connected to a voice channel.",
                color = discord.Color.red()
            )
            return await interaction.response.send_message(embed = embed)
        elif interaction.user.voice.channel != interaction.guild.me.voice.channel:
            embed = discord.Embed(
                description= "❌ You are not in my voice channel.",
                color = discord.Color.red()
            )
            return await interaction.response.send_message(embed = embed)
        elif not (voice.is_playing() and playlistconfig["isplaying"]):
            embed = discord.Embed(
                description= "❌ I am not playing anything.",
                color = discord.Color.red()
            )
            return await interaction.response.send_message(embed = embed)
        
        """ if not await KTtools.interactionuser_has_permissions(interaction, ["administrator"]) or interaction.guild.owner_id != interaction.user.id:
            if "dj" not in [role.name.lower() for role in interaction.user.roles]:
                embed = discord.Embed(
                    description= "You need to have the 'DJ' role or be an admin to use this command!",
                    color = discord.Color.dark_purple()
                )
                return await interaction.response.send_message(embed = embed, ephemeral=True) """

        if not interaction.guild.voice_client.is_paused():
            embed = discord.Embed(
            description= "Paused the playing",
            color = discord.Color.dark_purple()
            )
            await interaction.response.send_message(embed = embed)
            interaction.guild.voice_client.pause()
        else:
            embed = discord.Embed(
            description= "Resumed the playing",
            color = discord.Color.dark_purple()
            )
            await interaction.response.send_message(embed = embed)
            interaction.guild.voice_client.resume()
            
    @app_commands.command(name = "repeat", description = "Toggle repeat on/off")
    async def repeat(self, interaction : discord.Interaction) -> None:
        server_id = str(interaction.guild.id)
        
        if not interaction.user.voice:
            embed = discord.Embed(
                description= "❌ You are not connected to a voice channel.",
                color = discord.Color.red()
            )
            return await interaction.response.send_message(embed = embed)
        elif not interaction.guild.me.voice:
            embed = discord.Embed(
                description= "❌ I am not connected to a voice channel.",
                color = discord.Color.red()
            )
            return await interaction.response.send_message(embed = embed)
        elif interaction.user.voice.channel != interaction.guild.me.voice.channel:
            embed = discord.Embed(
                description= "❌ You are not in my voice channel.",
                color = discord.Color.red()
            )
            return await interaction.response.send_message(embed = embed)
        
        """ if not await KTtools.interactionuser_has_permissions(interaction, ["administrator"]) or interaction.guild.owner_id != interaction.user.id:
            if "dj" not in [role.name.lower() for role in interaction.user.roles]:
                embed = discord.Embed(
                    description= "You need to have the 'DJ' role or be an admin to use this command!",
                    color = discord.Color.dark_purple()
                )
                return await interaction.response.send_message(embed = embed, ephemeral=True) """
        
        playlistconfig = await KTtools.load_playlist(server_id)
        playlistconfig["repeat"] = not playlistconfig["repeat"]
        await KTtools.save_playlist(playlistconfig, server_id)
        
        if playlistconfig["repeat"]:
            embed = discord.Embed(
                description= "### Repeat ON",
                color = discord.Color.green()
            )
        else:
            embed = discord.Embed(
                description= "### Repeat OFF",
                color = discord.Color.red()
            )
        await interaction.response.send_message(embed = embed)

    @app_commands.command(name = "shuffle", description = "Shuffle the playlist")
    async def shuffle(self, interaction : discord.Interaction) -> None:
        server_id = str(interaction.guild.id)
        
        if not interaction.user.voice:
            embed = discord.Embed(
                description= "❌ You are not connected to a voice channel.",
                color = discord.Color.red()
            )
            return await interaction.response.send_message(embed = embed)
        elif not interaction.guild.me.voice:
            embed = discord.Embed(
                description= "❌ I am not connected to a voice channel.",
                color = discord.Color.red()
            )
            return await interaction.response.send_message(embed = embed)
        elif interaction.user.voice.channel != interaction.guild.me.voice.channel:
            embed = discord.Embed(
                description= "❌ You are not in my voice channel.",
                color = discord.Color.red()
            )
            return await interaction.response.send_message(embed = embed)
        
        """ if not await KTtools.interactionuser_has_permissions(interaction, ["administrator"]) or interaction.guild.owner_id != interaction.user.id:
            if "dj" not in [role.name.lower() for role in interaction.user.roles]:
                embed = discord.Embed(
                    description= "You need to have the 'DJ' role or be an admin to use this command!",
                    color = discord.Color.dark_purple()
                )
                return await interaction.response.send_message(embed = embed, ephemeral=True) """
        
        playlistconfig = await KTtools.load_playlist(server_id)
        playlistconfig["shuffle"] = not playlistconfig["shuffle"]
        await KTtools.save_playlist(playlistconfig, server_id)
        
        if playlistconfig["shuffle"]:
            embed = discord.Embed(
                description= "### Shuffle ON",
                color = discord.Color.green()
            )
        else:
            embed = discord.Embed(
                description= "### Shuffle OFF",
                color = discord.Color.red()
            )
        await interaction.response.send_message(embed = embed)

    @app_commands.command(name = "next", description = "Play the next song in the playlist")
    async def nextc(self, interaction : discord.Interaction) -> None:
        server_id = str(interaction.guild.id)
        playlistconfig = await KTtools.load_playlist(server_id)
        
        if not playlistconfig["isplaying"]:
            embed = discord.Embed(
                description= "❌ I am not playing anything.",
                color = discord.Color.red()
            )
            return await interaction.response.send_message(embed = embed)
        elif not interaction.user.voice:
            embed = discord.Embed(
                description= "❌ You are not connected to a voice channel.",
                color = discord.Color.red()
            )
            return await interaction.response.send_message(embed = embed)
        elif interaction.user.voice.channel != interaction.guild.me.voice.channel:
            embed = discord.Embed(
                description= "❌ You are not in my voice channel.",
                color = discord.Color.red()
            )
            return await interaction.response.send_message(embed = embed)
        elif (len(playlistconfig["playlist"]) <= 1) and not playlistconfig["repeat"]:
            embed = discord.Embed(
                description= "❌ Last song in the playlist, use /stop to stop the music or /play to queue more music",
                color = discord.Color.red()
            )
            return await interaction.response.send_message(embed = embed)

        """ if not await KTtools.interactionuser_has_permissions(interaction, ["administrator"]) or interaction.guild.owner_id != interaction.user.id:
            if "dj" not in [role.name.lower() for role in interaction.user.roles]:
                embed = discord.Embed(
                    description= "You need to have the 'DJ' role or be an admin to use this command!",
                    color = discord.Color.dark_purple()
                )
                return await interaction.response.send_message(embed = embed, ephemeral=True) """

        embed = discord.Embed(
            description= "✅ Loading next song...",
            color = discord.Color.dark_purple()
        )
        await interaction.response.send_message(embed = embed)
        
        interaction.guild.voice_client.stop()

    @app_commands.command(name = "rmsong", description = "Remove current song or specified song from the playlist. Type * to clear playlist")
    async def rmsong(self, interaction : discord.Interaction, song : str = None) -> None:
        server_id = str(interaction.guild.id)
        playlistconfig = await KTtools.load_playlist(server_id)
        
        if not interaction.user.voice:
            embed = discord.Embed(
                description= "❌ You are not connected to a voice channel.",
                color = discord.Color.red()
            )
            return await interaction.response.send_message(embed = embed)
        elif not interaction.guild.me.voice:
            embed = discord.Embed(
                description= "❌ I am not connected to a voice channel.",
                color = discord.Color.red()
            )
            return await interaction.response.send_message(embed = embed)
        elif interaction.user.voice.channel != interaction.guild.me.voice.channel:
            embed = discord.Embed(
                description= "❌ You are not in my voice channel.",
                color = discord.Color.red()
            )
            return await interaction.response.send_message(embed = embed)
        
        """ if not await KTtools.interactionuser_has_permissions(interaction, ["administrator"]) or interaction.guild.owner_id != interaction.user.id:
            if "dj" not in [role.name.lower() for role in interaction.user.roles]:
                embed = discord.Embed(
                    description= "You need to have the 'DJ' role or be an admin to use this command!",
                    color = discord.Color.dark_purple()
                )
                return await interaction.response.send_message(embed = embed, ephemeral=True) """
        if song is None:
            embed = discord.Embed(
                description = f"Removed {playlistconfig['playlist'][0]} from playlist",
                color = discord.Color.dark_purple()
            )
            await interaction.response.send_message(embed = embed)
            playlistconfig["playlist"].pop(0)
        
        elif song == "*":
            playlistconfig["playlist"] = []
            embed = discord.Embed(
            description = "Cleared playlist",
            color = discord.Color.dark_purple()
        )
        else:
            if KTmusic.get_youtube_search_info(query = song)["title"] not in playlistconfig["playlist"]:
                embed = discord.Embed(
                    description = f"❌ **{song}** is not in the playlist",
                    color = discord.Color.red()
                )
                return await interaction.response.send_message(embed = embed)

            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, lambda: playlistconfig["playlist"].remove(KTmusic.get_youtube_search_info(query = song)["title"]))
            embed = discord.Embed(
            description = f"Removed **{song}** from the playlist",
            color = discord.Color.dark_purple()
        )
        await KTtools.save_playlist(playlistconfig, server_id)
        
        await interaction.response.send_message(embed = embed)

    @app_commands.command(name = "playlist", description = "Show the current playlist")
    async def playlist(self, interaction : discord.Interaction) -> None:
        server_id = str(interaction.guild.id)
        playlistconfig = await KTtools.load_playlist(server_id)
        
        if not playlistconfig["isplaying"]:
            embed = discord.Embed(
                description = "❌ I am not playing anything",
                color = discord.Color.red()
            )
            return await interaction.response.send_message(embed = embed)
        elif not playlistconfig["playlist"]:
            embed = discord.Embed(
                description = "❌ Playlist is empty",
                color = discord.Color.red()
            )
            return await interaction.response.send_message(embed = embed)
        
        loop = asyncio.get_event_loop()
        embed = await loop.run_in_executor(None, lambda: KTmusic.create_playlist_embed(playlistconfig = playlistconfig))
        await interaction.response.send_message(embed = embed)

    @app_commands.command(name = "resetmusic", description = "Resets the music bot in case something goes wrong and music cant play")
    async def resetmusic(self, interaction : discord.Interaction) -> None:

        if not await KTtools.interactionuser_has_permissions(interaction, ["administrator"]) or interaction.guild.owner_id != interaction.user.id:
            if "dj" not in [role.name.lower() for role in interaction.user.roles]:
                embed = discord.Embed(
                    description= "You need to have the 'DJ' role or be an admin to use this command!",
                    color = discord.Color.dark_purple()
                )
                return await interaction.response.send_message(embed = embed, ephemeral=True)
        

        server_id = str(interaction.guild.id)
        playlistconfig = await KTtools.load_playlist(server_id)
        playlistconfig["playlist"] = []
        playlistconfig["isplaying"] = False
        playlistconfig["repeat"] = False
        playlistconfig["shuffle"] = False
        await KTtools.save_playlist(playlistconfig, server_id)
        embed = discord.Embed(
            description = "✅ Music bot has been reset",
            color = discord.Color.green()
        )
        await interaction.response.send_message(embed = embed)

class Misc(commands.Cog):
    def __init__(self, client : commands.Bot) -> None:
        self.client = client
    
    @app_commands.command(name = "cat", description = "Sends a random cat image :3")
    async def cat(self, interaction : discord.Interaction) -> None:
        embed = discord.Embed(
            description = "Loading the perfect cat image...",
            color = discord.Color.dark_purple()
        )
        await interaction.response.send_message(embed = embed)
        
        loop = asyncio.get_event_loop()
        cat_img = await loop.run_in_executor(None, lambda: KTmisc.scrape_image_from_subreddit(subr = choice(["cats", "cat", "catpictures"])))
        
        if cat_img is not None:
            embed = discord.Embed(
                description = "Here's your cat image!!! >:3",
                color = discord.Color.dark_purple()
            )
            embed.set_image(url = cat_img)
        else:
            embed = discord.Embed(
                description = "Sorry, I couldn't find any cat images :(",
                color = discord.Color.dark_purple()
            )
        
        await interaction.channel.send(embed = embed)

#!START
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
@client.event
async def on_ready() -> None:
    await client.add_cog(Welcomer(client=client))
    await client.add_cog(Autorole(client=client))
    await client.add_cog(Automod(client = client))
    await client.add_cog(Music(client = client))
    await client.add_cog(Misc(client = client))
    await client.tree.sync()
    inactivity_check.start()
    
    print(f"{client.user} working")


#!MAIN
def main() -> None:
    client.run(token = TOKEN, log_handler=handler, root_logger=True)

if __name__ == "__main__":
    asyncio.run(reset_all_playlists())
    main()