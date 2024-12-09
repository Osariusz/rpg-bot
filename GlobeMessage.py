import os
from pathlib import Path
import discord

from GlobeHandler import GlobeHandler
from GlobeView import GlobeView
from GlobeUtils import normalize_input

class GlobeMessage():

    def __init__(self, message: discord.Message):
        self.message = message
        self.embed_message = None
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

    def create_buttons(self) -> list[discord.ui.Button]:
        


        def change_latitude(change: float):
            self.coords[0] += change
            self.coords = normalize_input(self.coords)
        def change_longitude(change: float):
            self.coords[1] += change
            self.coords = normalize_input(self.coords)

        async def left(interaction : discord.Interaction):
            change_longitude(-25)
            await self.update_view(interaction)
        async def right(interaction : discord.Interaction):
            change_longitude(25)
            await self.update_view(interaction)
        async def up(interaction : discord.Interaction):
            change_latitude(25)
            await self.update_view(interaction)
        async def down(interaction : discord.Interaction):
            change_latitude(-25)
            await self.update_view(interaction)

        left_button: discord.ui.Button = discord.ui.Button(label="←")
        left_button.callback = left
        right_button: discord.ui.Button = discord.ui.Button(label="→")
        right_button.callback = right
        up_button: discord.ui.Button = discord.ui.Button(label="↑")
        up_button.callback = up
        down_button: discord.ui.Button = discord.ui.Button(label="↓")
        down_button.callback = down
        end_button: discord.ui.Button = discord.ui.Button(label="finish")

        return [
            left_button,
            up_button,
            down_button,
            right_button,
            end_button
        ]

    async def update_view(self, interaction : discord.Interaction):

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

        await interaction.edit(view=GlobeView(self.create_buttons()), file=file, embed=embed)
        self.delete_the_map(message)

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


        self.embed_message = await channel.send(view=GlobeView(self.create_buttons()), file=file, embed=embed)
        #self.delete_the_map(message)

