from typing import Any
from discord.ext import commands
import discord
from pathlib import Path
from GlobeView import GlobeView
import os

class Bot(commands.Bot):

    map_channels = []

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    def the_map_path_from_message(self, message: discord.Message):
        return Path(f"maps/{str(message.id)}.png")

    async def save_the_map(self, message: discord.Message):
        the_map = message.attachments[0]
        await the_map.save(self.the_map_path_from_message(message)) 
    
    def delete_the_map(self, message: discord.Message):
        os.remove(self.the_map_path_from_message(message))

    async def create_view(self, message: discord.Message):
        await self.save_the_map(message)

        file = discord.File(self.the_map_path_from_message(message))
        assert isinstance(message.channel, discord.TextChannel)
        channel: discord.TextChannel = message.channel

        embed = discord.Embed(
            title=f"{channel.name.capitalize()} {message.created_at.strftime('%d.%m.%Y')}",
            description="Tu doszło do koordmy",
            color=discord.Colour.blurple()
        )
        embed.set_image(url=f"attachment://{str(message.id)}.png")

        end_button: discord.ui.Button = discord.ui.Button(label="finish")
        await channel.send(view=GlobeView(self.the_map_path_from_message(message), end_button), file=file, embed=embed)
        self.delete_the_map(message)

    async def on_message(self, message: discord.Message):
        if(message.channel.id in self.map_channels and len(message.attachments) > 0):
            await self.create_view(message)

        