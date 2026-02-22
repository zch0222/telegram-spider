import asyncio
import os
from telethon import TelegramClient, events
import datetime
from core.config import TELETHON_API_ID, TELETHON_API_HASH, TELETHON_SESSION_NAME
from db.session import Database
from dao.message_dao import MessageDAO

# --- 配置区域 ---
api_id = TELETHON_API_ID  # 替换为你的 API ID
api_hash = TELETHON_API_HASH  # 替换为你的 API Hash
session_name = TELETHON_SESSION_NAME  # session文件名，会自动生成

print(TELETHON_API_ID)

# 这里的 chats 可以填：
# 1. 频道/群组的用户名 (例如 '@google')
# 2. 频道/群组的 ID (整数，例如 -100123456789)
# 3. 邀请链接 (例如 'https://t.me/joinchat/AAAA...')
target_chats_env = os.environ.get("TARGET_CHATS", "")
target_chats = [item.strip() for item in target_chats_env.split(",") if item.strip()]

# --- 初始化客户端 ---
client = TelegramClient(session_name, api_id, api_hash)

# --- 初始化MessageDao ---
message_dao = MessageDAO(Database())

def save_message_to_db(msg):
    print('saving message...')
    message_dao.insert_message(msg)

# --- 定义事件处理器 ---
# @client.on 装饰器用于注册事件
# events.NewMessage 表示监听新消息
# chats=target_chats 表示只监听特定列表里的群组/频道
# --- 事件处理器 ---
@client.on(events.NewMessage(chats=target_chats))
async def normal_handler(event):
    try:
        # --- 1. 数据准备 (异步快速处理) ---
        chat = await event.get_chat()
        sender = await event.get_sender()

        chat_username = chat.username if hasattr(chat, 'username') and chat.username else str(chat.id)
        sender_username = getattr(sender, 'username', None)
        sender_id = str(sender.id) if sender else None

        # 构建链接
        msg_link = f"https://t.me/{chat_username}/{event.id}" if hasattr(chat, 'username') and chat.username else ""

        # 构建数据字典
        msg_data = {
            "channel": f"@{chat_username}" if hasattr(chat, 'username') and chat.username else str(chat.id),
            "channel_name": chat.title if hasattr(chat, 'title') else "Unknown",
            "id": event.id,
            "date": event.date,
            "text": event.text,
            "link": msg_link,
            "sender_username": sender_username,
            "sender_id": sender_id
        }
        print(f"监听到消息: channel={msg_data['channel']} id={msg_data['id']} sender={msg_data['sender_username']} text={msg_data['text']}")

        # --- 2. 扔到线程池执行 (非阻塞) ---
        # asyncio.to_thread 会自动在后台线程运行 save_message_sync_task
        # 主程序会在这里 "await" 等待它完成，但不会阻塞事件循环处理其他消息
        # 如果你不希望等待写入完成（即“发后即忘”），可以使用 asyncio.create_task 配合 wrapper

        await asyncio.to_thread(save_message_to_db, msg_data)

    except Exception as e:
        print(f"处理消息异常: {e}")

# --- 启动客户端 ---
print("正在启动监听...")
print(f"监听频道列表: {target_chats}")
client.start()
print("监听中... 按 Ctrl+C 停止")
client.run_until_disconnected()
