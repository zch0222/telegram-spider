from pydantic import BaseModel


class SearchMessageTextDTO(BaseModel):
    messageText: str
