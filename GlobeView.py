import discord

from GlobeHandler import GlobeHandler

class GlobeView(discord.ui.View):

    def __init__(self, buttons : list[discord.ui.Button]):
        super().__init__(timeout=None)
        for button in buttons:
            self.add_item(button)
