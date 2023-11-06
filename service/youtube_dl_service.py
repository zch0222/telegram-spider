from core import get_logger, get_redis, YoutubeDL
import logging
from fastapi import Depends
import os
import youtube_dl
import pytz
import aioredis
from model import ResData, YoutubeDlProcessBO
from datetime import datetime
from uuid import uuid4
from constants import YOUTUBE_DL_DOWNLOAD_PROCESS_PREFIX
import time
import json
import asyncio


class YoutubeDlService:

    def __init__(self, redis: aioredis.Redis = Depends(get_redis), logger: logging.Logger = Depends(get_logger)):
        self.logger = logger
        self.redis = redis

    async def submit(self, url_list):
        asyncio.create_task(YoutubeDL().download(url_list, os.environ.get('YOUTUBE_DL_SAVE_PATH'), self.logger, self.redis))
        # shanghai_tz = pytz.timezone('Asia/Shanghai')
        # now = datetime.now(shanghai_tz)
        # redis_id = str(uuid4())
        # self.logger.info(f"{now.strftime('%Y-%m-%d %H:%M:%S')} -- youtube-dl: {str(redis_id)} start")
        # print(1)
        # print(url_list)
        # await self.redis.set(YOUTUBE_DL_DOWNLOAD_PROCESS_PREFIX + redis_id, YoutubeDlProcessBO(
        #     id=redis_id,
        #     url_list=url_list
        # ).to_json_str())
        # print(2)
        # try:
        #     ydl_opts = {
        #         'outtmpl': f"{os.environ.get('YOUTUBE_DL_SAVE_PATH')}/%(title)s.%(ext)s",
        #     }
        #
        #     with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        #         ydl.download(url_list)
        # except Exception as e:
        #     print(e)
        # finally:
        #     await self.redis.delete(YOUTUBE_DL_DOWNLOAD_PROCESS_PREFIX + redis_id)
        #     self.logger.info(f"{now.strftime('%Y-%m-%d %H:%M:%S')} -- youtube-dl: {str(redis_id)} finish")

    async def get_youtube_dl_download_process(self):
        while True:
            keys = await self.redis.keys(YOUTUBE_DL_DOWNLOAD_PROCESS_PREFIX + "*")
            youtube_dl_download_process_list = []
            for key in keys:
                youtube_dl_download_process = await self.redis.get(key)
                youtube_dl_download_process_list.append(youtube_dl_download_process)
            yield 'id: "{}"\nevent: "message"\ndata: {}\n\n'.format(int(time.time()),
                                                                    json.dumps(
                                                                        [item.decode('utf-8') for item in youtube_dl_download_process_list]))
            await asyncio.sleep(1)