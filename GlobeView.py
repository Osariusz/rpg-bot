import discord

class GlobeView(discord.ui.View):

    def __init__(self, map_file_path: str, end_button : discord.ui.Button):
        super().__init__(timeout=None)
        self.map_file_path = map_file_path
        self.add_item(end_button)
