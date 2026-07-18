import discord
from discord import app_commands

import helper

preferences = helper.load_file("preferences.json")

class MyBot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        for command in preferences["commands"]:
            if not command["enabled"]:
                self.tree.remove_command(command["name"])
        await self.tree.sync()

bot = MyBot()