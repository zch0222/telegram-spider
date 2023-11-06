from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from model import YoutubeDlSubmitDTO, ResData
from service.youtube_dl_service import YoutubeDlService
import asyncio

youtube_dl_router = APIRouter()


@youtube_dl_router.post("/youtube_dl/submit")
async def youtube_dl_submit(youtube_dl_submit_dto: YoutubeDlSubmitDTO, service: YoutubeDlService = Depends()):
    # asyncio.create_task(service.submit(youtube_dl_submit_dto.url_list))
    await service.submit(youtube_dl_submit_dto.url_list)
    return ResData.success("提交成功")


@youtube_dl_router.get("/youtube_dl/process")
async def youtube_dl_process(service: YoutubeDlService = Depends()):
    headers = {
        # 设置返回数据类型是SSE
        'Content-Type': 'text/event-stream',
        # 保证客户端的数据是新的
        'Cache-Control': 'no-cache',
    }
    return StreamingResponse(service.get_youtube_dl_download_process(), headers=headers)
