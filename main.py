import discord
from discord import app_commands
import time

from bot import bot
import helper

import commands.system
import commands.tibia
import commands.other
import commands.minecraft
# Todo: Add roblox integration to share what game I'm playing
# Todo: Add discord integration (self-bot) (hard) (VERY HARD)

BOT_TOKEN = helper.env("BOT_TOKEN")

preferences = helper.load_file("preferences.jsonc")

bot_start_time = None

@bot.event
async def on_ready():
    print(f"{helper.prefix()} 🟢 {bot.user} is online!")



@bot.tree.command(name="ping", description="Check if bot is online")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def ping(interaction: discord.Interaction):
    if not await helper.check_permissions(interaction): return
    helper.used_command(interaction)
    config = helper.get_command_config(interaction)

    unit = config["unit"]
    latency = bot.latency * 1000

    if unit == "μs":
        latency = latency * 1000
    elif unit == "s":
        latency = latency / 1000
    elif unit != "ms":
        helper.error_command(interaction, "Unit was not assigned to a proper unit. Please use one of the following: s, ms, μs. Defaulting to ms")
        unit = "ms"

    response = helper.replace_format_values(config["format"], [
        ["{PING}", f"{latency:.{config["precision"]}f}"],
        ["{UNIT}", unit]
    ])

    await interaction.response.send_message(response)



@bot.tree.command(name="info", description="View information about the bot")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def info(interaction: discord.Interaction):
    if not await helper.check_permissions(interaction): return
    helper.used_command(interaction)
    config = helper.get_command_config(interaction)

    repo = config["repo_format"]

    timestamp = f"<t:{bot_start_time}:R>"
    started = helper.replace_format_values(config["started_format"], [
        ["{TIMESTAMP}", timestamp]
    ])
 
    embed = discord.Embed(
        title=bot.user,
        description=helper.replace_format_values(config["format"], [
            ["{REPO}", repo],
            ["{STARTED}", started]
        ]),
        color=discord.Color.yellow()
    )

    embed.set_footer(text=f"🟢 Online • Response time: {bot.latency * 1000:.2f}ms")

    await interaction.response.send_message(embed=embed)



@bot.tree.command(name="commands", description="View available commands")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def commands(interaction: discord.Interaction):
    if not await helper.check_permissions(interaction): return
    helper.used_command(interaction)
    config = helper.get_command_config(interaction)

    total_commands = 0
    total_commands_used = 0

    command_list = ""
    for command in preferences["commands"]:
        if command["enabled"]:
            total_commands += 1
            count = config["count_for_disabled_count_commands"]
            if preferences["count_commands"]:
                count = helper.load_file("data/counts.json")[command["name"]]
                total_commands_used += count
            command_list += helper.replace_format_values(config["command_list_entry_format"], [
                ["{EMOJI}", command.get("emoji", config["default_emoji"])],
                ["{NAME}", command["name"]],
                ["{COUNT}", count],
                ["{DESCRIPTION}", command.get("description", config["no_description"])]
            ])
            command_list += "\n"

    embed = discord.Embed(
        title=helper.replace_format_values(config["title"], [
            ["{BOT}", str(bot.user)]
        ]),
        description=helper.replace_format_values(config["format"], [
            ["{COMMAND_LIST}", command_list]
        ]),
        color=discord.Color.yellow()
    )

    if total_commands_used == 0:
        total_commands_used = config["count_for_disabled_count_commands"]
    embed.set_footer(text=helper.replace_format_values(config["footer_format"], [
        ["{COUNT}", total_commands],
        ["{USED}", total_commands_used]
    ]))

    await interaction.response.send_message(embed=embed)



def setup():
    global bot_start_time
    bot_start_time = int(time.time())
    helper.init_temp()
    helper.init_logs()

    # Todo: Add info if bot token isnt in .env
    bot.run(BOT_TOKEN)

setup()