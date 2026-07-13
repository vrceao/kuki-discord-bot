import discord
from discord import app_commands
import os
from dotenv import load_dotenv
import json
import time

from bot import bot
import helper

import commands.system
import commands.tibia
import commands.fun
# Todo: Add roblox integration to share what game I'm playing
# Todo: Add discord integration (self-bot) (hard) (VERY HARD)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

with open("preferences.json", "r", encoding="utf-8") as file:
    preferences = json.load(file)

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

    # Todo: this
    embed = Discord.embed(
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

    bot.run(BOT_TOKEN)

setup()