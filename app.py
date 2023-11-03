from dotenv import load_dotenv
import os
from telethon import TelegramClient, utils
import asyncio
from telethon.tl.types import InputMessagesFilterPhotos, InputMessagesFilterDocument

load_dotenv()

API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")

client = TelegramClient('Jian', API_ID, API_HASH)
channel = "https://t.me/suzhilangZB"

async def main():
    messages = client.iter_messages(channel, limit=100)
    msges = ""
    async for message in messages:
        print(str(message.date))

if __name__ == '__main__':
    asyncio.run(main())
