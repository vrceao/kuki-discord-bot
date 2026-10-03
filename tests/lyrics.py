# Old code from vrceao/soundcloud-discord-lyrics

import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import time
import asyncio
import requests

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

bot = commands.Bot(command_prefix="!", self_bot=True)

# CUSTOMIZATION START

check_delay = 1 # How often should the script check your status. Note: this has nothing to do with updating your status, only checking
log_changes = True # Enable to show the status changes in the console

# Lyrics of the song, first value is the timestamp in seconds, second value is the lyric
lyrics = [
    [8, "I miss that kind of misery"],
    [9.6, "The kind where you are nice to me"],
    [11.7, "But only in the evening"],
    [13.4, "So I ask, am I just dreaming?"],
    [15.6, "I love you so much that it's dripping"],
    [18, "Dripping from my arms and such"],
    [19.8, "I'm sorry, I know I'm too much"],
    [22, "To love, to trust, I'm nothing, but"],
    [24, "I miss that kind of misery"],
    [26, "The kind where you are nice to me"],
    [27.9, "But only in the evening"],
    [29.5, "So I ask, am I just dreaming?"],
]

target_song = "misery. (best part)" # The song name (not artist)
lyric_format = "$LYRIC$ ♡.ᐟ⋆" # Format of your status, $LYRIC$ is the current line

# The emote displayed in the status
emote = {
    "name": "koishirocking",
    "id": 940427023845818388
}
# No emote
"""
emote = {
    "name": "",
    "id": None
}
"""
# Built-in emote
"""
emote = {
    "name": "❤️",
    "id": None
}
"""

# This status will be set when there's no lyric or the script ends
default_status = {
    "text": "Waiting for 𝐲𝐨𝐮 ♡.ᐟ⋆",
    "emote": {
        "name": "koishirocking",
        "id": 940427023845818388
    }
}

# CUSTOMIZATION END

current_time = 0
lyrics_displaying = False
current_lyric = None
default_status_displaying = False

async def update_status():
    global default_status_displaying

    if current_lyric == None:
        return
    
    default_status_displaying = False

    requests.patch("https://discord.com/api/v9/users/@me/settings", headers={
        "Authorization": DISCORD_TOKEN,
        "Content-Type": "application/json"
    }, json={
        "custom_status": {
            "text": lyric_format.replace("$LYRIC$", current_lyric),
            "emoji_name": emote["name"],
            "emoji_id": emote["id"]
        }
    })

    if log_changes:
        print(f"Updated status with: {lyric_format.replace("$LYRIC$", current_lyric)}")

def reset_status():
    global default_status_displaying

    default_status_displaying = True

    requests.patch("https://discord.com/api/v9/users/@me/settings", headers={
        "Authorization": DISCORD_TOKEN,
        "Content-Type": "application/json"
    }, json={
        "custom_status": {
            "text": default_status["text"],
            "emoji_name": default_status["emote"]["name"],
            "emoji_id": default_status["emote"]["id"]
        }
    })

async def display_lyrics():
    global current_time
    global current_lyric

    while True:
        if lyrics_displaying:
            new_lyric = None
            for i in range(len(lyrics) - 1):
                if current_time >= lyrics[-1][0]:
                    new_lyric = lyrics[-1][1]
                    break
                elif current_time >= lyrics[i][0] and current_time < lyrics[i + 1][0]:
                    new_lyric = lyrics[i][1]
                    break
            if new_lyric == None:
                if not default_status_displaying:
                    reset_status()
            if not new_lyric == current_lyric:
                current_lyric = new_lyric
                await update_status()
        else:
            print("off")
        await asyncio.sleep(.1)
        current_time += .1

async def check_activity():
    global current_time
    global lyrics_displaying

    for activity in bot.activities:
        if activity.name == "SoundCloud":
            if activity.details == target_song:
                current_time = time.time() - activity.timestamps.start.timestamp()
                if not lyrics_displaying:
                    lyrics_displaying = True
                return

    if not lyrics_displaying:
        return

    lyrics_displaying = False
    reset_status()

@bot.event
async def on_ready():
    asyncio.create_task(display_lyrics())

    while True:
        await check_activity()
        await asyncio.sleep(check_delay)

try:
    bot.run(DISCORD_TOKEN)
except KeyboardInterrupt:
    reset_status()