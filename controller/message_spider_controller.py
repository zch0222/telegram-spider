from fastapi import APIRouter, Depends, Request, Response, BackgroundTasks
from fastapi.responses import StreamingResponse
from model import SubmitTaskDTO
from service.message_spider_service import MessageService
import asyncio

message_spider_router = APIRouter()


@message_spider_router.post("/submit")
async def process(submit_task_dto: SubmitTaskDTO, service: MessageService = Depends()):
    channel = submit_task_dto.channel
    min_id = submit_task_dto.min_id

    asyncio.create_task(service.process_messages(channel, min_id))

    return {"message": "Process completed"}

@message_spider_router.get("/task_process")
async def task_process(service: MessageService = Depends()):
    headers = {
        # 设置返回数据类型是SSE
        'Content-Type': 'text/event-stream',
        # 保证客户端的数据是新的
        'Cache-Control': 'no-cache',
    }
    return StreamingResponse(service.get_task_process(), headers=headers)
