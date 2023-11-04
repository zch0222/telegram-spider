from telethon import TelegramClient, utils
import os


def get_telegram_client():
    return TelegramClient('Jian', os.environ.get("API_ID"), os.environ.get("API_HASH"))
