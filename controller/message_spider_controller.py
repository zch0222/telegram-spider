from fastapi import APIRouter, Depends, Request, Response, BackgroundTasks
from fastapi.responses import StreamingResponse
from model import SubmitTaskDTO, ResData, SearchMessageTextDTO, DownloadMessageMediaDTO
from service.message_spider_service import MessageService
import asyncio
from constants import YOUTUBE_DL_DOWNLOAD_PROCESS_PREFIX
import time
import json
import aioredis
from core import get_redis

message_spider_router = APIRouter()


@message_spider_router.post("/submit")
async def process(submit_task_dto: SubmitTaskDTO, service: MessageService = Depends()):
    channel = submit_task_dto.channel
    min_id = submit_task_dto.min_id

    asyncio.create_task(service.process_messages(channel, min_id))

    return ResData.success("提交成功")


@message_spider_router.get("/task_process")
async def task_process(service: MessageService = Depends()):
    headers = {
        # 设置返回数据类型是SSE
        'Content-Type': 'text/event-stream',
        # 保证客户端的数据是新的
        'Cache-Control': 'no-cache',
    }
    return StreamingResponse(service.get_task_process(), headers=headers)


@message_spider_router.get("/message_media_download_process")
async def message_media_download_process(service: MessageService = Depends()):
    headers = {
        # 设置返回数据类型是SSE
        'Content-Type': 'text/event-stream',
        # 保证客户端的数据是新的
        'Cache-Control': 'no-cache',
    }
    return StreamingResponse(service.get_message_media_download_process(), headers=headers)


@message_spider_router.post("/search_message_text")
def search_message_text(search_message_text_dto: SearchMessageTextDTO, service: MessageService = Depends()):
    return ResData.success(service.search_messages_by_text(search_message_text_dto.messageText))


@message_spider_router.post("/download_message_media")
async def download_message_media(download_message_media_dto: DownloadMessageMediaDTO,
                                 service: MessageService = Depends()):
    asyncio.create_task(service.download_media_from_message(download_message_media_dto.message_link))
    return ResData.success("提交下载任务成功")


async def get_youtube_dl_download_process(redis: aioredis.Redis):
    while True:
        keys = await redis.keys(YOUTUBE_DL_DOWNLOAD_PROCESS_PREFIX + "*")
        youtube_dl_download_process_list = []
        for key in keys:
            youtube_dl_download_process = await redis.get(key)
            youtube_dl_download_process_list.append(youtube_dl_download_process)
        yield 'id: "{}"\nevent: "message"\ndata: {}\n\n'.format(int(time.time()),
                                                                json.dumps(
                                                                    [item.decode('utf-8') for item in
                                                                     youtube_dl_download_process_list]))
        await asyncio.sleep(1)


@message_spider_router.get("/youtube_dl/process")
async def youtube_dl_process(redis: aioredis.Redis = Depends(get_redis)):
    headers = {
        # 设置返回数据类型是SSE
        'Content-Type': 'text/event-stream',
        # 保证客户端的数据是新的
        'Cache-Control': 'no-cache',
    }
    return StreamingResponse(get_youtube_dl_download_process(redis), headers=headers)