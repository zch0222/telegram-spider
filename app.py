from dotenv import load_dotenv
import os
from telethon import TelegramClient, utils
import json
import pymysql


load_dotenv()

API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")
CHANNEL = os.environ.get("CHANNEL")

print(API_ID)

client = TelegramClient('Jian', API_ID, API_HASH)

# 连接数据库
db = pymysql.connect(host=os.environ.get("MYSQL_HOST"), user=os.environ.get("MYSQL_USER"), password=os.environ.get("MYSQL_PASSWORD"), database=os.environ.get("MYSQL_DATABASE"))

async def main():
    me = await client.get_me()
    print(me.username)

    msges = []

    messages = client.iter_messages(CHANNEL, min_id=int(os.environ.get("MIN_ID")))
    async for message in messages:
        print(str(message.date))
        msg = {
            "id": message.id,
            "date": str(message.date),
            "text": message.text,
            "link": f"https://t.me/c/{message.to_id.channel_id}/{message.id}"  # 构建链接
        }
        msges.append(msg)

        print(msg)

        # 使用cursor ()方法获取操作游标
        cursor = db.cursor()

        # SQL 查询语句
        sql_query = "SELECT * FROM tb_message WHERE link = %s"
        cursor.execute(sql_query, (msg["link"],))
        result = cursor.fetchone()

        # 如果没有找到相同的链接，那么插入数据
        if result is None:
            # SQL 插入语句
            sql_insert = "INSERT INTO tb_message (channel, message_id, date, message_text, link) VALUES (%s, %s, %s, %s, %s)"
            values = (CHANNEL, msg["id"], msg["date"], msg["text"], msg["link"])

            try:
                # 执行sql语句
                cursor.execute(sql_insert, values)
                # 提交到数据库执行
                db.commit()
            except Exception as e:
                print(e)
                # 如果发生错误则回滚
                db.rollback()


    with open(f"messages.json", 'w', encoding='utf-8') as f:
        json.dump(msges, f, ensure_ascii=False, indent=4)


with client:
    client.loop.run_until_complete(main())

# 关闭数据库连接
db.close()