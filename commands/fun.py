import discord
from discord import app_commands

from bot import bot
import helper

@bot.tree.command(name="youmu_stare", description="Use this if you're confused")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def youmu_stare(interaction: discord.Interaction):
    helper.used_command("youmu_stare")

    image = discord.File("assets/youmu_stare.jpg", filename="youmu_stare.jpg")

    embed = discord.Embed(
        color=discord.Color.yellow()
    )

    embed.set_image(url="attachment://youmu_stare.jpg")

    await interaction.response.send_message(embed=embed, file=image)

@bot.tree.command(name="reimu_pressure", description="Use this if you're under pressure")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def reimu_pressure(interaction: discord.Interaction):
    helper.used_command("reimu_pressure")

    image = discord.File("assets/reimu_pressure.jpg", filename="reimu_pressure.jpg")

    embed = discord.Embed(
        color=discord.Color.yellow()
    )

    embed.set_image(url="attachment://reimu_pressure.jpg")

    await interaction.response.send_message(embed=embed, file=image)