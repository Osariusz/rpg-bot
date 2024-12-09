from typing import Any
from discord.ext import commands
import discord
from GlobeMessage import GlobeMessage
from GlobeView import GlobeView
from InteractionHandler import MessageHandler

class Bot(commands.Bot):

    map_channels = [696979620888576060, 376020411324039182, 377846006949085184, 569937360922476564, 1237015868752269363]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.interaction_handler = MessageHandler()

    async def on_ready(self) -> None:
        print(f"Bot is online! Logged in as {self.user}")
        channel_message_ids: list[tuple[int, int]] = self.interaction_handler.get_channel_message_ids()
        for channel_id, message_id in channel_message_ids:
            channel = await self.fetch_channel(channel_id)
            assert isinstance(channel, discord.TextChannel)
            message = await channel.fetch_message(message_id)
            globe_message = GlobeMessage(message)
            self.add_view(globe_message.create_globe_view())

    async def on_message(self, message: discord.Message):
        if(not message.author.bot and message.channel.id in self.map_channels and len(message.attachments) > 0):
            globe_message = GlobeMessage(message)
            await globe_message.send_globe_message()
            self.interaction_handler.add_message(globe_message.message)

        