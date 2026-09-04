import discord
from discord import app_commands
from mcstatus import JavaServer
import base64
import re
from bot import bot
import helper

DEFAULT_MINECRAFT_SERVER_IP = helper.env("DEFAULT_MINECRAFT_SERVER_IP")

@bot.tree.command(name="minecraft_server", description="View information about a Minecraft server")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def minecraft_server(interaction: discord.Interaction, ip: str = DEFAULT_MINECRAFT_SERVER_IP):
    helper.used_command(interaction)

    server = JavaServer.lookup(ip)
    status = server.status()

    motd = f"`ℹ️` {re.sub("§.", "", status.description)}".replace("\n", "\n`ℹ️` ")
    version = f"`⚙️` Version: {status.version.name}"
    player_count = f"`📊` Player count: {status.players.online}/{status.players.max}"

    # Todo: Add player limit in preferences
    if status.players.sample != None and status.players.sample != []:
        if len(status.players.sample) != 0:
            if len(status.players.sample) == 1:
                player_list = "`👤` "
            else:
                player_list = "`👥` "
            for player in status.players.sample:
                player_list += f"{player.name}, "
            player_list = player_list.rstrip(", ")
    else:
        player_list = "`⚠️` Player list is hidden on this server"

    favicon = status.raw.get("favicon")
    if favicon:
        icon_path = f"temp/{ip.replace(".", "_")}.png"
        header, data = favicon.split(",", 1)
        with open(icon_path, "wb") as f:
            f.write(base64.b64decode(data))
    else:
        icon_path = "assets/minecraft/default.jpg"
    icon_image = discord.File(icon_path, filename=f"icon.jpg")

    embed = discord.Embed(
        title=ip,
        description=f"{motd}\n{version}\n{player_count}\n{player_list}",
        color=discord.Color.yellow()
    )

    embed.set_thumbnail(url=f"attachment://icon.jpg")

    # embed.set_image(url=f"attachment://{image.value}.jpg")

    await interaction.response.send_message(embed=embed, file=icon_image)