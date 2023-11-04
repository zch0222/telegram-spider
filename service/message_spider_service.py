import json

from dao.message_dao import MessageDAO
from core import get_redis
from fastapi import Depends
from telethon import TelegramClient, utils, types
from datetime import datetime
import time
import os
import aioredis
import asyncio
from uuid import uuid4
from model import TaskBO
from constants import TASK_PROCESS_PREFIX
from core import get_telegram_client


class MessageService:
    def __init__(self, dao: MessageDAO = Depends(), redis: aioredis.Redis = Depends(get_redis)):
        self.dao = dao
        self.redis = redis

    async def process_messages(self, channel, min_id):
        client = TelegramClient('Jian', os.environ.get("API_ID"), os.environ.get("API_HASH"))
        await client.start()
        redis_id = str(uuid4())
        await self.redis.set(TASK_PROCESS_PREFIX + redis_id, TaskBO(
            createTime=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            channel=channel,
            currentMessageId=0,
            minMessageId=min_id
        ).to_json_str())
        messages = client.iter_messages(channel, min_id=min_id)
        async for message in messages:
            sender = await message.get_sender()  # 获取发送者
            sender_username = sender.username  # 发送者用户名
            sender_id = sender.id  # 发送者id
            channel_name = message.chat.title  # 频道名称
            msg = {
                "channel": channel,
                "channel_name": channel_name,  # 添加频道名称
                "id": message.id,
                "date": str(message.date),
                "text": message.text,
                "sender_username": sender_username,  # 添加发送者用户名
                "sender_id": sender_id,  # 添加发送者id
                "link": f"https://t.me/c/{message.to_id.channel_id}/{message.id}"  # 构建链接
            }
            await self.redis.set(TASK_PROCESS_PREFIX + redis_id, TaskBO(
                createTime=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                channel=channel,
                currentMessageId=0,
                minMessageId=min_id
            ).to_json_str())
            print(msg)
            if self.dao.get_message_by_link(msg["link"]) is None:
                self.dao.insert_message(msg)
        await client.disconnect()
        await self.redis.delete(TASK_PROCESS_PREFIX + redis_id)

    async def get_task_process(self):
        while True:
            keys = await self.redis.keys(TASK_PROCESS_PREFIX + "*")
            task_list = []
            for key in keys:
                task = await self.redis.get(key)
                task_list.append(task)
            print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            yield 'id: "{}"\nevent: "message"\ndata: {}\n\n'.format(int(time.time()),
                                                                    json.dumps(
                                                                        [item.decode('utf-8') for item in task_list]))
            await asyncio.sleep(1)

    def search_messages_by_text(self, text):
        return self.dao.search_messages_by_text(text)

    async def download_media_from_message(self, message_link: str, telegram_client: TelegramClient = Depends(get_telegram_client)):
        await telegram_client.start()
        message = await telegram_client.get_messages(message_link)
        if message.media:

            path = os.environ.get("MEDIA_DOWNLOAD_SAVE_PATH")
            print(path)

            # 检查 to_id 的类型并获取相应的 ID
            if isinstance(message.to_id, types.PeerUser):
                print(f"User ID: {message.to_id.user_id}")
                path = path + f"/user/{message.to_id.user_id}"
            elif isinstance(message.to_id, types.PeerChat):
                print(f"Group ID: {message.to_id.chat_id}")
                path = path + f"/group/{message.to_id.chat_id}"
            elif isinstance(message.to_id, types.PeerChannel):
                print(f"Channel ID: {message.to_id.channel_id}")
                path = path + f"/channel/{message.to_id.channel_id}"

            print(path)

            subdir = os.path.join(path, str(message.id))
            os.makedirs(subdir, exist_ok=True)
            # 下载媒体文件到子目录
            await message.download_media(subdir)


