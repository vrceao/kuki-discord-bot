import json
import json5
import time
import humanize
import shutil
import os
import discord
from discord import app_commands
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def env(name):
    return os.getenv(name)

def load_file(path):
    with open(path, "r", encoding="utf-8") as file:
        if path.split(".")[-1] == "jsonc":
            result = json5.load(file)
        else:
            result = json.load(file)
    return result

preferences = load_file("preferences.jsonc")

def colored(r, g, b, text, bold=False):
    style = "1;" if bold else ""
    return f"\033[{style}38;2;{r};{g};{b}m{text}\033[0m"

def current_timestamp():
    formatted = str(datetime.now()).split(".")[0]
    date = formatted.split(" ")[0]
    time = formatted.split(" ")[1]
    return date + " " + time

def prefix():
    return colored(128, 128, 128, current_timestamp(), True)

log_file = None

def init_temp():
    shutil.rmtree("temp", ignore_errors=True)
    os.makedirs("temp", exist_ok=True)

def init_logs():
    global log_file

    path = f"logs/{current_timestamp().replace(" ", "-").replace(":", "-")}.json"

    os.makedirs("logs", exist_ok=True)

    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write("[]")

    log_file = path

def log_command(interaction, success: bool = True):
    if not preferences["log_commands"]:
        return

    for command in preferences["commands"]:
        if command["name"] == interaction.command.name:
            if not command["log_command"]:
                return
            break

    if not os.path.exists(log_file):
        print("log file doesnt exist for some reason")
        return

    log = load_file(log_file)

    arguments = {
        key: str(value)
        for key, value in vars(interaction.namespace).items()
    }

    log.append({
        "json_format_version": preferences["json_format_version"],
        "version": preferences["version"],
        "unix_timestamp": int(str(time.time()).split(".")[0]),
        "timestamp": current_timestamp(),
        "command": interaction.command.name,
        "success": success,
        "user": interaction.user.name,
        "channel": interaction.channel.id,
        "arguments": arguments
    })

    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=4)

def count_command(command_name):
    if not preferences["count_commands"]:
        return

    for command in preferences["commands"]:
        if command["name"] == command_name:
            if not command["count_command"]:
                return
            break

    path = "data/counts.json"

    os.makedirs("data", exist_ok=True)

    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write("{}")

    counts = load_file(path)

    if command_name in counts:
        counts[command_name] += 1
    else:
        counts[command_name] = 1

    with open(path, "w", encoding="utf-8") as f:
        json.dump(counts, f, indent=4)

def print_command(interaction, success: bool = True):
    if not preferences["print_commands"]:
        return

    for command in preferences["commands"]:
        if command["name"] == interaction.command.name:
            if not command["print_command"]:
                return
            break

    if success:
        print(f"{prefix()} @{colored(128, 255, 128, interaction.user.name)} called /{colored(128, 255, 128, interaction.command.name)} in #{colored(128, 255, 128, interaction.channel.id)} successfully")
    else:
        print(f"{prefix()} @{colored(128, 255, 128, interaction.user.name)} tried calling /{colored(128, 255, 128, interaction.command.name)} in #{colored(128, 255, 128, interaction.channel.id)} but didn't have permission")

def used_command(interaction):
        # [*] Calling youmu_stare
        log_command(interaction)
        print_command(interaction)
        count_command(interaction.command.name)

async def check_permissions(interaction):
    if not preferences["permission"]["check"]: return True

    for command in preferences["commands"]:
        if command["name"] == interaction.command.name:
            if interaction.user.id in command["allowed_users"] or "*" in command["allowed_users"]:
                return True

    config = preferences["permission"]["config"]

    command = replace_format_values(config["command_format"], [["{COMMAND}", interaction.command.name]])
    uid = replace_format_values(config["uid_format"], [["{UID}", interaction.user.id]])

    if preferences["permission"]["log_command"]:
        log_command(interaction, False)
    if preferences["permission"]["print_command"]:
        print_command(interaction, False)

    embed = discord.Embed(
        title=config["title"],
        description=replace_format_values(config["format"], [
            ["{COMMAND}", command],
            ["{UID}", uid],
            ["{MESSAGE}", config["message_format"]],
            ["{REPO}", config["repo_format"]]
        ]),
        color=discord.Color.yellow()
    )

    await interaction.response.send_message(embed=embed)

    return False

def format_filesize(size):
    return humanize.naturalsize(size)

def get_command_info(interaction):
    target = None

    if isinstance(interaction, str):
        target = interaction
    else:
        target = interaction.command.name
    
    for command in preferences["commands"]:
        if command["name"] == target:
            return command

    return None

def replace_format_values(original, replacements):
    modified = str(original)
    for replacement in replacements:
        modified = modified.replace(str(replacement[0]), str(replacement[1]))
    return modified