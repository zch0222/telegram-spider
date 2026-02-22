from db import get_db
from fastapi import Depends

class UserDAO:
    def __init__(self, db=Depends(get_db)):
        self.db = db

    def get_user_by_username(self, username):
        cursor = self.db.cursor()
        sql = "SELECT id, username, password FROM tb_user WHERE username = %s"
        cursor.execute(sql, (username,))
        result = cursor.fetchone()
        if result:
            return {"id": result[0], "username": result[1], "password": result[2]}
        return None

    def get_user_by_id(self, user_id):
        cursor = self.db.cursor()
        sql = "SELECT id, username, password FROM tb_user WHERE id = %s"
        cursor.execute(sql, (user_id,))
        result = cursor.fetchone()
        if result:
            return {"id": result[0], "username": result[1], "password": result[2]}
        return None

    def create_user(self, username, password):
        cursor = self.db.cursor()
        sql = "INSERT INTO tb_user (username, password) VALUES (%s, %s)"
        cursor.execute(sql, (username, password))
        self.db.commit()
        return cursor.lastrowid

    def update_password(self, user_id, new_password):
        cursor = self.db.cursor()
        sql = "UPDATE tb_user SET password = %s WHERE id = %s"
        cursor.execute(sql, (new_password, user_id))
        self.db.commit()
