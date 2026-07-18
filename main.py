import discord
from discord import app_commands
import os
from dotenv import load_dotenv
import time

from bot import bot
import helper

import commands.system
import commands.tibia
import commands.other
# Todo: Add roblox integration to share what game I'm playing
# Todo: Add discord integration (self-bot) (hard) (VERY HARD)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

preferences = helper.load_file("preferences.json")

bot_start_time = None

@bot.event
async def on_ready():
    print(f"{helper.prefix()} 🟢 {bot.user} is online!")

@bot.tree.command(name="ping", description="See if bot if online")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def ping(interaction: discord.Interaction):
    helper.used_command("ping")

    await interaction.response.send_message(f"`🟢` Online • Response time: {bot.latency * 1000:.2f}ms")

@bot.tree.command(name="info", description="View information about this bot")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def info(interaction: discord.Interaction):
    helper.used_command("info")

    repo = f"`🔗` Github: {preferences['github_repo']}"
    discord_timestamp = f"<t:{bot_start_time}:R>"
    time_since_start = f"`🕒` Bot started {discord_timestamp}"

    embed = discord.Embed(
        title=bot.user,
        description=f"{repo}\n{time_since_start}",
        color=discord.Color.yellow()
    )

    embed.set_footer(text=f"🟢 Online • Response time: {bot.latency * 1000:.2f}ms")

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="commands", description="View the commands for this bot")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def commands(interaction: discord.Interaction):
    helper.used_command("commands")

    # HARD

    # commands_string = ""
    # if preferences["count_commands"]:
    #     path = "data/counts.json"
    #     if not os.path.exists(path):
    #         return

    #     counts = helper.load_file("data/counts.json")
    #     for command_name, enabled in preferences["commands"].items():
    #         if enabled:
    #             if command_name in counts:

    #             commands_string += f"{command_name}\n"
    # else:
    #     for command_name, enabled in preferences["commands"].items():
    #         if enabled:
    #             commands_string += f"{command_name}\n"

    embed = discord.Embed(
        title=f"{bot.user} commands",
        description="Here display all the available commands and how many times they been used if count_commands is enabled",
        color=discord.Color.yellow()
    )

    embed.set_footer(text=f"⚙️ Total commands: yes")

    await interaction.response.send_message(embed=embed)

def setup():
    global bot_start_time
    bot_start_time = int(time.time())
    helper.init_logs()

    # Todo: Add info if bot token isnt in .env
    bot.run(BOT_TOKEN)

setup()