import discord
from discord import app_commands
import os
import re

from bot import bot
import helper

preferences = helper.load_file("preferences.jsonc")

# Move all this config to preferences.json
blacklisted_extensions = [
    "env",
    "kdbx",
    "db"
]

filtered_entries = [
    "$Recycle.Bin",
    "$SysReset",
    "$WINDOWS.~BT",
    "$Windows.~WS",
    ".GamingRoot",
    "DumpStack.log",
    "bootTel.dat",
    "Documents and Settings",
    "DumpStack.log.tmp",
    "hiberfil.sys",
    "pagefile.sys",
    "Recovery",
    "swapfile.sys",
    "System Volume Information",
    "__pycache__"
]

possible_syntax_highlights = [
    "py", "js", "ts",
    "java", "c", "cpp",
    "cs", "css", "html",
    "xml", "json", "yml",
    "sql", "sh", "php",
    "rb", "go", "rs",
    "lua", "md", "ini"
]

image_extensions = [
    "png", "jpg", "jpeg", "gif"
]



# Todo: Make "D:" and other drive letters work as a path because now it displays the current directory lol
@bot.tree.command(name="read_directory", description="Display contents of a directory on host's computer")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def read_dir(interaction: discord.Interaction, dir: str, entries_limit: int = 20, display_filtered: bool = False):
    if not await helper.check_permissions(interaction): return
    helper.used_command(interaction)
    config = helper.get_command_config(interaction)

    if re.fullmatch(r"[C-Z]", dir):
        dir += ":"

    dir = dir.replace("/", "\\")
    if not dir.endswith("\\"):
        dir += "\\"

    # Error catching
    if not os.path.isdir(dir):
        description = config["messages"]["not_a_directory"]
        if not os.path.exists(dir):
            description = config["messages"]["doesnt_exist"]

        embed = discord.Embed(
            title=helper.replace_format_values(config["title"], [
                ["{DIRECTORY}", f"`{dir}`"]
            ]),
            description=description,
            color=discord.Color.yellow()
        )

        await interaction.response.send_message(embed=embed)
        return

    directory_contents = os.listdir(dir)

    # Todo: fix order because for some reason "/read_directory dir:D:/ entries_limit:2" breaks very badly (not common tho)
    # Yes, I vibecoded this for loop but it still doesn't work properly
    file_list = ""
    filtered_folders = 0
    filtered_files = 0
    displayed = 0
    for entry in directory_contents:
        full_path = os.path.join(dir, entry)
        if not display_filtered and entry in filtered_entries:
            if os.path.isdir(full_path):
                filtered_folders += 1
            else:
                filtered_files += 1
            continue
        if displayed >= entries_limit:
            remaining = len(directory_contents) - filtered_folders - filtered_files - displayed
            if remaining == 1:
                status = config["messages"]["truncated"]["single"]
            else:
                status = helper.replace_format_values(config["messages"]["truncated"]["single"], [
                    ["{RESULTS}", remaining]
                ])
            break

        if os.path.isdir(full_path):
            icon = f"`{config['icons']['folder']}`"
        elif len(entry.split(".")) == 1:
            icon = f"`{config['icons']['file']}`"
        else:
            extension = entry.split(".")[len(entry.split(".")) - 1]
            icon = config["icons"]["file"]
            for type in config["extension_types"]:
                if extension in config["extension_types"][type]:
                    icon = config["icons"][type]
                    break
        file_list += helper.replace_format_values(config["file_list_entry_format"], [
            ["{ICON}", icon],
            ["{NAME}", entry]
        ])
        file_list += "\n"
        displayed += 1
    else:
        status = config["messages"]["all_displayed"]
    file_list = file_list.rstrip("\n")

    # Add filtered string
    filtered_total = filtered_folders + filtered_files
    filtered = ""
    if filtered_total != 0:
        if filtered_total == 1:
            filtered = helper.replace_format_values(config["messages"]["filtered"]["single"], [
                ["{FILTERED}", filtered_total]
            ])
        else:
            filtered = helper.replace_format_values(config["messages"]["filtered"]["multiple"], [
                ["{FILTERED}", filtered_total]
            ])

    # Separate files and folders
    folders = 0
    files = 0
    for i in range(len(directory_contents)):
        if os.path.isdir(os.path.join(dir, directory_contents[i])):
            folders += 1
        else:
            files += 1

    embed = discord.Embed(
        title=helper.replace_format_values(config["title"], [
            ["{DIRECTORY}", f"`{dir}`"]
        ]),
        description=helper.replace_format_values(config["format"], [
            ["{FILE_LIST}", file_list],
            ["{STATUS}", status],
            ["{FILTERED}", filtered]
        ]),
        color=discord.Color.yellow()
    )

    embed.set_footer(text=f"📁 Folders: {folders - filtered_folders} (Total: {folders}) • 📄 Files: {files - filtered_files} (Total: {files})")

    await interaction.response.send_message(embed=embed)



# Todo: When reading a file add ability to change starting character so that you can read the file in multiple requests even if its big
# Todo: Also add ability to read from the end rather than from start
@bot.tree.command(name="read_file", description="Display contents of a file on host's computer")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def read_file(interaction: discord.Interaction, path: str, character_limit: int = 1000):
    if not await helper.check_permissions(interaction): return
    helper.used_command(interaction)

    # Error catching
    if os.path.isdir(path) or not os.path.exists(path):
        if os.path.isdir(path):
            description = "`⚠️` This is a directory not a file"
        else:
            description = "`⚠️` File doesn't exist"

        embed = discord.Embed(
            title=f"File: \"{path}\"",
            description=description,
            color=discord.Color.yellow()
        )

        await interaction.response.send_message(embed=embed)
        return

    file_extension = path.split(".")[len(path.split(".")) - 1]

    # Blocking blacklisted extensions
    if file_extension in blacklisted_extensions:
        description = "`⚠️` This file extension is blacklisted for reading"

        embed = discord.Embed(
            title=f"File: \"{path}\"",
            description=description,
            color=discord.Color.yellow()
        )

        await interaction.response.send_message(embed=embed)
        return

    # Images
    if file_extension in image_extensions:
        embed = discord.Embed(
            title=f"File: \"{path}\"",
            description="",
            color=discord.Color.yellow()
        )

        if len(path.split("/")) == 1:
            fileName = path.split(".")[0]
        else:
            fileName = path.split("/")[-1].split(".")[0]
        imageFile = discord.File(path, filename=f"{fileName}.{file_extension}")
        embed.set_image(url=f"attachment://{fileName}.{file_extension}")

        await interaction.response.send_message(embed=embed, file=imageFile)
        return

    # Reading
    with open(path, "r", encoding="utf-8") as f:
        full_file_content = f.read()

    # Codeblock
    codeblock_language = ""
    for i in range(len(possible_syntax_highlights)):
        if file_extension == possible_syntax_highlights[i]:
            codeblock_language = possible_syntax_highlights[i]
            break;

    # Todo: Display amount of lines as well
    # Todo: Make 0 or "inf" work as ignoring the limit
    file_content = full_file_content[:character_limit]
    file_content_codeblock = f"```{codeblock_language}\n{file_content}```"
    characters_truncated = len(full_file_content) - character_limit
    if characters_truncated == 1:
        info = f"`⚠️` Truncated {characters_truncated} character"
    elif characters_truncated > 1:
        info = f"`⚠️` Truncated {characters_truncated} characters"
    else:
        info = "`✅` All characters displayed"

    embed = discord.Embed(
        title=f"File: \"{path}\"",
        description=f"{file_content_codeblock}\n{info}",
        color=discord.Color.yellow()
    )

    file_size = os.stat(path).st_size

    percentage_displayed = len(file_content) / len(full_file_content) * 100
    embed.set_footer(text=f"📜 Characters: {len(full_file_content)} (Displaying {len(file_content)} which is {percentage_displayed:.2f}%) • 💾 Size: {helper.format_filesize(file_size)}")

    await interaction.response.send_message(embed=embed)



@bot.tree.command(name="read_screen", description="Send an image of host's computer screen")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.choices(monitor=[
    app_commands.Choice(name="Primary", value="primary"),
    app_commands.Choice(name="Second", value="second"),
    app_commands.Choice(name="All", value="all")
])
async def read_file(interaction: discord.Interaction, monitor: app_commands.Choice[str]):
    if not await helper.check_permissions(interaction): return
    helper.used_command(interaction)

    os.makedirs("data/screenshots", exist_ok=True)

    # Todo: Put the monitor config to preferences.json somehow
    if monitor.value == "primary":
        x = 0
        y = 0
        width = 1920
        height = 1080
    elif monitor.value == "second":
        x = -1920
        y = 0
        width = 1920
        height = 1080
    elif monitor.value == "all":
        x = -1920
        y = 0
        width = 3840
        height = 1080

    fileName = f"{helper.current_timestamp().replace(" ", "-").replace(":", "-")}.png"
    path = f"data/screenshots/{fileName}"
    if not os.path.exists(path):
        from PIL import ImageGrab

        screenshot = ImageGrab.grab(
            bbox=(x, y, x + width, y + height),
            all_screens=True
        )

        screenshot.save(path)

    imageFile = discord.File(path, filename=f"{fileName}.png")

    await interaction.response.send_message(file=imageFile)