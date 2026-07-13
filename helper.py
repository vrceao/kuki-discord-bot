import json
import time
import humanize
import os
from datetime import datetime, timezone

with open("preferences.json", "r", encoding="utf-8") as file:
    preferences = json.load(file)

def colored(r, g, b, text, bold=False):
    style = "1;" if bold else ""
    return f"\033[{style}38;2;{r};{g};{b}m{text}\033[0m"

def current_timestamp():
    formatted = str(datetime.now()).split(".")[0]
    date = formatted.split(" ")[0]
    time = formatted.split(" ")[1]
    date = f"{date.split('-')[2]}.{date.split('-')[1]}.{date.split('-')[0]}"
    return date + " " + time

def prefix():
    return colored(128, 128, 128, current_timestamp(), True)

log_file = None

def init_logs():
    global log_file

    path = f"logs/{current_timestamp().replace(" ", "-").replace(":", "-")}.json"

    if not os.path.exists("logs"):
        os.mkdir("logs")

    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write("[]")

    log_file = path

def log_command(command_name):
    if not os.path.exists(log_file):
        print("log file doesnt exist for some reason")

    with open(log_file, "r", encoding="utf-8") as f:
        log = json.load(f)

    log.append({
        "version": preferences["version"],
        "unix": int(str(time.time()).split(".")[0]),
        "time": current_timestamp(),
        "command": command_name
    })

    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=4)

def count_command(command_name):
    path = "data/counts.json"

    if not os.path.exists("data"):
        os.mkdir("data")

    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write("{}")

    with open(path, "r", encoding="utf-8") as f:
        counts = json.load(f)

    if command_name in counts:
        counts[command_name] += 1
    else:
        counts[command_name] = 1

    with open(path, "w", encoding="utf-8") as f:
        json.dump(counts, f, indent=4)

def used_command(command_name):
    if preferences["log_commands"]:
        log_command(command_name)
        print(f"{prefix()} Calling {colored(128, 255, 128, command_name)}")
    if preferences["count_commands"]:
        count_command(command_name)
        return

def format_filesize(size):
    return humanize.naturalsize(size)