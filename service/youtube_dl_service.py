from core import get_logger
import logging
from fastapi import Depends
import os
import youtube_dl
import pytz
from model import ResData
from datetime import datetime


class YoutubeDlService:

    def __init__(self, logger: logging.Logger = Depends(get_logger)):
        self.logger = logger

    def submit(self, url):
        shanghai_tz = pytz.timezone('Asia/Shanghai')
        now = datetime.now(shanghai_tz)
        self.logger.info(f"{now.strftime('%Y-%m-%d %H:%M:%S')} -- youtube-dl: {url}")
        ydl_opts = {
            'outtmpl': f"'{os.environ.get('YOUTUBE_DL_SAVE_PATH')}/%(title)s.%(ext)s'",
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return ResData.success("下载成功")
