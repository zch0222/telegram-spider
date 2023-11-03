from pydantic import BaseModel


class SubmitTaskDTO(BaseModel):
    channel: str
    min_id: int
