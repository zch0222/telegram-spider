from db import get_db
from fastapi import Depends

class YtDlpDAO:
    def __init__(self, db=Depends(get_db)):
        self.db = db

    def create_task(self, url):
        cursor = self.db.cursor()
        sql = "INSERT INTO tb_yt_dlp_task (url, status) VALUES (%s, %s)"
        cursor.execute(sql, (url, "pending"))
        self.db.commit()
        return cursor.lastrowid

    def update_task_status(self, task_id, status):
        cursor = self.db.cursor()
        sql = "UPDATE tb_yt_dlp_task SET status = %s WHERE id = %s"
        cursor.execute(sql, (status, task_id))
        self.db.commit()

    def update_task_progress(self, task_id, progress, speed, eta, downloaded_bytes, total_bytes):
        cursor = self.db.cursor()
        sql = """
            UPDATE tb_yt_dlp_task 
            SET status = 'downloading', progress = %s, speed = %s, eta = %s, 
                downloaded_bytes = %s, total_bytes = %s 
            WHERE id = %s
        """
        cursor.execute(sql, (progress, speed, eta, downloaded_bytes, total_bytes, task_id))
        self.db.commit()

    def complete_task(self, task_id, title, file_path):
        cursor = self.db.cursor()
        sql = """
            UPDATE tb_yt_dlp_task 
            SET status = 'completed', title = %s, file_path = %s, progress = 100.00 
            WHERE id = %s
        """
        cursor.execute(sql, (title, file_path, task_id))
        self.db.commit()

    def fail_task(self, task_id, error_msg):
        cursor = self.db.cursor()
        sql = "UPDATE tb_yt_dlp_task SET status = 'error', error_msg = %s WHERE id = %s"
        cursor.execute(sql, (error_msg, task_id))
        self.db.commit()

    def get_pending_tasks(self):
        cursor = self.db.cursor()
        sql = "SELECT * FROM tb_yt_dlp_task WHERE status = 'pending'"
        cursor.execute(sql)
        
        if cursor.description:
            column_names = [desc[0] for desc in cursor.description]
            return [dict(zip(column_names, row)) for row in cursor.fetchall()]
        return []

    def get_all_tasks(self):
        cursor = self.db.cursor()
        sql = "SELECT * FROM tb_yt_dlp_task ORDER BY id DESC"
        cursor.execute(sql)
        
        if cursor.description:
            column_names = [desc[0] for desc in cursor.description]
            return [dict(zip(column_names, row)) for row in cursor.fetchall()]
        return []
