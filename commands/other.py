import discord
from discord import app_commands
import hashlib
from bot import bot
import helper

hash_display_limit = 50

# Todo: move these images and values or whatever to preferences.json so you can easily add them
@bot.tree.command(name="image", description="Display an image")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.choices(image=[
    app_commands.Choice(name="youmu_stare", value="youmu_stare"),
    app_commands.Choice(name="reimupressure", value="reimupressure"),
])
async def image(interaction: discord.Interaction, image: app_commands.Choice[str], in_embed: bool = True):
    helper.used_command(interaction)

    image_file = discord.File(f"assets/{image.value}.jpg", filename=f"{image.value}.jpg")

    if in_embed:
        embed = discord.Embed(
            color=discord.Color.yellow()
        )

        embed.set_image(url=f"attachment://{image.value}.jpg")

        await interaction.response.send_message(embed=embed, file=image_file)
    else:
        await interaction.response.send_message(file=image_file)

@bot.tree.command(name="hash", description="Hash a string")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.choices(type=[
    app_commands.Choice(name="sha256", value="sha256"),
    app_commands.Choice(name="sha1", value="sha1"),
])
async def hash(interaction: discord.Interaction, text: str, type: app_commands.Choice[str] | None = None):
    helper.used_command(interaction)

    if type is None:
        type = app_commands.Choice(name="sha256", value="sha256")

    type = type.value

    original = f"`®️` Input: `{text}`"
    method = f"`🔓` Method: `{type}`"
    hashed = hashlib.sha256(text.encode()).hexdigest()
    hashed_string = f"`🔐` Hash: `{hashed}`"

    embed = discord.Embed(
        title=f"Hashing",
        description=f"{original}\n{method}\n{hashed_string}",
        color=discord.Color.yellow()
    )

    await interaction.response.send_message(embed=embed)