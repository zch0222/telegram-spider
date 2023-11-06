from core import get_redis, get_logger
from fastapi import Depends
import logging
import subprocess
import os
import re


class YouGetService:

    def __init__(self, logger: logging.Logger = Depends(get_logger)):
        self.logger = logger

    def submit(self, url: str):
        process = subprocess.Popen(["you-get", url], stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT, cwd=os.environ.get("YOU_GET_DOWNLOAD_SAVE_PATH"))
        while True:
            output = process.stdout.readline().decode()
            print(output)
            if output == '' and process.poll() is not None:
                break
            if output:
                match = re.search(r'(\d+)%', output)
                if match:
                    progress = match.group(1)
                    print(f"下载进度: {progress}%")