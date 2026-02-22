import asyncio
import time
import os
import pytz
from core.config import CHECK_INTERVAL
from db.session import Database
from dao.message_dao import MessageDAO
from core.log import get_logger
from core.telegram_client import telegram_manager

logger = get_logger()

class PollingService:
    def __init__(self):
        self.is_running = False
        self._task = None
        self.target_chats = []

    async def start(self):
        if self.is_running:
            return
        
        # Load target chats
        target_chats_env = os.environ.get("TARGET_CHATS", "")
        self.target_chats = [item.strip() for item in target_chats_env.split(",") if item.strip()]

        self.is_running = True
        logger.info(f"Polling Service started. Monitoring {len(self.target_chats)} chats: {self.target_chats}")
        # Run loop in background
        self._task = asyncio.create_task(self._run_loop())

    async def stop(self):
        if not self.is_running:
            return
        self.is_running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Polling Service stopped.")

    async def _run_loop(self):
        while self.is_running:
            try:
                # Check if client is connected
                if not telegram_manager.client.is_connected():
                    logger.warning("Telegram client not connected, waiting...")
                    await asyncio.sleep(5)
                    continue

                await self._poll()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Global error in polling loop: {e}")
                await asyncio.sleep(10)
            
            logger.info(f"Sleeping for {CHECK_INTERVAL} seconds...")
            await asyncio.sleep(CHECK_INTERVAL)

    async def _poll(self):
        logger.info("Starting polling cycle...")
        start_time = time.time()
        
        # Create a new DB connection for this cycle
        db_conn = Database().get_conn()
        dao = MessageDAO(db_conn)
        
        client = telegram_manager.client
        
        for chat_target in self.target_chats:
            try:
                # Resolve entity
                entity = await client.get_entity(chat_target)
                
                # Determine channel identifier as used in DB
                chat_username = entity.username if hasattr(entity, 'username') and entity.username else str(entity.id)
                channel_str = f"@{chat_username}" if hasattr(entity, 'username') and entity.username else str(entity.id)
                
                # Get latest ID
                last_id = dao.get_latest_message_id(channel_str)
                logger.info(f"Checking {chat_target} ({channel_str}). Last ID in DB: {last_id}")
                
                # Fetch new messages
                # If last_id is 0 (first time subscription), limit to 100 to avoid fetching too much history
                limit = None if last_id > 0 else 100
                min_id = last_id
                
                # client.get_messages returns a TotalList which is a list-like object
                messages = await client.get_messages(entity, min_id=min_id, limit=limit)
                
                if not messages:
                    logger.info(f"No new messages for {chat_target}")
                    continue
                    
                logger.info(f"Found {len(messages)} new messages for {chat_target}")
                
                # Process messages (oldest first)
                for message in reversed(messages):
                    sender = await message.get_sender()
                    await self._save_message(dao, message, entity, sender)
                    
            except Exception as e:
                logger.error(f"Error processing {chat_target}: {e}")
        
        # Close connection
        try:
            db_conn.close()
        except:
            pass
        
        elapsed = time.time() - start_time
        logger.info(f"Cycle completed in {elapsed:.2f}s")

    async def _save_message(self, dao, message, chat, sender):
        try:
            chat_username = chat.username if hasattr(chat, 'username') and chat.username else str(chat.id)
            sender_username = getattr(sender, 'username', None)
            sender_id = str(sender.id) if sender else None

            # Build link
            msg_link = f"https://t.me/{chat_username}/{message.id}" if hasattr(chat, 'username') and chat.username else ""

            # Use UTC date directly
            msg_date = message.date

            # Build data dict
            msg_data = {
                "channel": f"@{chat_username}" if hasattr(chat, 'username') and chat.username else str(chat.id),
                "channel_name": chat.title if hasattr(chat, 'title') else "Unknown",
                "id": message.id,
                "date": msg_date,
                "text": message.text,
                "link": msg_link,
                "sender_username": sender_username,
                "sender_id": sender_id
            }

            # Save to DB
            dao.insert_message(msg_data)
            logger.info(f"Saved message: channel={msg_data['channel']} id={msg_data['id']} date={msg_data['date']}")
            
        except Exception as e:
            logger.error(f"Error saving message {message.id}: {e}")

# Global instance
polling_service = PollingService()
