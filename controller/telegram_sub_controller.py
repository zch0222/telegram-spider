from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from model.res_data import ResData
from exception.business_exception import BusinessException
from core.log import get_logger

logger = get_logger()

# 引入你的 Service
from service.telegram_sub_service import TelegramSubService

# 定义 Router
telegram_sub_router = APIRouter(
    prefix="/api/telegram/subscribe",
    tags=["Telegram Subscription Manager"]
)


# --- DTO (Data Transfer Objects) ---

class ChannelRequest(BaseModel):
    """
    用于添加或移除频道的请求体
    """
    channel_input: str = Field(
        ...,
        description="频道的用户名 (@username), 邀请链接 (https://t.me/...), 或 ID",
        example="@google"
    )


class SubGroupResponse(BaseModel):
    """
    订阅群组的返回模型 (根据你的 DAO 返回结构定义，这里做个通用定义)
    """
    group_id: int
    group_name: str | None = None
    group_type: int | None = None
    group_link: str | None = None


# --- Endpoints ---

@telegram_sub_router.post("/add", status_code=status.HTTP_201_CREATED)
async def add_channel(
        request: ChannelRequest,
        service: TelegramSubService = Depends()
):
    """
    **动态添加监听频道**

    - 解析 Telegram 频道/群组信息
    - 存入数据库
    - 加入内存缓存进行实时监听
    """
    try:
        result = await service.add_channel(request.channel_input)
        return ResData.success(result)
    except ValueError as e:
        # 捕获已知参数错误
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        # 捕获 Telethon 连接错误或其他未知错误
        # 建议在 Service 层具体化 Exception 类型，这里统一处理为 500 或 400
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"添加频道失败: {str(e)}"
        )


@telegram_sub_router.get("/list", response_model=List[Dict[str, Any]])
def get_all_subscriptions(
        service: TelegramSubService = Depends()
):
    """
    **获取所有已订阅的频道/群组列表**
    """
    try:
        # Service 中 get_all_sub_groups 是同步方法，这里不需要 await
        # FastAPI 会在线程池中运行它，不会阻塞主循环
        return ResData.success(service.get_all_sub_groups())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取列表失败: {str(e)}"
        )

@telegram_sub_router.get("/telegram_manager_chat_ids", response_model=List[Dict[str, Any]])
def get_all_subscriptions(
        service: TelegramSubService = Depends()
):
    """
    **获取所有已订阅的频道/群组列表**
    """
    try:
        # Service 中 get_all_sub_groups 是同步方法，这里不需要 await
        # FastAPI 会在线程池中运行它，不会阻塞主循环
        return ResData.success(service.get_telegram_manager_target_chat_ids())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取列表失败: {str(e)}"
        )

@telegram_sub_router.delete("/remove")
async def remove_channel(
        channel_input: str = Query(..., description="要移除的频道标识 (用户名/链接/ID)"),
        service: TelegramSubService = Depends()
):
    """
    **移除监听频道**

    - 从数据库删除
    - 从内存缓存移除
    """
    try:
        result = await service.remove_channel(channel_input)

        if result.get("status") == "not_found":
            raise BusinessException("频道不存在")

        return ResData.success(result)
    except HTTPException:
        raise 
    except Exception as e:
        raise BusinessException("移除频道失败")