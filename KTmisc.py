import requests
from bs4 import BeautifulSoup
import asyncpraw
import random
import os
from dotenv import load_dotenv
import discord

#REDDIT LOAD
load_dotenv()
USERNAME = os.getenv("RD_USERNAME")
PASSW = os.getenv("RD_PASS")
SECRET = os.getenv("RD_SECRET")
CLIENT = os.getenv("RD_CLIENT")
AGENT = os.getenv("RD_AGENT")

async def scrape_image_from_subreddit(subr : str) -> str:
    async with asyncpraw.Reddit(
        client_id=CLIENT,
        client_secret=SECRET,
        password=PASSW,
        user_agent=AGENT,
        username=USERNAME,
    ) as reddit:
        sub = await reddit.subreddit(subr)
        posts = [submission async for submission in sub.hot(limit=40)]
        random_post_idx = random.randint(0, 40)

        #IMG SCRAPE
        try:
            url = posts[random_post_idx].url
            page = requests.get(url)
            soup = BeautifulSoup(page.content, "html.parser", from_encoding="iso-8859-1")

            images = soup.find_all("img")
            img = [img["src"] for img in images if img.has_attr("src") and "preview.redd.it" in img["src"]]
            
            if img:
                return img[0]
        except Exception:
            return None
        return None


#HELP
class PaginationView(discord.ui.View):
    current_page = 1
    sep = 5
   
    async def send(self, interaction):
        try:
            await interaction.response.send("Here is your help!:")
        except Exception: ...
        self.message = await interaction.channel.send(view = self)
        await self.update_message(self.data[:self.sep])
    
    def create_embed(self, data):
        embed = discord.Embed(title = "Help", color = discord.Color.dark_purple())
        for item in data:
            embed.add_field(name = "", value = f"`{item}`", inline = False)
        return embed
    
    async def update_message(self, data):
        await self.message.edit(embed = self.create_embed(data), view = self)
    
    
    @discord.ui.button(label = "<", style = discord.ButtonStyle.primary)
    async def next_butt(self, interaction : discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.current_page -= 1
        until_item = self.current_page * self.sep
        from_item = until_item - self.sep
        await self.update_message(self.data[from_item:until_item])
        
    @discord.ui.button(label = ">", style = discord.ButtonStyle.primary)
    async def prev_butt(self, interaction : discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.current_page += 1
        until_item = self.current_page * self.sep
        from_item = until_item - self.sep
        await self.update_message(self.data[from_item:until_item])
           
async def paginate(interaction: discord.Interaction, data):
    pagination_view = PaginationView()
    pagination_view.data = data
    await pagination_view.send(interaction=interaction)