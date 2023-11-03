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
        sql_insert = "INSERT INTO tb_message (channel, message_id, date, message_text, link) VALUES (%s, %s, %s, %s, %s)"
        values = (msg["channel"], msg["id"], msg["date"], msg["text"], msg["link"])
        cursor.execute(sql_insert, values)
        self.db.commit()

    def search_messages_by_text(self, text):
        cursor = self.db.cursor()
        sql_query = "SELECT * FROM tb_message WHERE message_text LIKE %s"
        cursor.execute(sql_query, ("%" + text + "%",))
        return cursor.fetchall()
