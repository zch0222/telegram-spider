from pydantic import BaseModel
import json

class TaskBO(BaseModel):
    createTime: str
    channel: str
    currentMessageId: int
    minMessageId: int
    percent: float

    def to_json_str(self):
        print(json.dumps({
            "createTime": self.createTime,
            "channel": self.channel,
            "currentMessageId": self.currentMessageId,
            "minMessageId": self.minMessageId,
            "percent": self.percent
        }))
        return json.dumps({
            "createTime": self.createTime,
            "channel": self.channel,
            "currentMessageId": self.currentMessageId,
            "minMessageId": self.minMessageId,
            "percent": self.percent
        })
