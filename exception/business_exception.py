# --- 1. 自定义业务异常类 ---
class BusinessException(Exception):
    """
    自定义业务异常
    用于在 Service 层主动抛出逻辑错误，如：raise BusinessException("余额不足")
    """
    def __init__(self, msg: str):
        self.msg = msg
        super().__init__(msg)