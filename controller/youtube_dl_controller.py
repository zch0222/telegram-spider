from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from model import YoutubeDlSubmitDTO, ResData
from service.youtube_dl_service import YoutubeDlService
import asyncio
from constants import YOUTUBE_DL_DOWNLOAD_PROCESS_PREFIX
import time
import json
import aioredis
from core import get_redis

youtube_dl_router = APIRouter()


@youtube_dl_router.post("/youtube_dl/submit")
async def youtube_dl_submit(youtube_dl_submit_dto: YoutubeDlSubmitDTO, service: YoutubeDlService = Depends()):
    # asyncio.create_task(service.submit(youtube_dl_submit_dto.url_list))
    await service.submit(youtube_dl_submit_dto.url_list)
    return ResData.success("提交成功")


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


@youtube_dl_router.get("/youtube_dl/process")
async def youtube_dl_process(redis: aioredis.Redis = Depends(get_redis)):
    headers = {
        # 设置返回数据类型是SSE
        'Content-Type': 'text/event-stream',
        # 保证客户端的数据是新的
        'Cache-Control': 'no-cache',
    }
    return StreamingResponse(get_youtube_dl_download_process(redis), headers=headers)
