from dao.message_dao import MessageDAO
from fastapi import Depends
from telethon import TelegramClient, utils
import os


class MessageService:
    def __init__(self, dao: MessageDAO = Depends()):
        self.dao = dao

    async def process_messages(self, channel, min_id):
        client = TelegramClient('Jian', os.environ.get("API_ID"), os.environ.get("API_HASH"))
        await client.start()
        messages = client.iter_messages(channel, min_id=min_id)
        async for message in messages:
            msg = {
                "id": message.id,
                "date": str(message.date),
                "text": message.text,
                "link": f"https://t.me/c/{message.to_id.channel_id}/{message.id}"  # 构建链接
            }
            print(msg)
            if self.dao.get_message_by_link(msg["link"]) is None:
                self.dao.insert_message(msg)
        await client.disconnect()
