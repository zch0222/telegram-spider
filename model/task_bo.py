from pydantic import BaseModel
import json


class TaskBO(BaseModel):
    name: str
    createTime: str
    channel: str
    currentMessageId: int
    minMessageId: int
    percent: float

    def to_json_str(self):
        print(json.dumps({
            "name": self.name,
            "createTime": self.createTime,
            "channel": self.channel,
            "currentMessageId": self.currentMessageId,
            "minMessageId": self.minMessageId,
            "percent": self.percent
        }))
        return json.dumps({
            "name": self.name,
            "createTime": self.createTime,
            "channel": self.channel,
            "currentMessageId": self.currentMessageId,
            "minMessageId": self.minMessageId,
            "percent": self.percent
        })
