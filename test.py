from telethon import TelegramClient

# Remember to use your own values from my.telegram.org!
api_id = 20845514
api_hash = 'b9664b45b910f3e48eaf7771e5d3b3b4'
client = TelegramClient('yxlm1832', api_id, api_hash)

async def main():
    # Getting information about yourself
    me = await client.get_me()

    # "me" is a user object. You can pretty-print
    # any Telegram object with the "stringify" method:
    print(me.stringify())


with client:
    client.loop.run_until_complete(main())
