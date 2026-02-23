import json
import logging

from dao.message_dao import MessageDAO
from core import get_redis, get_logger
from fastapi import Depends
from telethon import TelegramClient, utils, types
from datetime import datetime
import pytz
import time
import os
import re
import aioredis
import asyncio
from uuid import uuid4
from model import TaskBO
from constants import TASK_PROCESS_PREFIX, MESSAGE_MEDIA_DOWNLOAD_PROCESS_PREFIX
from core.telegram_client import telegram_manager
from core.config import MEDIA_DOWNLOAD_SAVE_PATH


class MessageService:
    def __init__(self, dao: MessageDAO = Depends(), redis: aioredis.Redis = Depends(get_redis),
                 logger: logging.Logger = Depends(get_logger)):
        self.dao = dao
        self.redis = redis
        self.logger = logger

    async def save_message(self, message, channel, redis_id, min_id, max_id):
        sender = await message.get_sender()  # 获取发送者
        sender_username = ""
        sender_id = 0
        channel_name = message.chat.title  # 频道名称
        if sender is not None:
            sender_username = sender.username  # 发送者用户名
            sender_id = sender.id  # 发送者id
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
            name=channel_name,
            createTime=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            channel=channel,
            currentMessageId=message.id,
            minMessageId=min_id,
            percent=(max_id - message.id + 1) / (max_id - min_id + 1) * 100
        ).to_json_str())
        print(msg)
        if self.dao.get_message_by_link(msg["link"]) is None:
            self.dao.insert_message(msg)

    async def process_messages(self, channel, min_id):
        client = telegram_manager.client
        # await client.start() # managed by lifespan
        redis_id = str(uuid4())
        print(redis_id)
        try:
            messages = client.iter_messages(channel, min_id=min_id - 1)
            max_id = -1
            channel_name = ""
            async for message in messages:
                if "" == channel_name:
                    channel_name = message.chat.title
                if -1 == max_id:
                    max_id = message.id
                await self.save_message(message, channel, redis_id, min_id, max_id)
        except Exception as e:
            print(e)
        finally:
            shanghai_tz = pytz.timezone('Asia/Shanghai')
            now = datetime.now(shanghai_tz)
            await self.redis.set(TASK_PROCESS_PREFIX + redis_id, TaskBO(
                name=channel_name,
                createTime=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                channel=channel,
                currentMessageId=message.id,
                minMessageId=min_id,
                percent=100
            ).to_json_str())
            # await self.redis.delete(TASK_PROCESS_PREFIX + redis_id)
            # await client.disconnect() # managed by lifespan
            self.logger.info(f"{now.strftime('%Y-%m-%d %H:%M:%S')} -- spider: {channel} min_id: {min_id} Finish")

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

    def search_messages_by_text(self, text, channel=None, page=1, page_size=20):
        return self.dao.search_messages_by_text(text, channel, page, page_size)

    async def get_message_media_download_process(self):
        while True:
            keys = await self.redis.keys(MESSAGE_MEDIA_DOWNLOAD_PROCESS_PREFIX + "*")
            task_list = []
            for key in keys:
                task = await self.redis.get(key)
                task_list.append(task)
            yield 'id: "{}"\nevent: "message"\ndata: {}\n\n'.format(int(time.time()),
                                                                    json.dumps(
                                                                        [item.decode('utf-8') for item in task_list]))
            await asyncio.sleep(1)

    async def download_media_from_message(self, message_link: str):
        print(message_link)
        redis_key = MESSAGE_MEDIA_DOWNLOAD_PROCESS_PREFIX + message_link
        check_redis_data = await self.redis.get(redis_key)
        if check_redis_data:
            print(f"link is downloading {message_link}")
            return
        
        telegram_client = telegram_manager.client
        # await telegram_client.start() # managed by lifespan
        try:
            pattern = r'(.*?)/(\d+)$'
            match = re.search(pattern, message_link)
            link = match.group(1)
            message_id = match.group(2)
            print(link)
            print(message_id)
            print(int(message_id))
            messages = telegram_client.iter_messages(link, min_id=int(message_id) - 1, max_id=int(message_id) + 1)
            async for message in messages:
                print(message.media)
                if message.media:
                    path = MEDIA_DOWNLOAD_SAVE_PATH
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
                    await self.redis.set(MESSAGE_MEDIA_DOWNLOAD_PROCESS_PREFIX + message_link, message_link)
                    await message.download_media(subdir)
                    await self.redis.delete(MESSAGE_MEDIA_DOWNLOAD_PROCESS_PREFIX + message_link)
        finally:
            pass # await telegram_client.disconnect() # managed by lifespan
