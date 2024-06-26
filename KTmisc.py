import requests
from bs4 import BeautifulSoup
import asyncpraw
import random
import os
from dotenv import load_dotenv

#REDDIT LOAD
load_dotenv()
USERNAME = os.getenv("RD_USERNAME")
PASSW = os.getenv("RD_PASS")
SECRET = os.getenv("RD_SECRET")
CLIENT = os.getenv("RD_CLIENT")
AGENT = os.getenv("RD_AGENT")


##TODO FIX THIS TO WORK WITH ASYNCPRAW
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

            