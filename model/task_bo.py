from pydantic import BaseModel


class TaskBO(BaseModel):
    createTime: str
    channel: str
    currentMessageId: int
    minMessageId: int

    def to_dic(self):
        return {
            "createTime": self.createTime,
            "channel": self.channel,
            "currentMessageId": self.currentMessageId,
            "minMessageId": self.minMessageId
        }
