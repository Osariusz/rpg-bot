from typing import Any
from discord.ext import commands
import discord
from GlobeMessage import GlobeMessage, save_message_to_db, get_all_globe_messages, GlobeMessageORM

class Bot(commands.Bot):

    map_channels = [696979620888576060, 376020411324039182, 377846006949085184, 569937360922476564, 1237015868752269363]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    async def on_ready(self) -> None:
        print(f"Bot is online! Logged in as {self.user}")
        channel_message_ids: list[GlobeMessageORM] = get_all_globe_messages()
        for globe_message_orm in channel_message_ids:
            channel = await self.fetch_channel(int(globe_message_orm.channel_id))
            assert isinstance(channel, discord.TextChannel)
            message = await channel.fetch_message(int(globe_message_orm.message_id))
            globe_message = GlobeMessage(message, [float(globe_message_orm.latitude), float(globe_message_orm.longitude)])
            self.add_view(globe_message.create_globe_view())

    async def on_message(self, message: discord.Message):
        if(not message.author.bot and message.channel.id in self.map_channels and len(message.attachments) > 0):
            globe_message = GlobeMessage(message)
            await globe_message.send_globe_message()
            save_message_to_db(globe_message)

        