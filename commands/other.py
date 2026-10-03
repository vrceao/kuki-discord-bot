import os
import random
from datetime import datetime
import discord
from discord import app_commands
import hashlib
from bot import bot
import helper

hash_display_limit = 50

preferences = helper.load_file("preferences.jsonc")



# Todo: move choices to preferences
# Todo: add ability to hash files
command = helper.get_command_info("hash")
@bot.tree.command(name=command["name"], description=command["description"])
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.choices(type=[
    app_commands.Choice(name="sha256", value="sha256"),
    app_commands.Choice(name="sha1", value="sha1"),
])
async def hash(interaction: discord.Interaction, text: str, type: app_commands.Choice[str] | None = None):
    if not await helper.check_permissions(interaction): return
    helper.used_command(interaction)
    config = helper.get_command_info(interaction)["config"]

    if type is None:
        type = app_commands.Choice(name="sha256", value="sha256")

    type = type.value

    if type == "sha1":
        hashed_string = hashlib.sha1(text.encode()).hexdigest()
    else:
        hashed_string = hashlib.sha256(text.encode()).hexdigest()

    original = helper.replace_format_values(config["original_format"], [
        ["{ORIGINAL}", text]
    ])
    method = helper.replace_format_values(config["method_format"], [
        ["{METHOD}", type]
    ])
    hash = helper.replace_format_values(config["hash_format"], [
        ["{HASH}", hashed_string]
    ])

    embed = discord.Embed(
        title=config["title"],
        description=helper.replace_format_values(config["format"], [
            ["{ORIGINAL}", original],
            ["{METHOD}", method],
            ["{HASH}", hash]
        ]),
        color=discord.Color.yellow()
    )

    await interaction.response.send_message(embed=embed)



picture_pools = helper.get_command_info("picture")["config"]["pools"]
picture_choices = [
    app_commands.Choice(name=pool["name"], value=pool["value"])
    for pool in picture_pools
]

command = helper.get_command_info("picture")
@bot.tree.command(name=command["name"], description=command["description"])
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.choices(pool=picture_choices)
async def picture(interaction: discord.Interaction, pool: app_commands.Choice[str], raw: bool = False):
    if not await helper.check_permissions(interaction): return
    helper.used_command(interaction)
    config = helper.get_command_info(interaction)["config"]

    directory = None

    for pool_ in config["pools"]:
        if pool_["value"] == pool.value:
            directory = pool_["directory"]

    drawings = os.listdir(directory)
    drawing = os.path.join(directory, drawings[random.randint(0, len(drawings) - 1)])
    date = str(datetime.fromtimestamp(os.path.getmtime(drawing))).split(".")[0]

    image_file = discord.File(drawing, filename="picture.png")

    if not raw:
        embed = discord.Embed(
            title=helper.replace_format_values(config["title"], [
                ["{DATE}", date]
            ]),
            color=discord.Color.yellow()
        )

        embed.set_image(url=f"attachment://picture.png")

        await interaction.response.send_message(embed=embed, file=image_file)
    else:
        await interaction.response.send_message(file=image_file)