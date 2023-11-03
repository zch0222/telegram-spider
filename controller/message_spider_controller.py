from fastapi import APIRouter, Depends, Request, Response, BackgroundTasks
from model import SubmitTaskDTO
from service.message_spider_service import MessageService

message_spider_router = APIRouter()


@message_spider_router.post("/submit")
async def process(submit_task_dto: SubmitTaskDTO, service: MessageService = Depends()):
    channel = submit_task_dto.channel
    min_id = submit_task_dto.min_id

    await service.process_messages(channel, min_id)

    return {"message": "Process completed"}
