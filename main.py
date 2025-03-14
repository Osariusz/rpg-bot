from typing import Any
import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from bot import Bot

load_dotenv()
intents = discord.Intents.all()
bot = Bot(intents=intents)

if __name__ == "__main__":
    bot.load_extension('cogs.admin_cog')
    bot.load_extension('cogs.user_private_cog')
    TOKEN: str = os.getenv("DISCORD_TOKEN", "")
    if not TOKEN:
        raise ValueError("DISCORD_TOKEN not found in the .env file.")
    bot.run(TOKEN)
