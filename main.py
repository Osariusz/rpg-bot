from typing import Any
import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from bot import Bot

# Load environment variables from .env file
load_dotenv()

# Create an instance of the bot with proper intents
intents = discord.Intents.default()  # Modify intents if needed
bot = Bot(intents=intents)

# Event triggered when the bot is ready
@bot.event
async def on_ready() -> None:
    print(f"Bot is online! Logged in as {bot.user}")

# Run the bot
if __name__ == "__main__":
    # Load token from the environment
    bot.load_extension('cogs.greetings')
    TOKEN: str = os.getenv("DISCORD_TOKEN", "")
    if not TOKEN:
        raise ValueError("DISCORD_TOKEN not found in the .env file.")
    bot.run(TOKEN)
