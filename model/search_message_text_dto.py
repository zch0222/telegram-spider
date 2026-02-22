from pydantic import BaseModel
from typing import Optional


class SearchMessageTextDTO(BaseModel):
    messageText: Optional[str] = None
    channel: Optional[str] = None
    page: int = 1
    page_size: int = 20
