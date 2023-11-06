from pydantic import BaseModel


class YouGetSubmitDTO(BaseModel):
    url: str
