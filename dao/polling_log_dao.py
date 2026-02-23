from db import get_db
from fastapi import Depends

class PollingLogDAO:
    def __init__(self, db=Depends(get_db)):
        self.db = db

    def log(self, level: str, message: str, module: str = "PollingService"):
        try:
            cursor = self.db.cursor()
            sql = "INSERT INTO tb_polling_log (level, message, module) VALUES (%s, %s, %s)"
            cursor.execute(sql, (level, message, module))
            self.db.commit()
        except Exception as e:
            print(f"Failed to write log to DB: {e}")

    def query_logs(self, level=None, keyword=None, page=1, page_size=20):
        cursor = self.db.cursor()
        sql = "SELECT * FROM tb_polling_log WHERE 1=1"
        params = []
        
        if level:
            sql += " AND level = %s"
            params.append(level)
            
        if keyword:
            sql += " AND message LIKE %s"
            params.append(f"%{keyword}%")
            
        sql += " ORDER BY id DESC LIMIT %s OFFSET %s"
        params.append(page_size)
        params.append((page - 1) * page_size)
        
        cursor.execute(sql, params)
        if cursor.description:
            column_names = [desc[0] for desc in cursor.description]
            return [dict(zip(column_names, row)) for row in cursor.fetchall()]
        return []

    def count_logs(self, level=None, keyword=None):
        cursor = self.db.cursor()
        sql = "SELECT COUNT(*) FROM tb_polling_log WHERE 1=1"
        params = []
        
        if level:
            sql += " AND level = %s"
            params.append(level)
            
        if keyword:
            sql += " AND message LIKE %s"
            params.append(f"%{keyword}%")
            
        cursor.execute(sql, params)
        return cursor.fetchone()[0]
