from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from model import YouGetSubmitDTO
from service.you_get_service import YouGetService


you_get_router = APIRouter()

@you_get_router.post("/you_get/submit")
def you_get_submit(you_get_submit_dto: YouGetSubmitDTO, service: YouGetService = Depends()):
    service.submit(you_get_submit_dto.url)
