from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# ==========================================
# 1. 基础模型 (包含共享字段)
# ==========================================
class SubGroup(BaseModel):
    """
    SubGroup 基础字段，对应数据库中非自动生成的列
    """
    group_type: int = Field(..., description="群组类型: 0 群聊 1 频道", examples=[1])
    group_id: int = Field(..., max_length=500, description="群组id (业务id)", examples=[10086])
    group_name: str = Field(..., max_length=500, description="群组名称", examples=["Python交流群"])
    group_link: Optional[str] = Field(None, max_length=500, description="链接", examples=["https://t.me/example"])