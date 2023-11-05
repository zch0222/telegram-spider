from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware
import logging
from logging.handlers import RotatingFileHandler
import subprocess
from model import ResData

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


@app.post("restart")
def restart():
    command = "pkill -f 'uvicorn' && nohup uvicorn main:app --host 0.0.0.0 --port 8000 &"
    process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    output, error = process.communicate()

    if error:
        return ResData.error("重启失败")
    else:
        return ResData.success("重启成功")


@app.get("status")
def status():
    return ResData.success("正在运行")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app="app:app", host="0.0.0.0", port=8000, workers=4)
