from pydantic import BaseModel


class YoutubeDlSubmitDTO(BaseModel):
    url_list: list[str]
