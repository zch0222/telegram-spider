import asyncio
import os
from telethon import TelegramClient
from core.config import TELETHON_API_ID, TELETHON_API_HASH, TELETHON_SESSION_NAME

async def main():
    print(f"Starting Telegram Login...")
    print(f"Session Name: {TELETHON_SESSION_NAME}")
    
    # Ensure API ID is integer
    try:
        api_id = int(TELETHON_API_ID)
    except (ValueError, TypeError):
        print("Error: API_ID must be an integer. Please check your .env file.")
        return

    client = TelegramClient(TELETHON_SESSION_NAME, api_id, TELETHON_API_HASH)
    
    # This will prompt for phone number and code if not logged in
    await client.start()
    
    # Check if authorized
    if await client.is_user_authorized():
        me = await client.get_me()
        print(f"\n✅ Login Successful!")
        print(f"User: {me.first_name} {me.last_name or ''} (@{me.username})")
        print(f"ID: {me.id}")
        print(f"Phone: {me.phone}")
        print(f"\nSession file saved as: {TELETHON_SESSION_NAME}.session")
        print("You can now run the main application.")
    else:
        print("\n❌ Login Failed.")
    
    await client.disconnect()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
