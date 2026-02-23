from fastapi import APIRouter, Depends
from model.polling_log_search_dto import PollingLogSearchDTO
from service.polling_log_service import PollingLogService
from model import ResData

polling_log_router = APIRouter(prefix="/polling_log", tags=["Polling Logs"])

@polling_log_router.post("/search")
def search_logs(dto: PollingLogSearchDTO, service: PollingLogService = Depends()):
    result = service.search_logs(dto.level, dto.keyword, dto.page, dto.page_size)
    return ResData.success(result)
