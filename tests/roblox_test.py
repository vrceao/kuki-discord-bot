import requests
import os
from dotenv import load_dotenv

load_dotenv()

cookies = {
    ".ROBLOSECURITY": os.getenv("ROBLOX_COOKIE")
}
response = requests.post("https://friends.roblox.com/v1/users/523178675/friends", cookies=cookies).json()

print(response)