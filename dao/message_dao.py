from db import get_db
from fastapi import Depends


class MessageDAO:
    def __init__(self, db=Depends(get_db)):
        self.db = db

    def get_message_by_link(self, link):
        cursor = self.db.cursor()
        sql_query = "SELECT * FROM tb_message WHERE link = %s"
        cursor.execute(sql_query, (link,))
        return cursor.fetchone()

    def insert_message(self, msg):
        cursor = self.db.cursor()
        sql_insert = "INSERT INTO tb_message (channel, channel_name, message_id, date, message_text, link, sender_username, sender_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        values = (msg["channel"], msg["channel_name"], msg["id"], msg["date"], msg["text"], msg["link"], msg["sender_username"], msg["sender_id"])
        cursor.execute(sql_insert, values)
        self.db.commit()

    def search_messages_by_text(self, text):
        cursor = self.db.cursor()
        sql_query = "SELECT * FROM tb_message WHERE message_text LIKE %s"
        cursor.execute(sql_query, ("%" + text + "%",))
        result_set = cursor.fetchall()

        # 获取列名
        column_names = [desc[0] for desc in cursor.description]

        # 将结果封装到字典中
        messages = [dict(zip(column_names, row)) for row in result_set]

        return messages

    def get_latest_message_id(self, channel):
        cursor = self.db.cursor()
        sql_query = "SELECT MAX(message_id) FROM tb_message WHERE channel = %s"
        cursor.execute(sql_query, (channel,))
        result = cursor.fetchone()
        return result[0] if result and result[0] is not None else 0
