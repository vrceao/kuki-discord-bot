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
    if not await helper.check_permissions(interaction): return
    helper.used_command(interaction)
    config = helper.get_command_config(interaction)

    server = JavaServer.lookup(ip)
    status = server.status()

    motd = f"{config["motd_prefix"]}{re.sub("§.", "", status.description)}".replace("\n", f"\n{config["motd_prefix"]}")

    version = helper.replace_format_values(config["version_format"], [
        ["{VERSION}", status.version.name]
    ])

    player_count = helper.replace_format_values(config["player_count_format"], [
        ["{ONLINE}", status.players.online],
        ["{MAX}", status.players.max]
    ])

    # Todo: Add player limit in preferences
    pl = status.players.sample
    if pl != [] and pl != None:
        weird = False
        for player in pl:
            if "§" in player.name:
                weird = True
        if weird:
            player_list = config["player_list_messages"]["custom"]
        else:
            # reminding_players = 0
            # if len(pl) > config["player_list_max_players"]:
            #     pl = pl[:config["player_list_max_players"]]
            #     reminding_players = len(pl) - config["player_list_max_players"]
            if len(pl) != 0:
                if len(pl) == 1:
                    player_list = config["player_list_prefix"]["single"]
                else:
                    player_list = config["player_list_prefix"]["multiple"]
                for player in pl:
                    player_list += f"{player.name}, "
                player_list = player_list.rstrip(", ")
                # if reminding_players != 0:
                #     player_list += f" (and {reminding_players} more)"
    elif pl == None:
        player_list = config["player_list_messages"]["empty"]
    else:
        player_list = config["player_list_messages"]["hidden"]

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
        description=helper.replace_format_values(config["format"], [
            ["{MOTD}", motd],
            ["{VERSION}", version],
            ["{PLAYER_COUNT}", player_count],
            ["{PLAYER_LIST}", player_list]
        ]),
        color=discord.Color.yellow()
    )

    embed.set_thumbnail(url=f"attachment://icon.jpg")

    await interaction.response.send_message(embed=embed, file=icon_image)