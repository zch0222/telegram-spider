import youtube_dl
import pytz
from datetime import datetime
from uuid import uuid4
from constants import YOUTUBE_DL_DOWNLOAD_PROCESS_PREFIX
from model import YoutubeDlProcessBO
import aioredis
from fastapi import Depends
from core import get_redis, get_logger
import logging


class YoutubeDL:

    def __init__(self, redis: aioredis.Redis = Depends(get_redis), logger: logging.Logger = Depends(get_logger)):
        self.logger = logger
        self.redis = redis

    async def download(self, url_list, save_path):
        print(1)
        shanghai_tz = pytz.timezone('Asia/Shanghai')
        now = datetime.now(shanghai_tz)
        redis_id = str(uuid4())
        print(redis_id)
        self.logger.info(f"{now.strftime('%Y-%m-%d %H:%M:%S')} -- youtube-dl: {str(redis_id)} start")
        print(2)
        print(url_list)
        await self.redis.set(YOUTUBE_DL_DOWNLOAD_PROCESS_PREFIX + redis_id, YoutubeDlProcessBO(
            id=redis_id,
            url_list=url_list
        ).to_json_str())
        print(2)
        try:
            ydl_opts = {
                'outtmpl': f"{save_path}/%(title)s.%(ext)s",
            }

            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download(url_list)
        except Exception as e:
            print(e)
        finally:
            await self.redis.delete(YOUTUBE_DL_DOWNLOAD_PROCESS_PREFIX + redis_id)
            self.logger.info(f"{now.strftime('%Y-%m-%d %H:%M:%S')} -- youtube-dl: {str(redis_id)} finish")
