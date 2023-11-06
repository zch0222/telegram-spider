from pydantic import BaseModel


class YoutubeDlSubmitDTO(BaseModel):
    url: str
