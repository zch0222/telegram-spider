from pydantic import BaseModel
from typing import Optional

class PollingLogSearchDTO(BaseModel):
    level: Optional[str] = None
    keyword: Optional[str] = None
    page: int = 1
    page_size: int = 20
