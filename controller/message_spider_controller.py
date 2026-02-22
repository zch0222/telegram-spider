from fastapi import APIRouter, Depends, Request, Response, BackgroundTasks
from fastapi.responses import StreamingResponse
from model import SubmitTaskDTO, ResData, SearchMessageTextDTO, DownloadMessageMediaDTO
from service.message_spider_service import MessageService
import asyncio

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
def search_message_text(dto: SearchMessageTextDTO, service: MessageService = Depends()):
    return ResData.success(service.search_messages_by_text(
        text=dto.messageText,
        channel=dto.channel,
        page=dto.page,
        page_size=dto.page_size
    ))


@message_spider_router.post("/download_message_media")
async def download_message_media(download_message_media_dto: DownloadMessageMediaDTO,
                                 service: MessageService = Depends()):
    asyncio.create_task(service.download_media_from_message(download_message_media_dto.message_link))
    return ResData.success("提交下载任务成功")