import asyncio
import logging
import threading  # 1. 引入线程锁模块
from telethon import TelegramClient, events
from core.config import TELETHON_API_ID, TELETHON_API_HASH, TELETHON_SESSION_NAME

# 引入你的 DB 和 DAO
from db import get_db
from dao.message_dao import MessageDAO
from dao.sub_group_dao import SubGroupDAO

logger = logging.getLogger("telegram_client")


class TelegramClientManager:
    def __init__(self):
        # 1. 初始化 Client
        self.client = TelegramClient(TELETHON_SESSION_NAME, TELETHON_API_ID, TELETHON_API_HASH)

        # 2. 内存缓存
        self.target_chat_ids = set()

        # 3. 初始化线程锁 (Thread Safe)
        # 用于保护 self.target_chat_ids 在多线程环境下（Asyncio 线程 vs Web 外部线程）的读写安全
        self._lock = threading.Lock()

    async def start(self):
        """生命周期：启动"""
        logger.info("正在启动 Telegram Client...")
        await self.client.start()

        # 注册事件监听
        self.client.add_event_handler(self._message_handler, events.NewMessage(incoming=True))

        # 启动时加载数据库中的订阅列表
        await self.refresh_cache()
        logger.info("Telegram Client 启动成功")

    async def stop(self):
        """生命周期：停止"""
        logger.info("正在断开 Telegram Client...")
        await self.client.disconnect()

    async def refresh_cache(self):
        """从数据库刷新缓存 (线程安全)"""
        db = get_db()
        try:
            # 在锁外进行数据库查询（IO耗时操作，不要阻塞锁）
            dao = SubGroupDAO(db)
            all_groups = dao.get_all_sub_group()

            # 准备新的 Set
            new_ids = {int(item["group_id"]) for item in all_groups if item.get("group_id")}

            # --- 临界区：更新内存 ---
            with self._lock:
                self.target_chat_ids = new_ids
            # ---------------------

            logger.info(f"缓存刷新完毕，当前监听 {len(new_ids)} 个频道")
        except Exception as e:
            logger.error(f"刷新缓存失败: {e}")
        finally:
            # 确保关闭数据库连接
            if hasattr(db, 'close'):
                db.close()

    def add_id_to_cache(self, chat_id: int):
        """供外部 Service 调用：动态添加 ID (线程安全)"""
        with self._lock:
            self.target_chat_ids.add(int(chat_id))
        logger.debug(f"动态添加监听 ID: {chat_id}")

    def remove_id_from_cache(self, chat_id: int):
        """供外部 Service 调用：动态移除 ID (线程安全)"""
        with self._lock:
            if int(chat_id) in self.target_chat_ids:
                self.target_chat_ids.remove(int(chat_id))
        logger.debug(f"动态移除监听 ID: {chat_id}")

    async def _message_handler(self, event):
        """
        核心消息处理器
        """
        # --- 1. 线程安全的极速过滤 ---
        # 仅在判断集合包含关系时加锁，速度极快 (O(1))
        # 如果不加锁，当外部正在 refresh_cache 重置集合时，这里可能会报错
        should_process = False
        with self._lock:
            if event.chat_id in self.target_chat_ids:
                should_process = True

        if not should_process:
            return

        # --- 2. 业务逻辑 (耗时操作在锁外进行) ---
        try:
            chat = await event.get_chat()
            sender = await event.get_sender()

            chat_username = chat.username if hasattr(chat, 'username') and chat.username else str(chat.id)
            sender_username = getattr(sender, 'username', None)

            # 构造链接
            msg_link = ""
            if hasattr(chat, 'username') and chat.username:
                msg_link = f"https://t.me/{chat_username}/{event.id}"

            msg_data = {
                "channel": f"@{chat_username}" if hasattr(chat, 'username') and chat.username else str(chat.id),
                "channel_name": getattr(chat, 'title', "Unknown"),
                "id": event.id,
                "date": event.date,
                "text": event.text,
                "link": msg_link,
                "sender_username": sender_username,
                "sender_id": str(sender.id) if sender else None
            }

            # --- 3. 异步转同步写入数据库 ---
            # 使用 asyncio.to_thread 避免阻塞 Telegram 的事件循环
            await asyncio.to_thread(self._save_message_sync, msg_data)

        except Exception as e:
            logger.error(f"处理消息异常: {e}")

    def _save_message_sync(self, msg_data):
        """同步方法：手动管理 DB 连接并写入"""
        db = get_db()
        try:
            dao = MessageDAO(db)
            dao.insert_message(msg_data)
            logger.info(f"消息已保存: {msg_data['id']} (来自: {msg_data['channel_name']})")
        except Exception as e:
            logger.error(f"数据库写入失败: {e}")
        finally:
            # 极其重要：手动获取的 DB 连接必须手动释放
            if hasattr(db, 'close'):
                db.close()

    def get_client(self):
        return self.client

    def get_target_chat_ids(self):
        with self._lock:
            return self.target_chat_ids.copy()


# --- 实例化全局单例 ---
telegram_manager = TelegramClientManager()