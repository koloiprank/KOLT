
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

#!TOKEN
load_dotenv()
TOKEN : Final[str] = os.getenv('DISCORD_TOKEN')

intents : Intents = Intents.all()
client : Client = Client(intents = intents)
tree = app_commands.CommandTree(client)

#!FUNC
#*Chat+logging
@client.event
async def on_message(message: discord.Message):
    author = message.author
    channel = message.channel
    content = message.content
    
    if message.author != client.user:
        print(f">>> [{channel}]{author}: {content}")

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

#*Autorole On-react
@client.event
async def on_raw_reaction_add(payload):
    
    message = await client.get_channel(payload.channel_id).fetch_message(payload.message_id)
    reaction = str(discord.utils.get(message.reactions))
    user = payload.member
    config = await KTtools.load_config()
    
    if reaction in config["react_roles"] and str(payload.channel_id) in config["autorole_channels"]:
        
        role = config["react_roles"][reaction]
        
        if not user.bot:
            
            await user.add_roles(discord.Object(id = role))
            print(f"{user} has been given the role {role} from reaction {reaction}")

@client.event
async def on_raw_reaction_remove(payload):
   
    message = await client.get_channel(payload.channel_id).fetch_message(payload.message_id)
    reaction = str(discord.utils.get(message.reactions))
    user = message.guild.get_member(payload.user_id)
    config = await KTtools.load_config()
    
    
    if reaction in config["react_roles"] and str(payload.channel_id) in config["autorole_channels"]:
        
        role = config["react_roles"][reaction]
        
        if not user.bot:
            await user.remove_roles(discord.Object(id = role))
            print(f"{user} has been removed the role {role} from reaction removal {reaction}")
 
            
#*Welcome
@client.event
async def on_member_join(member: discord.Member):
    config = await KTtools.load_config()
    channel = member.guild.get_channel(int(config["welcome_channel"]))
    
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
    has_perms = await KTtools.has_permissions(interaction, permissions) or await KTtools.has_permissions(interaction, ["administrator"])
    
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
    has_perms = await KTtools.has_permissions(interaction, permissions) or await KTtools.has_permissions(interaction, ["administrator"])
    
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
    has_perms = await KTtools.has_permissions(interaction, permissions) or await KTtools.has_permissions(interaction, ["administrator"])
    
    if has_perms:
        config = await KTtools.load_config()
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
    has_perms = await KTtools.has_permissions(interaction, permissions) or await KTtools.has_permissions(interaction, ["administrator"])
    
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
    has_perms = await KTtools.has_permissions(interaction, permissions) or await KTtools.has_permissions(interaction, ["administrator"])
    
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
    has_perms = await KTtools.has_permissions(interaction, permissions) or await KTtools.has_permissions(interaction, ["administrator"])
    
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
    has_perms = await KTtools.has_permissions(interaction, permissions) or await KTtools.has_permissions(interaction, ["administrator"])
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
                
                config = await KTtools.load_config()
                config["react_roles"][str(emoji)] = str(role).strip("<@&>")
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







#!START
@client.event
async def on_ready() -> None:
    await tree.sync()
    print(f"{client.user} working")

#!MAIN
def main() -> None:
    client.run(token = TOKEN, log_handler=handler)
    
if __name__ == "__main__":
    main()