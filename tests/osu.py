import os
from dotenv import load_dotenv

load_dotenv()

OSU_SESSION = os.getenv("OSU_SESSION")

print(len(OSU_SESSION))