from pydantic import BaseModel


class DownloadMessageMediaDTO(BaseModel):
    message_link: str
