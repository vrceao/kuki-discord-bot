import json
import time
import humanize
import shutil
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def env(name):
    return os.getenv(name)

def load_file(path):
    with open(path, "r", encoding="utf-8") as file:
        result = json.load(file)
    return result

preferences = load_file("preferences.json")

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

def log_command(command_name):
    if not os.path.exists(log_file):
        print("log file doesnt exist for some reason")

    log = load_file(log_file)

    log.append({
        "version": preferences["version"],
        "unix_timestamp": int(str(time.time()).split(".")[0]),
        "timestamp": current_timestamp(),
        "command": command_name
    })

    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=4)

def count_command(command_name):
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

def used_command(command_name):
    if preferences["log_commands"]:
        log_command(command_name)
        # [*] Calling youmu_stare
        print(f"{prefix()} Calling {colored(128, 255, 128, command_name)}")
    if preferences["count_commands"]:
        count_command(command_name)
        return

def format_filesize(size):
    return humanize.naturalsize(size)