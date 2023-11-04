import json

from dao.message_dao import MessageDAO
from core import get_redis
from fastapi import Depends
from telethon import TelegramClient, utils
from datetime import datetime
import time
import os
import aioredis
import asyncio
from uuid import uuid4
from model import TaskBO
from constants import TASK_PROCESS_PREFIX


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
                                                                    json.dumps([item.decode('utf-8') for item in task_list]))
            await asyncio.sleep(1)

    def search_messages_by_text(self, text):
        return self.dao.search_messages_by_text(text)
