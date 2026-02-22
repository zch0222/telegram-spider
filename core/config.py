import os
from dotenv import load_dotenv

load_dotenv()

TELETHON_API_ID = os.environ.get("API_ID")
TELETHON_API_HASH = os.environ.get("API_HASH")
TELETHON_SESSION_NAME = 'Jian'