from pydantic import BaseModel
import json


class YoutubeDlProcessBO(BaseModel):
    id: str
    url_list: list[str]

    def to_json_str(self):
        return json.dumps({
            "id": self.id,
            "url_list": self.url_list
        })
