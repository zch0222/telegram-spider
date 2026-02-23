import os
from dotenv import load_dotenv

load_dotenv()

TELETHON_API_ID = os.environ.get("API_ID")
TELETHON_API_HASH = os.environ.get("API_HASH")
TELETHON_SESSION_NAME = 'Jian'
CHECK_INTERVAL = int(os.environ.get("CHECK_INTERVAL", 120))
MEDIA_DOWNLOAD_SAVE_PATH = os.environ.get("MEDIA_DOWNLOAD_SAVE_PATH", "downloads")

# CORS Configuration
env_origins = os.environ.get("CORS_ORIGINS", "")
if env_origins:
    CORS_ORIGINS = [origin.strip() for origin in env_origins.split(",") if origin.strip()]
else:
    CORS_ORIGINS = [
        "http://localhost:3000",
        "http://154.7.179.45:8081",
        "https://telegram.yxlm.cloud"
    ]
