from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from model import YouGetSubmitDTO
from service.youtube_dl_service import YoutubeDlService


youtube_dl_router = APIRouter()


@youtube_dl_router.post("/youtube_dl/submit")
def you_get_submit(you_get_submit_dto: YouGetSubmitDTO, service: YoutubeDlService = Depends()):
    return service.submit(you_get_submit_dto.url)
