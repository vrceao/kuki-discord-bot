import os
import random
import discord
from discord import app_commands
import hashlib
from bot import bot
import helper

hash_display_limit = 50

preferences = helper.load_file("preferences.jsonc")
picture_pools = helper.get_command_config("picture")["pools"]

picture_choices = [
    app_commands.Choice(name=pool["name"], value=pool["value"])
    for pool in picture_pools
]



@bot.tree.command(name="hash", description="Hash a string")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.choices(type=[
    app_commands.Choice(name="sha256", value="sha256"),
    app_commands.Choice(name="sha1", value="sha1"),
])
async def hash(interaction: discord.Interaction, text: str, type: app_commands.Choice[str] | None = None):
    if not await helper.check_permissions(interaction): return
    helper.used_command(interaction)
    config = helper.get_command_config(interaction)

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



@bot.tree.command(name="picture", description="Get a random picture from a selected pool")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.choices(pool=picture_choices)
async def image(interaction: discord.Interaction, pool: app_commands.Choice[str], in_embed: bool = True):
    if not await helper.check_permissions(interaction): return
    helper.used_command(interaction)
    config = helper.get_command_config(interaction)

    directory = None

    for pool_ in config["pools"]:
        if pool_["value"] == pool.value:
            directory = pool_["directory"]

    drawings = os.listdir(directory)
    drawing = os.path.join(directory, drawings[random.randint(0, len(drawings) - 1)])

    image_file = discord.File(drawing, filename="picture.png")

    if in_embed:
        embed = discord.Embed(
            color=discord.Color.yellow()
        )

        embed.set_image(url=f"attachment://picture.png")

        await interaction.response.send_message(embed=embed, file=image_file)
    else:
        await interaction.response.send_message(file=image_file)