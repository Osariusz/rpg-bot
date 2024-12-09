import os
from pathlib import Path
import discord

from GlobeHandler import GlobeHandler
from GlobeView import GlobeView

class GlobeMessage():

    def __init__(self, message: discord.Message):
        self.message = message
        self.coords: list[float] = [0,0]
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

    async def create_view(self):
        await self.save_the_map()

        self.globe_handler.generate_planet_image(self.coords, self.temp_map_path())

        file = discord.File(self.temp_map_path())
        assert isinstance(self.message.channel, discord.TextChannel)
        channel: discord.TextChannel = self.message.channel

        embed = discord.Embed(
            title=f"{channel.name.capitalize()} {self.message.created_at.strftime('%d.%m.%Y')}",
            description="Tu doszło do koordmy",
            color=discord.Colour.blurple()
        )
        embed.set_image(url=f"attachment://{self.the_map_filename_from_message()}")

        end_button: discord.ui.Button = discord.ui.Button(label="finish")
        await channel.send(view=GlobeView(end_button), file=file, embed=embed)
        #self.delete_the_map(message)

