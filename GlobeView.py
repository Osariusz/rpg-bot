import discord

from GlobeHandler import GlobeHandler

class GlobeView(discord.ui.View):

    def __init__(self, end_button : discord.ui.Button):
        super().__init__(timeout=None)
        self.add_item(end_button)
