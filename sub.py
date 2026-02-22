import asyncio
import os
import time
import pytz
from telethon import TelegramClient
from core.config import TELETHON_API_ID, TELETHON_API_HASH, TELETHON_SESSION_NAME, CHECK_INTERVAL
from db.session import Database
from dao.message_dao import MessageDAO
from core.log import get_logger

# Configure logger
logger = get_logger()

# Load target chats
target_chats_env = os.environ.get("TARGET_CHATS", "")
target_chats = [item.strip() for item in target_chats_env.split(",") if item.strip()]

async def save_message(dao, message, chat, sender):
    try:
        chat_username = chat.username if hasattr(chat, 'username') and chat.username else str(chat.id)
        sender_username = getattr(sender, 'username', None)
        sender_id = str(sender.id) if sender else None

        # Build link
        msg_link = f"https://t.me/{chat_username}/{message.id}" if hasattr(chat, 'username') and chat.username else ""

        # Build data dict
        msg_data = {
            "channel": f"@{chat_username}" if hasattr(chat, 'username') and chat.username else str(chat.id),
            "channel_name": chat.title if hasattr(chat, 'title') else "Unknown",
            "id": message.id,
            "date": message.date,
            "text": message.text,
            "link": msg_link,
            "sender_username": sender_username,
            "sender_id": sender_id
        }

        # Save to DB
        dao.insert_message(msg_data)
        logger.info(f"Saved message: channel={msg_data['channel']} id={msg_data['id']}")
        
    except Exception as e:
        logger.error(f"Error saving message {message.id}: {e}")

async def main():
    logger.info("Initializing Telegram Client...")
    
    # Ensure API ID is integer
    try:
        api_id = int(TELETHON_API_ID)
    except (ValueError, TypeError):
        api_id = TELETHON_API_ID

    client = TelegramClient(TELETHON_SESSION_NAME, api_id, TELETHON_API_HASH)
    await client.start()
    
    logger.info(f"Client started. Monitoring {len(target_chats)} chats: {target_chats}")
    logger.info(f"Check interval: {CHECK_INTERVAL} seconds")

    while True:
        try:
            logger.info("Starting polling cycle...")
            start_time = time.time()
            
            # Create a new DB connection for this cycle
            db_conn = Database().get_conn()
            dao = MessageDAO(db_conn)
            
            for chat_target in target_chats:
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
                    # If last_id is 0, limit to 20 to avoid fetching too much history on first run
                    limit = None if last_id > 0 else 20
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
                        await save_message(dao, message, entity, sender)
                        
                except Exception as e:
                    logger.error(f"Error processing {chat_target}: {e}")
            
            # Close connection
            try:
                db_conn.close()
            except:
                pass
            
            elapsed = time.time() - start_time
            logger.info(f"Cycle completed in {elapsed:.2f}s")
            
        except Exception as e:
            logger.error(f"Global error in polling loop: {e}")
            await asyncio.sleep(10)
            
        logger.info(f"Sleeping for {CHECK_INTERVAL} seconds...")
        await asyncio.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Service stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
