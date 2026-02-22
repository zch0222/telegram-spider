from fastapi import Depends
import logging

from core import get_logger
# 引入你原有的数据库逻辑
from dao.message_dao import MessageDAO
from dao.sub_group_dao import SubGroupDAO
from model.sub_group import SubGroup
from core.telegram_client import telegram_manager


class TelegramSubService:
    def __init__(self, message_dao: MessageDAO = Depends(), sub_group_dao: SubGroupDAO = Depends(),
                 logger: logging.Logger = Depends(get_logger)):
        self.client = telegram_manager.get_client()
        self.message_dao = message_dao
        self.logger = logger
        # 订阅频道过滤
        self.sub_group_dao = sub_group_dao

    async def add_channel(self, channel_input: str):
        """
        动态添加监听频道
        channel_input: 可以是用户名 (@google), 链接, 或 ID
        """
        try:
            # 1. 获取实体对象
            entity = await self.client.get_entity(channel_input)

            chat_id = entity.id
            chat_title = getattr(entity, 'title', 'Unknown')

            # 2. 解析群组类型 (0: 群聊, 1: 频道)
            # Telethon 中，broadcast=True 代表是 Channel，否则可能是 Chat 或 Megagroup
            is_broadcast = getattr(entity, 'broadcast', False)
            g_type = 1 if is_broadcast else 0

            # 3. 解析链接
            chat_link = None
            if hasattr(entity, 'username') and entity.username:
                chat_link = f"https://t.me/{entity.username}"

            # 5. 同步写入数据库
            # 先检查数据库是否已经存在该群组，避免重复插入报错
            existing_group = self.sub_group_dao.get_sub_group_by_group_id(chat_id)

            if not existing_group:
                # 构建 Pydantic 模型
                new_sub_group = SubGroup(
                    group_type=g_type,
                    group_id=chat_id,
                    group_name=chat_title,
                    group_link=chat_link
                )

                # 重要：DAO 里的 insert 方法需要字典，使用 model_dump() 转换
                self.sub_group_dao.insert_sub_group(new_sub_group.model_dump())

                # 添加到内存订阅中
                telegram_manager.add_id_to_cache(chat_id)

                self.logger.info(f"数据库已新增订阅: {chat_title}")
            else:
                self.logger.info(f"数据库已存在该订阅，跳过插入: {chat_title}")

            return {
                "status": "success",
                "chat_id": chat_id,
                "title": chat_title,
                "type": "Channel" if g_type == 1 else "Group"
            }

        except Exception as e:
            self.logger.error(f"添加频道失败: {e}")
            # 这里的 raise e 会导致接口返回 500 错误，如果希望接口友好返回，可以捕获并返回特定格式
            raise e

    def get_all_sub_groups(self):
        return self.sub_group_dao.get_all_sub_group()

    def get_all_sub_group_ids(self):
        all_sub_group = self.get_all_sub_groups()
        return [
            item.get("group_id")
            for item in all_sub_group
            if item.get("group_id") is not None
        ]

    def get_telegram_manager_target_chat_ids(self):
        return telegram_manager.get_target_chat_ids()

    async def remove_channel(self, channel_input: str):
        """动态移除监听频道"""
        try:
            entity = await self.client.get_entity(channel_input)
            chat_id = entity.id

            if chat_id in self.get_all_sub_group_ids():
                # 删除数据库中频道
                self.sub_group_dao.delete_by_group_id(chat_id)

                # 从内存订阅中移除
                telegram_manager.remove_id_from_cache(chat_id)

                self.logger.info(f"已移除监听: {chat_id}")
                return {"status": "removed", "chat_id": chat_id}
            else:
                return {"status": "not_found", "message": "该频道未在监听列表中"}
        except Exception as e:
            self.logger.error(f"移除频道失败: {e}")
            raise e