from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from service.yt_dlp_service import YtDlpService
from model import ResData
import asyncio

yt_dlp_router = APIRouter(prefix="/yt-dlp", tags=["Yt-Dlp Download"])

class YtDlpSubmitDTO(BaseModel):
    url: str

@yt_dlp_router.post("/submit")
async def submit_task(dto: YtDlpSubmitDTO, service: YtDlpService = Depends()):
    task_id = await service.submit_task(dto.url)
    return ResData.success({"task_id": task_id}, "Task submitted successfully")

@yt_dlp_router.get("/process")
async def get_process(service: YtDlpService = Depends()):
    headers = {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive'
    }
    return StreamingResponse(service.get_task_progress_stream(), headers=headers)

@yt_dlp_router.get("/list")
async def get_list(service: YtDlpService = Depends()):
    tasks = await service.get_all_tasks()
    return ResData.success(tasks)
