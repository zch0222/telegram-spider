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

    def search_messages_by_text(self, text, channel=None, page=1, page_size=20):
        cursor = self.db.cursor()
        
        sql_query = "SELECT * FROM tb_message WHERE 1=1"
        params = []
        
        if text:
            sql_query += " AND message_text LIKE %s"
            params.append("%" + text + "%")
            
        if channel:
            sql_query += " AND channel LIKE %s"
            params.append("%" + channel + "%")
            
        # Add sorting (descending by date)
        sql_query += " ORDER BY date DESC"
        
        # Add pagination
        offset = (page - 1) * page_size
        sql_query += " LIMIT %s OFFSET %s"
        params.extend([page_size, offset])
        
        cursor.execute(sql_query, tuple(params))
        result_set = cursor.fetchall()

        # 获取列名
        if cursor.description:
            column_names = [desc[0] for desc in cursor.description]
            # 将结果封装到字典中
            messages = [dict(zip(column_names, row)) for row in result_set]
        else:
            messages = []

        # Get total count for pagination info
        count_sql = "SELECT COUNT(*) FROM tb_message WHERE 1=1"
        count_params = []
        
        if text:
            count_sql += " AND message_text LIKE %s"
            count_params.append("%" + text + "%")
            
        if channel:
            count_sql += " AND channel LIKE %s"
            count_params.append("%" + channel + "%")
            
        cursor.execute(count_sql, tuple(count_params))
        total = cursor.fetchone()[0]

        return {
            "list": messages,
            "total": total,
            "page": page,
            "page_size": page_size
        }

    def get_latest_message_id(self, channel):
        cursor = self.db.cursor()
        sql_query = "SELECT MAX(message_id) FROM tb_message WHERE channel = %s"
        cursor.execute(sql_query, (channel,))
        result = cursor.fetchone()
        return result[0] if result and result[0] is not None else 0
