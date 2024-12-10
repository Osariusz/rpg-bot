import os
from pathlib import Path
import discord

from db.db import Base, engine, session
from globe.globe_handler import GlobeHandler
from globe.globe_view import GlobeView
from globe.globe_utils import normalize_input, coordinates_text

from sqlalchemy import Column, Integer, Float

class GlobeMessage():

    def __init__(self, message: discord.Message, coords: list[float] | None = None):
        self.message = message
        self.embed_message = None
        if(coords == None):
            coords = [0,0]
        assert coords is not None
        self.coords: list[float] = coords
        self.globe_handler = GlobeHandler(self.the_map_path_from_message())

    def the_map_path_from_message(self):
        return Path(f"maps/{self.the_map_filename_from_message()}")
    
    def the_map_filename_from_message(self):
        return Path(f"{str(self.message.id)}.png")

    def temp_map_path(self):
        return Path(f"temp/{self.the_map_filename_from_message()}")

    async def save_the_map(self):
        the_map = self.message.attachments[0]
        await the_map.save(self.the_map_path_from_message()) 
    
    def delete_the_map(self):
        os.remove(self.the_map_path_from_message())
    
    def delete_temp_map(self):
        os.remove(self.temp_map_path())

    def create_buttons(self) -> list[discord.ui.Button]:
        
        def change_latitude(change: float):
            self.coords[0] += change
            self.coords = normalize_input(self.coords)
            session.query(GlobeMessageORM).filter(GlobeMessageORM.message_id == self.message.id).update({'latitude': self.coords[0]})
            session.commit()
        def change_longitude(change: float):
            self.coords[1] += change
            self.coords = normalize_input(self.coords)
            session.query(GlobeMessageORM).filter(GlobeMessageORM.message_id == self.message.id).update({'longitude': self.coords[1]})
            session.commit()

        DEFAULT_HOP: int = 30
        async def left(interaction : discord.Interaction):
            change_longitude(-DEFAULT_HOP)
            await self.update_globe_message(interaction)
        async def right(interaction : discord.Interaction):
            change_longitude(DEFAULT_HOP)
            await self.update_globe_message(interaction)
        async def up(interaction : discord.Interaction):
            change_latitude(DEFAULT_HOP)
            await self.update_globe_message(interaction)
        async def down(interaction : discord.Interaction):
            change_latitude(-DEFAULT_HOP)
            await self.update_globe_message(interaction)

        def button_id(text_fragment: str) -> str:
            return f"{self.message.id}{text_fragment}"

        left_button: discord.ui.Button = discord.ui.Button(label="←", custom_id=button_id("left"))
        left_button.callback = left
        right_button: discord.ui.Button = discord.ui.Button(label="→", custom_id=button_id("right"))
        right_button.callback = right
        up_button: discord.ui.Button = discord.ui.Button(label="↑", custom_id=button_id("up"))
        up_button.callback = up
        down_button: discord.ui.Button = discord.ui.Button(label="↓", custom_id=button_id("down"))
        down_button.callback = down

        return [
            left_button,
            up_button,
            down_button,
            right_button
        ]

    async def get_current_state(self):
        await self.save_the_map()
        self.globe_handler.generate_planet_image(self.coords, self.temp_map_path())

        file = discord.File(self.temp_map_path())
        assert isinstance(self.message.channel, discord.TextChannel)
        channel: discord.TextChannel = self.message.channel

        embed = discord.Embed(
            title=f"{channel.name.capitalize()} {self.message.created_at.strftime('%d.%m.%Y')}",
            description=coordinates_text(self.coords),
            color=discord.Colour.blurple()
        )
        embed.set_image(url=f"attachment://{self.the_map_filename_from_message()}")
        return (file, embed)

    def create_globe_view(self):
        return GlobeView(self.create_buttons())

    async def update_globe_message(self, interaction : discord.Interaction):
        file, embed = await self.get_current_state()

        await interaction.edit(view=self.create_globe_view(), file=file, embed=embed)
        self.delete_the_map()
        self.delete_temp_map()

    async def send_globe_message(self):
        file, embed = await self.get_current_state()

        self.embed_message = await self.message.channel.send(view=self.create_globe_view(), file=file, embed=embed)
        self.delete_the_map()
        self.delete_temp_map()

    def get_message(self) -> discord.Message | None: 
        return self.message
    
class GlobeMessageORM(Base):
    __tablename__ = 'globe_messages'

    message_id = Column(Integer, primary_key=True)
    channel_id = Column(Integer)
    latitude = Column(Float)
    longitude = Column(Float)

def save_message_to_db(globe_message: GlobeMessage):
    orm_instance = GlobeMessageORM(
        message_id=globe_message.message.id,
        channel_id = globe_message.message.channel.id,
        latitude = globe_message.coords[0],
        longitude = globe_message.coords[1]
    )
    session.add(orm_instance)
    session.commit()

def get_all_globe_messages():
    messages = session.query(GlobeMessageORM).all()
    return messages
