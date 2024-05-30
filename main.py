
#*Discord
import discord
from discord import Intents, Client, app_commands

#*OS
from typing import Final
import os
from dotenv import load_dotenv
import logging

#*Custom modules
import KTwelcome
import KTtools
import KTautorole
import KTmoderation

#!TOKEN
load_dotenv()
TOKEN : Final[str] = os.getenv('DISCORD_TOKEN')

intents : Intents = Intents.all()
client : Client = Client(intents = intents)
tree = app_commands.CommandTree(client)

#!FUNC
#*Chat logging
@client.event
async def on_message(message: discord.Message):
    author = message.author
    channel = message.channel
    content = message.content
    
    if message.author != client.user:
        print(f">>> [{channel}]{author}: {content}")



#*Autorole On-react
@client.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    user = payload.member
    config = await KTtools.load_config()
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
    config = await KTtools.load_config()
    reaction = str(payload.emoji.name) 
    
    if reaction in config["react_roles"] and str(payload.channel_id) in config["autorole_channels"]:
        role = config["react_roles"][reaction]
        
        if not user.bot:
            await user.remove_roles(discord.Object(id = role))
            print(f"{user} has been cleared of the role {role} from reaction {reaction}")
 
            

#*Welcome
@client.event
async def on_member_join(member: discord.Member):
    config = await KTtools.load_config()
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
        
@tree.command(name = "setwelcomechannel", description = "Opens a dropdown menu to set your automatic welcome and goodbye channel")
async def set_welcome_channel(interaction : discord.Interaction) -> None:
    
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

@tree.command(name = "setwelcome", description= "Opens an embed with buttons to set your automatic welcome and goodbye message")
async def set_welcome_message(interaction : discord.Interaction) -> None:
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

@tree.command(name = "testwelcome", description = "Test the welcome message")
async def testwelcome(interaction : discord.Interaction) -> None:
    
    permissions = ["manage_channels", "manage_messages"]
    has_perms = await KTtools.interactionuser_has_permissions(interaction, permissions) or await KTtools.interactionuser_has_permissions(interaction, ["administrator"])
    
    if has_perms:
        config = await KTtools.load_config()
        
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
            
            await interaction.response.send_message(embed = embed)
        
        elif config["welcome_type"] == "image":
            
            if await KTwelcome.create_welcome_image(interaction.user, config) is not None:
                
                await interaction.channel.send(file = await KTwelcome.create_welcome_image(interaction.user, config))
            
            else:
                
                embed = discord.Embed(
                description= "❌ Couldn't send image.\nTry checking the image link is valid and setting it up again with /setwelcome .",
                colour = discord.Color.red()
                )
                
                await interaction.response.send_message("ERROR", ephemeral = True)
                await interaction.channel.send(embed = embed)

        elif config["welcome_type"] == "both":
            
            embed = discord.Embed(
                title="**WELCOME!!**",
                description= str(await KTwelcome.create_welcome_message(interaction.user, config)),
                color=discord.Color.dark_gold()
            )
            
            await interaction.response.send_message(embed = embed)
            
            if await KTwelcome.create_welcome_image(interaction.user, config) is not None:
                
                await interaction.channel.send(file = await KTwelcome.create_welcome_image(interaction.user, config))
            
            else:
                
                embed = discord.Embed(
                description= "❌ Couldn't send image.\nTry checking the image link is valid and setting it up again with /setwelcome .",
                colour = discord.Color.red()
                )
            
                await interaction.channel.send(embed = embed)
    else:
        embed = discord.Embed(
            description = "❌ You don't have permission to use this command.",
            color = discord.Color.red()
        )
        await interaction.response.send_message(embed = embed, ephemeral=True)



#*Autorole 
@tree.command(name = "addautorolechannel", description= "Adds the channel to the autorole list. Allows autorole react to work here.")
async def addautorolechannel(interaction : discord.Interaction) -> None:
    
    permissions = ["manage_channels", "manage_messages", "manage_roles"]
    has_perms = await KTtools.interactionuser_has_permissions(interaction, permissions) or await KTtools.interactionuser_has_permissions(interaction, ["administrator"])
    
    if has_perms:
        config = await KTtools.load_config()
        
        if str(interaction.channel.id) not in config["autorole_channels"]:
            config["autorole_channels"].append(str(interaction.channel.id))
            await KTtools.save_config(config)

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
    
@tree.command(name = "removeautorolechannel", description= "Removes the channel from the autorole-allowed channel list")
async def removeautorolechannel(interaction : discord.Interaction) -> None:
    
    permissions = ["manage_channels", "manage_messages", "manage_roles"]
    has_perms = await KTtools.interactionuser_has_permissions(interaction, permissions) or await KTtools.interactionuser_has_permissions(interaction, ["administrator"])
    
    if has_perms:
        config = await KTtools.load_config()

        if str(interaction.channel.id) in config["autorole_channels"]:
            
            config["autorole_channels"].remove(str(interaction.channel.id))
            await KTtools.save_config(config)
            
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

@tree.command(name = "autoroleonjoin", description= "Opens an embed with a dropdown to select automatic roles upon joining")
async def autoroleonjoin(interaction : discord.Interaction) -> None:
    
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

@tree.command(name = "autoroleonreact", description= "Reacts to the **LAST MESSAGE ON CHANNEL**. Sets roles for an emoji react.")
async def autoroleonreact(interaction : discord.Interaction, emoji : str, role : str) -> None:
    
    permissions = ["manage_channels", "manage_messages", "manage_roles"]
    has_perms = await KTtools.interactionuser_has_permissions(interaction, permissions) or await KTtools.interactionuser_has_permissions(interaction, ["administrator"])
    config = await KTtools.load_config()
    
    if has_perms:
        messageID = interaction.channel.last_message_id
        
        try:
            message = await interaction.channel.fetch_message(messageID)
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
                        description= "❌ Invalid emoji!",
                        color=discord.Color.red()
                        )
                    await interaction.response.send_message(embed = embed, ephemeral = True)
                    return

                config["react_roles"][await KTtools.format_emoji(str(emoji))] = str(role).strip("<@&>")
                await KTtools.save_config(config)
                await interaction.response.send_message("Done!", ephemeral = True)
            else:
                embed = discord.Embed(
                    description= "❌ This channel is not in autorole list.\nUse **/addautorolechannel** to add it, then try again.",
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



#*Moderation
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

#Warns
@tree.command(name = "warn", description= "Warns a user")
async def warn(interaction : discord.Interaction, member : discord.Member, reason : str) -> None:
    
    permissions = ["moderate_members"]
    has_perms = await KTtools.interactionuser_has_permissions(interaction, permissions) or await KTtools.interactionuser_has_permissions(interaction, ["administrator"])
    warns_mutes_kicks = await KTtools.load_WMK()
    
    if has_perms:
        if await is_member_punishable(interaction, member, "warn"):
            if str(member.id) not in warns_mutes_kicks:
                await KTmoderation.add_user(member)
                await KTmoderation.manual_warn(interaction, member, reason)
            else:
                await KTmoderation.manual_warn(interaction, member, reason)
    else:
        embed = discord.Embed(
            description= "❌ You don't have permission to use this command.",
            color = discord.Color.red()
        )
        await interaction.response.send_message(embed = embed, ephemeral=True)

@tree.command(name = "removewarn", description= "Removes 1 warn from a user")
async def removewarn(interaction : discord.Interaction, member : discord.Member) -> None:
    
    permissions = ["moderate_members"]
    has_perms = await KTtools.interactionuser_has_permissions(interaction, permissions) or await KTtools.interactionuser_has_permissions(interaction, ["administrator"])
    warns_mutes_kicks = await KTtools.load_WMK()
    
    if has_perms:
        if await is_member_punishable(interaction, member, "warn/unwarn"):
            if str(member.id) not in warns_mutes_kicks:
                await KTmoderation.add_user(member)
                await KTmoderation.manual_remove_warn(interaction, member,)
            else:
                await KTmoderation.manual_remove_warn(interaction, member)
    else:
        embed = discord.Embed(
            description= "❌ You don't have permission to use this command.",
            color = discord.Color.red()
        )
        await interaction.response.send_message(embed = embed, ephemeral=True)

@tree.command(name = "removeallwarns", description= "Removes all warns from a user")
async def removeallwarns(interaction : discord.Interaction, member : discord.Member) -> None:
    
    permissions = ["moderate_members"]
    has_perms = await KTtools.interactionuser_has_permissions(interaction, permissions) or await KTtools.interactionuser_has_permissions(interaction, ["administrator"])
    warns_mutes_kicks = await KTtools.load_WMK()
    
    if has_perms:
        
        if await is_member_punishable(interaction, member, "warn/unwarn"):
            if str(member.id) not in warns_mutes_kicks:
                await KTmoderation.add_user(member)
                await KTmoderation.manual_remove_all_warns(interaction, member,)
            else:
                await KTmoderation.manual_remove_all_warns(interaction, member)
    else:
        embed = discord.Embed(
            description= "❌ You don't have permission to use this command.",
            color = discord.Color.red()
        )
        await interaction.response.send_message(embed = embed, ephemeral=True)

#Mutes
@tree.command(name = "mute", description= "Mutes a user for x minutes")
async def mute(interaction : discord.Interaction, member : discord.Member, reason : str, duration : int) -> None:
    
    permissions = ["moderate_members"]
    has_perms = await KTtools.interactionuser_has_permissions(interaction, permissions) or await KTtools.interactionuser_has_permissions(interaction, ["administrator"])
    warns_mutes_kicks = await KTtools.load_WMK()
    
    if has_perms:
        if await is_member_punishable(interaction, member, "mute/unmute"):
            if str(member.id) not in warns_mutes_kicks:
                await KTmoderation.add_user(member)
                await KTmoderation.manual_mute(interaction, member, reason, duration)
            else:
                await KTmoderation.manual_mute(interaction, member, reason, duration)
    else:
        embed = discord.Embed(
            description= "❌ You don't have permission to use this command.",
            color = discord.Color.red()
        )
        await interaction.response.send_message(embed = embed, ephemeral=True)

@tree.command(name = "unmute", description= "Unmutes a user")
async def unmute(interaction : discord.Interaction, member : discord.Member) -> None:

    permissions = ["moderate_members"]
    has_perms = await KTtools.interactionuser_has_permissions(interaction, permissions) or await KTtools.interactionuser_has_permissions(interaction, ["administrator"])
    warns_mutes_kicks = await KTtools.load_WMK()
    
    if has_perms:
        if await is_member_punishable(interaction, member, "mute/unmute"):
            if str(member.id) not in warns_mutes_kicks:
                await KTmoderation.add_user(member)
                await KTmoderation.manual_unmute(interaction, member)
            else:
                await KTmoderation.manual_unmute(interaction, member)
    else:
        embed = discord.Embed(
            description= "❌ You don't have permission to use this command.",
            color = discord.Color.red()
        )
        await interaction.response.send_message(embed = embed, ephemeral=True)

@tree.command(name = "removemute", description= "Removes 1 mute count from a user, does NOT unmute")
async def removemute(interaction : discord.Interaction, member : discord.Member) -> None:
    
    permissions = ["moderate_members"]
    has_perms = await KTtools.interactionuser_has_permissions(interaction, permissions) or await KTtools.interactionuser_has_permissions(interaction, ["administrator"])
    warns_mutes_kicks = await KTtools.load_WMK()
    
    if has_perms:
        if await is_member_punishable(interaction, member, "mute/unmute"):
            if str(member.id) not in warns_mutes_kicks:
                await KTmoderation.add_user(member)
                await KTmoderation.manual_remove_mute(interaction, member)
            else:
                await KTmoderation.manual_remove_mute(interaction, member)
    else:
        embed = discord.Embed(
            description= "❌ You don't have permission to use this command.",
            color = discord.Color.red()
        )
        await interaction.response.send_message(embed = embed, ephemeral=True)

@tree.command(name = "removeallmutes", description= "Removes all mutes from a user, does NOT unmute")
async def removeallmutes(interaction : discord.Interaction, member : discord.Member) -> None:
    
    permissions = ["moderate_members"]
    has_perms = await KTtools.interactionuser_has_permissions(interaction, permissions) or await KTtools.interactionuser_has_permissions(interaction, ["administrator"])
    warns_mutes_kicks = await KTtools.load_WMK()
    
    if has_perms:
        if await is_member_punishable(interaction, member, "mute/unmute"):
            if str(member.id) not in warns_mutes_kicks:
                await KTmoderation.add_user(member)
                await KTmoderation.manual_remove_all_mutes(interaction, member)
            else:
                await KTmoderation.manual_remove_all_mutes(interaction, member)
    else:
        embed = discord.Embed(
            description= "❌ You don't have permission to use this command.",
            color = discord.Color.red()
        )
        await interaction.response.send_message(embed = embed, ephemeral=True)

#Kicks
@tree.command(name = "kick", description= "Kicks a user")
async def kick(interaction : discord.Interaction, member : discord.Member, reason : str) -> None:

    permissions = ["kick_members"]
    has_perms = await KTtools.interactionuser_has_permissions(interaction, permissions) or await KTtools.interactionuser_has_permissions(interaction, ["administrator"])
    warns_mutes_kicks = await KTtools.load_WMK()
    
    if has_perms:
        if await is_member_punishable(interaction, member, "kick"):
            if str(member.id) not in warns_mutes_kicks:
                await KTmoderation.add_user(member)
                await KTmoderation.manual_kick(interaction, member, reason) 
            else:
                await KTmoderation.manual_kick(interaction, member, reason)
    else:
        embed = discord.Embed(
            description= "❌ You don't have permission to use this command.",
            color = discord.Color.red()
        )
        await interaction.response.send_message(embed = embed, ephemeral=True)

@tree.command(name = "removekick", description= "Removes 1 kick count from a user, does NOT kick")
async def removekick(interaction : discord.Interaction, member : discord.Member) -> None:
    
    permissions = ["kick_members"]
    has_perms = await KTtools.interactionuser_has_permissions(interaction, permissions) or await KTtools.interactionuser_has_permissions(interaction, ["administrator"])
    warns_mutes_kicks = await KTtools.load_WMK()
    
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

@tree.command(name="removeallkicks", description= "Removes all kicks from a user, does NOT kick")
async def removeallkicks(interaction : discord.Interaction, member : discord.Member) -> None:
    
    permissions = ["kick_members"]
    has_perms = await KTtools.interactionuser_has_permissions(interaction, permissions) or await KTtools.interactionuser_has_permissions(interaction, ["administrator"])
    warns_mutes_kicks = await KTtools.load_WMK()
    
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
            
            await KTtools.save_WMK(warns_mutes_kicks)
    else:
        embed = discord.Embed(
            description= "❌ You don't have permission to use this command.",
            color = discord.Color.red()
        )
        await interaction.response.send_message(embed = embed, ephemeral=True)

#Ban
@tree.command(name = "ban", description= "Bans a user")
async def ban(interaction : discord.Interaction, member : discord.Member, reason : str) -> None:

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
@tree.command(name = "setmaxwarncount", description= "Sets the max warn count")
async def setmaxwarncount(interaction : discord.Interaction,count : int) -> None:
    
    permissions = ["administrator"]
    has_perms = await KTtools.interactionuser_has_permissions(interaction, permissions)
    
    if has_perms:
        if count < 0:
            embed = discord.Embed(
                description= "❌ Count must be greater than 0.",
                color = discord.Color.red()
            )
            return await interaction.response.send_message(embed = embed, ephemeral=True)
        config = await KTtools.load_config()
        config["max_warns"] = count
        await KTtools.save_config(config)
        
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

@tree.command(name = "setmaxmutecount", description= "Sets the max mute count")
async def setmaxmutecount(interaction : discord.Interaction,count : int) -> None:
    
    permissions = ["administrator"]
    has_perms = await KTtools.interactionuser_has_permissions(interaction, permissions)
    
    if has_perms:
        if count < 0:
            embed = discord.Embed(
                description= "❌ Count must be greater than 0.",
                color = discord.Color.red()
            )
            return await interaction.response.send_message(embed = embed, ephemeral=True)
        config = await KTtools.load_config()
        config["max_mutes"] = count
        await KTtools.save_config(config)
        
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

@tree.command(name = "setmuteduration", description = "Sets automod mute duration in minutes")
async def setmuteduration(interaction : discord.Interaction, duration : int) -> None:
    
    permissions = ["administrator"]
    has_perms = await KTtools.interactionuser_has_permissions(interaction, permissions)
    
    if has_perms:
        if duration < 0:
            embed = discord.Embed(
                description= "❌ Duration must be greater than 0.",
                color = discord.Color.red()
            )
            return await interaction.response.send_message(embed = embed, ephemeral=True)
        config = await KTtools.load_config()
        config["mute_duration"] = duration
        await KTtools.save_config(config)
        
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

@tree.command(name="setmaxkickcount", description= "Sets the max kick count")
async def setmaxkickcount(interaction : discord.Interaction,count : int) -> None:
    
    permissions = ["administrator"]
    has_perms = await KTtools.interactionuser_has_permissions(interaction, permissions)
    
    if has_perms:
        if count < 0:
            embed = discord.Embed(
                description= "❌ Count must be greater than 0.",
                color = discord.Color.red()
            )
            return await interaction.response.send_message(embed = embed, ephemeral=True)
        config = await KTtools.load_config()
        config["max_kicks"] = count
        await KTtools.save_config(config)
        
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



#!START
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
@client.event
async def on_ready() -> None:
    await tree.sync()
    print(f"{client.user} working")

#!MAIN
def main() -> None:
    client.run(token = TOKEN, log_handler=handler, root_logger=True)
    
if __name__ == "__main__":
    main()