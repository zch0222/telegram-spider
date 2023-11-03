from dotenv import load_dotenv
import os
from telethon import TelegramClient, utils
import json
import asyncio
from telethon.tl.types import InputMessagesFilterPhotos, InputMessagesFilterDocument

load_dotenv()

API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")
CHANNEL = os.environ.get("CHANNEL")

print(API_ID)

client = TelegramClient('Jian', API_ID, API_HASH)

async def main():
    me = await client.get_me()
    print(me.username)

    msges = []

    messages = client.iter_messages(CHANNEL, limit=100)
    async for message in messages:
        print(str(message.date))
        msges.append({
            "id": message.id,
            "date": str(message.date),
            "text": message.text,
            "link": f"https://t.me/c/{message.to_id.channel_id}/{message.id}"  # 构建链接
        })
    with open(f"{CHANNEL}.json", 'w', encoding='utf-8') as f:
        json.dump(msges, f, ensure_ascii=False, indent=4)

with client:
    client.loop.run_until_complete(main())

