import discord
from discord import app_commands
import requests
import humanize
from datetime import datetime, timezone

from bot import bot
import helper

@bot.tree.command(name="tibia_character", description="Display information about character")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def tibia_character(interaction: discord.Interaction, character_name: str):
    helper.used_command("tibia_character")

    tibia_response = requests.get(f"https://api.tibiadata.com/v4/character/{character_name}").json()

    character = tibia_response["character"]["character"]

    premium_status = None
    if character['account_status'] == "Free Account":
        premium_status = "<:free_account:1525591898214105331>"
    elif character['account_status'] == "Premium Account":
        premium_status = "<:premium_account:1525591899367276695>"
    else:
        premium_status = "premium_status not assigned (error)"

    # Todo: fix this time mess
    last_login = f"{character['last_login'].split('T')[0].replace("-", ".")} {character['last_login'].split('T')[1].split('Z')[0]}" # 2026.07.04 20:05:28
    last_seen = humanize.naturaltime(datetime.now(timezone.utc) - datetime.fromisoformat(character['last_login'])) # 7 days ago
    discord_timestamp = f"<t:{int(datetime.fromisoformat(character['last_login'].replace('Z', '+00:00')).timestamp())}:T>" # <t:1783803613:R>
    footer = None
    if "other_characters" in tibia_response["character"]:
        for other_character in tibia_response["character"]["other_characters"]:
            if other_character["name"] == character["name"]:
                if other_character["status"] == "offline":
                    footer = f"🔴 Last seen {last_seen} at {last_login}"
                elif other_character["status"] == "online":
                    footer = f"🟢 Logged on {last_seen} at {last_login}"
    else:
        # Todo: use /v4/world/{name} request on the players' world and see online players to determine if player is offline or not
        if "day" in last_seen or "month" in last_seen or "year" in last_seen:
            footer = f"🔴 Last seen {last_seen} at {last_login} (Hidden)"
        else:
            footer = f"🟡 Logged on {last_seen} at {last_login} (Hidden)"

    vocations = {
        "None": "`🚫` None",
        "Knight": "`⚔️` Knight",
        "Elite Knight": "⚔️` Elite Knight",
        "Paladin": "`🏹` Paladin",
        "Royal Paladin": "`🏹` Royal Paladin",
        "Sorcerer": "`💫` Sorcerer",
        "Master Sorcerer": "`💫` Master Sorcerer",
        "Druid": "`🌿` Druid",
        "Elder Druid": "`🌿` Elder Druid",
    }

    vocation = vocations.get(character["vocation"], "vocation not assigned (error)")

    genders = {
        "male": "`♂️` Male",
        "female": "`♀️` Female",
    }

    gender = genders.get(character["sex"], "gender not assigned (error)")

    # Todo: Change the emote based on the world's region
    embed = discord.Embed(
        title=f"[{character['level']}] {premium_status} {character['name']}",
        description=f"{vocation}\n`🌍` {character['world']}\n{gender}\n`🛖` {character['residence']}\n",
        color=discord.Color.yellow()
    )

    embed.set_footer(text=footer)

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="tibia_boosted", description="See today's boosted creatures")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def tibia_boosted(interaction: discord.Interaction):
    helper.used_command("tibia_boosted")

    tibia_response = requests.get("https://api.tibiadata.com/v4/boostablebosses").json()

    boosted_boss = tibia_response["boostable_bosses"]["boosted"]

    embed = discord.Embed(
        title=f"{boosted_boss['name']}",
        color=discord.Color.yellow()
    )

    embed.set_image(url=boosted_boss["image_url"])
    print(boosted_boss["image_url"])

    await interaction.response.send_message(embed=embed)