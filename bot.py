import os
from typing import Any
from discord.ext import commands
import discord
from db.message_thread import get_all_message_thread_channels
from globe.globe_message import GlobeMessage, save_message_to_db, get_all_globe_messages, GlobeMessageORM
from globe.globe_dedicated_channel import get_all_globe_dedicated_channels
from db.db import Base, engine
import pyvista
from db.statistics import UserORM, save_to_db

class Bot(commands.Bot):

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.map_channels = []
        self.message_thread_channels = []

    def refresh_map_channels(self):
        self.map_channels = [channel.id for channel in get_all_globe_dedicated_channels()]

    def refresh_message_thread_channels(self):
        self.message_thread_channels = [channel.id for channel in get_all_message_thread_channels()]

    async def on_ready(self) -> None:
        should_start_xvfb: bool = os.getenv("START_XVFB", False) == "True"
        if(should_start_xvfb):
            pyvista.start_xvfb()

        Base.metadata.create_all(engine)
        self.refresh_map_channels()
        self.refresh_message_thread_channels()
        channel_message_ids: list[GlobeMessageORM] = get_all_globe_messages()
        for globe_message_orm in channel_message_ids:
            try:
                channel = await self.fetch_channel(int(globe_message_orm.channel_id))
                assert isinstance(channel, discord.TextChannel) or isinstance(channel, discord.Thread)
                message = await channel.fetch_message(int(globe_message_orm.message_id))
                globe_message = GlobeMessage(message, [float(globe_message_orm.latitude), float(globe_message_orm.longitude)])
                self.add_view(globe_message.create_globe_view())
            except Exception as e:
                print(e)
        print(f"Bot is online! Logged in as {self.user}")


    async def on_message(self, message: discord.Message):
        if(not message.author.bot and message.channel.id in self.map_channels and len(message.attachments) > 0):
            globe_message = GlobeMessage(message)
            await globe_message.send_globe_message()
            save_message_to_db(globe_message)
        if(not message.author.bot and message.channel.id in self.message_thread_channels):
            cleaner_content: str = discord.utils.remove_markdown(message.clean_content)
            message_content_lines: list[str] = cleaner_content.split("\n")
            name: str = "thread"
            if(len(message_content_lines) > 0 and len(message_content_lines[0]) > 0):
                name = message_content_lines[0]
            await message.create_thread(name=name)

        
