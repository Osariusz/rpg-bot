from typing import Any
from discord.ext import commands
import discord
from GlobeMessage import GlobeMessage

class Bot(commands.Bot):

    map_channels = [696979620888576060, 376020411324039182]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    async def on_message(self, message: discord.Message):
        if(message.channel.id in self.map_channels and len(message.attachments) > 0):
            await GlobeMessage(message).create_view()

        