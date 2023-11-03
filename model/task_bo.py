from pydantic import BaseModel
import json

class TaskBO(BaseModel):
    createTime: str
    channel: str
    currentMessageId: int
    minMessageId: int

    def to_json_str(self):
        return json.dumps({
            "createTime": self.createTime,
            "channel": self.channel,
            "currentMessageId": self.currentMessageId,
            "minMessageId": self.minMessageId
        })
