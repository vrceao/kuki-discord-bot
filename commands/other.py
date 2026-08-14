import discord
from discord import app_commands
from bot import bot
import helper

# Todo: move these images and values or whatever to preferences.json so you can easily add them
@bot.tree.command(name="image", description="Display an image")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.choices(image=[
    app_commands.Choice(name="youmu_stare", value="youmu_stare"),
    app_commands.Choice(name="reimupressure", value="reimupressure"),
])
async def image(interaction: discord.Interaction, image: app_commands.Choice[str], in_embed: bool = True):
    helper.used_command("image")

    image_file = discord.File(f"assets/{image.value}.jpg", filename=f"{image.value}.jpg")

    if in_embed:
        embed = discord.Embed(
            color=discord.Color.yellow()
        )

        embed.set_image(url=f"attachment://{image.value}.jpg")

        await interaction.response.send_message(embed=embed, file=image_file)
    else:
        await interaction.response.send_message(file=image_file)