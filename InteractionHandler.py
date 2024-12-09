import discord
import os

class MessageHandler():

    MESSAGES_PATH: str = "messages.txt"
    TUPLE_SPLITTER: str = ","

    def __init__(self) -> None:
        self.channel_message_ids: list[tuple[int, int]] | None = None

    def save_messages(self):
        with open(self.MESSAGES_PATH, "w") as file:
            file.writelines(f"{x}{self.TUPLE_SPLITTER}{y}\n" for x,y in self.channel_message_ids)

    def read_messages(self):
        if(os.path.isfile(self.MESSAGES_PATH)):
            with(open(self.MESSAGES_PATH, "r")) as file:
                self.channel_message_ids = [tuple(map(int, line.strip().split(self.TUPLE_SPLITTER))) for line in file]
        else:
            print("No messages file present!")

    def initialize_channel_message_ids(self):
        self.channel_message_ids = []
        self.read_messages()

    def add_message(self, message: discord.Message):
        if(not self.channel_message_ids):
            self.initialize_channel_message_ids()
        assert self.channel_message_ids is not None
        self.channel_message_ids.append((message.channel.id, message.id))
        self.save_messages()
    
    def get_channel_message_ids(self) -> list[tuple[int, int]]:
        if(not self.channel_message_ids):
            self.initialize_channel_message_ids()
        assert self.channel_message_ids is not None
        return self.channel_message_ids