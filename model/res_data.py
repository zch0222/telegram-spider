from dataclasses import dataclass

@dataclass
class ResData:
    code: int
    msg: str
    data: object

    def to_dict(self):
        return {
            "code": self.code,
            "msg": self.msg,
            "data": self.data
        }

    @staticmethod
    def success(data: object):
        res_data = ResData(1, "", data)
        return res_data.to_dict()

    @staticmethod
    def error(msg: str):
        res_data = ResData(0, msg, {})
        return res_data.to_dict()
