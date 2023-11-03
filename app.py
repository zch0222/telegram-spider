from dotenv import load_dotenv
import os
from telethon import TelegramClient, utils
import asyncio
from telethon.tl.types import InputMessagesFilterPhotos, InputMessagesFilterDocument

load_dotenv()

API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")

print(API_ID)

client = TelegramClient('Jian', API_ID, API_HASH)
channel = "https://t.me/suzhilangZB"

async def main():
    me = await client.get_me()
    print(me.username)

    messages = client.iter_messages(channel, limit=100)
    msges = ""
    async for message in messages:
        print(str(message.date))

with client:
    client.loop.run_until_complete(main())

