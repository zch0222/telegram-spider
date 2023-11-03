from fastapi import Depends
import pymysql
import os


class Database:
    def __init__(self):
        print(os.environ.get("MYSQL_USER"))
        self.conn = pymysql.connect(host=os.environ.get("MYSQL_HOST"), user=os.environ.get("MYSQL_USER"),
                                    password=os.environ.get("MYSQL_PASSWORD"),
                                    database=os.environ.get("MYSQL_DATABASE"))

    def get_conn(self):
        return self.conn


def get_db(database: Database = Depends()):
    return database.get_conn()
