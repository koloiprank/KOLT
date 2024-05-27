
#*Discord
import discord

#*OS
import json

#*Tools
import KTtools
from easy_pil import Editor, load_image_async, Font


#Welcome channel select
class ChannelDropdown(discord.ui.Select):
    
    def __init__(self, guild : discord.Guild) -> None:
        
        channel_list = guild.text_channels
        
        options = [ discord.SelectOption( label = channel.name, value = channel.id ) for channel in channel_list ]
        super().__init__(placeholder = "Select channel", options=options, min_values=1, max_values=1)  

    async def callback(self, interaction : discord.Interaction) -> None:
        
        channel_ID = self.values[0]
        
        set_welcome_channel(channel_ID)
        
        embed = discord.Embed(colour = discord.Colour.dark_purple(), description = f"Selected welcome channel: **#{interaction.guild.get_channel(int(channel_ID))}**")
        await interaction.response.send_message(embed = embed)
class ChannelView(discord.ui.View):
    
    def __init__(self, guild : discord.Guild) -> None:
        super().__init__()
        self.add_item(ChannelDropdown(guild))

async def select_welcome_channel(interaction : discord.Interaction) -> None:
    
    embed = discord.Embed(
        colour = discord.Colour.dark_purple(),
        title = "Set your automatic welcome and goodbye channel",
        description ="Select your channel to set as automatic welcome and goodbye channel."
    )
    
    await interaction.response.send_message(embed = embed, view=ChannelView(interaction.guild))
    
def set_welcome_channel(channelID : int) -> None: 
    with open("/config.json", "r+") as file:
        adminvars = json.load(file)
        adminvars.update({"welcome_channel" : channelID})
    file.close()
    
    with open("/config.json", "r+") as file:
        json.dump(adminvars, file)
    file.close()
 


#Welcome text select
async def select_welcome(interaction : discord.Interaction) -> None:
    embed = discord.Embed(
        colour = discord.Colour.dark_purple(),
        title = "Set your automatic welcome and goodbye message",
        description = f"Select your automatic welcome as a message.\nPress the button below and write your message or image link on the pop-up.\n\nIf you select image, paste the image link in the message field.\n\nIf you select message, type the text you want to display on join. Use **@user** or **@server** to mention the user or the server.\n\nExample: \n**@user Welcome to @server!!**\n**{interaction.user.mention} Welcome to {interaction.guild.name}!!**\n\nIf you select Both, you will be asked to set a message and an image link."
    )
    
    view = ButtonImgMsg()
    await interaction.response.send_message(embed = embed, view = view)
    await view.wait()

class ButtonImgMsg(discord.ui.View):
    
    @discord.ui.button(label = "Image", style = discord.ButtonStyle.green)
    async def img_select(self, interaction : discord.Interaction, button : discord.ui.Button) -> None:
        
        image_modal = ImageInput()
        await interaction.response.send_modal(image_modal)
        
        set_welcome_type("image")
        
    @discord.ui.button(label = "Message", style = discord.ButtonStyle.green)
    async def msg_select(self, interaction : discord.Interaction, button : discord.ui.Button) -> None:
        
        message_modal = MessageInput()
        await interaction.response.send_modal(message_modal)
        
        set_welcome_type("message")

    @discord.ui.button(label = "Both", style = discord.ButtonStyle.green)
    async def both_select(self, interaction : discord.Interaction, button : discord.ui.Button) -> None:
        
        message_modal = BothInput()
        await interaction.response.send_modal(message_modal)
        
        set_welcome_type("both")

class MessageInput(discord.ui.Modal, title= "Set message"):
    message = discord.ui.TextInput(
        style = discord.TextStyle.short,
        label = "Message",
        required = True,
        placeholder = "Type here"
    )
    
    async def on_submit(self, interaction: discord.Interaction) -> None:
        message = self.message.value
        set_welcome_msg(message)
        
        embed = discord.Embed(
            description= "✅ Message set succesfully.",
            colour = discord.Color.green()
        )
        
        await interaction.response.send_message(embed = embed)
        
        self.stop()
  
class ImageInput(discord.ui.Modal, title = "Set image link"):
    image = discord.ui.TextInput(
        style = discord.TextStyle.short,
        label = "Image link",
        required = True,
        placeholder = "Type here"
    )
    
    async def on_submit(self, interaction: discord.Interaction) -> None:
        imagelink = self.image.value
        set_welcome_image(imagelink)
        
        embed = discord.Embed(
            description= "✅ Image link set succesfully.",
            colour = discord.Color.green()
        )
        
        await interaction.response.send_message(embed = embed)
        
        self.stop()
  
class BothInput(discord.ui.Modal, title = "Set message and image link"):
    text = discord.ui.TextInput(
        style = discord.TextStyle.short,
        label = "Welcoming text",
        required = True,
        placeholder = "TEXT"
    ) 
    image = discord.ui.TextInput(
        style = discord.TextStyle.short,
        label = "Image link",
        required = True,
        placeholder= "IMAGE LINK"
    )
    
    async def on_submit(self, interaction: discord.Interaction) -> None:
        imagelink = self.image.value
        set_welcome_image(imagelink)
        message = self.text.value
        set_welcome_msg(message)
        
        
        embed = discord.Embed(
            description= "✅ Image link and message set succesfully.",
            colour = discord.Color.green()
        )
        
        await interaction.response.send_message(embed = embed)
        
        self.stop()

def set_welcome_type(typ : str) -> None:
    with open("config.json", "r+") as file:
        adminvars = json.load(file)
        adminvars.update({"welcome_type" : typ})
    file.close()
    
    with open("config.json", "w") as file:
        json.dump(adminvars, file)
    file.close()

def set_welcome_msg(msg : str) -> None:
    with open("config.json", "r+") as file:
        adminvars = json.load(file)
        adminvars.update({"welcome_message" : msg})
    file.close()
    
    with open("config.json", "w") as file:
        json.dump(adminvars, file)
    file.close()
    
def set_welcome_image(url : str) -> None:
    with open("config.json", "r+") as file:
        adminvars = json.load(file)
        adminvars.update({"welcome_image" : url})
    file.close()
    
    with open("config.json", "w") as file:
        json.dump(adminvars, file)
    file.close()



#Welcome send message
async def create_welcome_message(member : discord.Member, config : dict[str : str]) -> str:
    message = await KTtools.format_message(msg = config["welcome_message"], member = member, guild = member.guild)
    
    return message

#Welcome send image 
async def create_welcome_image(member : discord.Member, config : dict[str : str]) -> discord.File:
    try:
        message_big1 = "Welcome to"
        message_big2 = member.guild.name
        message_small = member.name
        font_big = Font.poppins(size = 55, variant = "bold")
        font_mid = Font.poppins(size = 48, variant = "bold")
        font_small = Font.poppins(size = 40, variant = "light")
        
        if member.avatar is not None:
            profile_image = await load_image_async(member.avatar.url)
        else:
            profile_image = await load_image_async(member.default_avatar.url)
            
        profile = Editor(profile_image).resize((200, 200)).circle_image()
        background = Editor(await load_image_async(config["welcome_image"])).resize((1244, 700))

        background.paste(profile, (522, 150))
        background.ellipse((522, 150), 200, 200, outline= "white", stroke_width = 5)
        background.text((622, 360), message_big1, color="white", font=font_mid, align="center")
        background.text((622, 410), message_big2, color="white", font=font_big, align="center")
        background.text((622, 470), message_small, color="white", font=font_small, align="center")
        
        file = discord.File(fp = background.image_bytes, filename = "welcome.png")
        return file
    
    except Exception:
        return None