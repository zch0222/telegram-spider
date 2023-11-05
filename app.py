from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware
import logging
from logging.handlers import RotatingFileHandler
from fastapi.responses import StreamingResponse
import subprocess
from model import ResData
import time
import json
import asyncio

from controller import message_spider_router
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

formatter = logging.Formatter('%(levelname)s - %(message)s')
file_handler = RotatingFileHandler(filename="app.log", maxBytes=1000000, backupCount=10)
file_handler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)

origins = [
    "http://localhost:3000",
    "http://154.7.179.45:8081",
    "https://telegram.yxlm.cloud"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(message_spider_router)


@app.post("/restart")
def restart():
    command = "pkill -f 'uvicorn' && nohup uvicorn main:app --host 0.0.0.0 --port 8000 &"
    process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    output, error = process.communicate()

    if error:
        return ResData.error("重启失败")
    else:
        return ResData.success("重启成功")


async def get_status():
    while True:
        yield 'id: "{}"\nevent: "message"\ndata: {}\n\n'.format(int(time.time()),
                                                                json.dumps(ResData.success("RUNNING")))

        await asyncio.sleep(2)


@app.get("/status")
def status():
    headers = {
        # 设置返回数据类型是SSE
        'Content-Type': 'text/event-stream',
        # 保证客户端的数据是新的
        'Cache-Control': 'no-cache',
    }
    return StreamingResponse(get_status(), headers=headers)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app="app:app", host="0.0.0.0", port=8000, workers=4)
