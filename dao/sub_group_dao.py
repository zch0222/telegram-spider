from db import get_db
from fastapi import Depends


class SubGroupDAO:
    def __init__(self, db=Depends(get_db)):
        self.db = db

    def get_all_sub_group(self):
        """
        获取所有订阅群组列表
        """
        cursor = self.db.cursor()
        sql_query = "SELECT * FROM tb_sub_group"
        cursor.execute(sql_query)

        # 获取所有查询结果
        result_set = cursor.fetchall()

        # 获取列名 (从 cursor.description 中提取)
        column_names = [desc[0] for desc in cursor.description]

        # 将结果集（元组列表）转换为字典列表
        sub_groups = [dict(zip(column_names, row)) for row in result_set]

        return sub_groups

    def insert_sub_group(self, sub_group):
        """
        新增订阅群组
        :param sub_group: 包含 group_type, group_id, group_name, group_link 的字典
        """
        cursor = self.db.cursor()
        # create_time 和 update_time 由数据库默认值处理
        sql_insert = """
            INSERT INTO tb_sub_group 
            (group_type, group_id, group_name, group_link) 
            VALUES (%s, %s, %s, %s)
        """
        values = (
            sub_group["group_type"],
            sub_group["group_id"],
            sub_group["group_name"],
            sub_group.get("group_link")  # 使用 get 防止 link 为空时报错，或者是 None
        )
        cursor.execute(sql_insert, values)
        self.db.commit()
        return cursor.lastrowid

    def get_sub_group_by_id(self, pk_id):
        """
        根据主键ID获取群组
        """
        cursor = self.db.cursor()
        sql_query = "SELECT * FROM tb_sub_group WHERE id = %s"
        cursor.execute(sql_query, (pk_id,))

        row = cursor.fetchone()
        if row:
            # 模仿参考代码，将结果封装为字典
            column_names = [desc[0] for desc in cursor.description]
            return dict(zip(column_names, row))
        return None

    def get_sub_group_by_group_id(self, group_id):
        """
        根据业务 group_id 获取群组
        """
        cursor = self.db.cursor()
        sql_query = "SELECT * FROM tb_sub_group WHERE group_id = %s"
        cursor.execute(sql_query, (group_id,))

        row = cursor.fetchone()
        if row:
            column_names = [desc[0] for desc in cursor.description]
            return dict(zip(column_names, row))
        return None

    def update_sub_group(self, pk_id, sub_group):
        """
        更新群组信息
        :param pk_id: 主键ID
        :param sub_group: 包含要更新字段的字典
        """
        cursor = self.db.cursor()
        # 更新时手动刷新 update_time 为当前时间 (NOW())
        sql_update = """
            UPDATE tb_sub_group 
            SET group_type = %s, group_name = %s, group_link = %s, update_time = NOW() 
            WHERE id = %s
        """
        values = (
            sub_group["group_type"],
            sub_group["group_name"],
            sub_group.get("group_link"),
            pk_id
        )
        cursor.execute(sql_update, values)
        self.db.commit()

    def delete_sub_group(self, pk_id):
        """
        根据主键ID删除群组
        """
        cursor = self.db.cursor()
        sql_delete = "DELETE FROM tb_sub_group WHERE id = %s"
        cursor.execute(sql_delete, (pk_id,))
        self.db.commit()

    def delete_by_group_id(self, group_id: int):
        """
        根据group_id删除群组
        """
        cursor = self.db.cursor()
        sql_delete = "DELETE FROM tb_sub_group WHERE group_id = %s"
        cursor.execute(sql_delete, (group_id,))
        self.db.commit()

    def search_sub_groups_by_name(self, name):
        """
        根据群组名称模糊搜索
        """
        cursor = self.db.cursor()
        sql_query = "SELECT * FROM tb_sub_group WHERE group_name LIKE %s"
        cursor.execute(sql_query, ("%" + name + "%",))
        result_set = cursor.fetchall()

        # 获取列名
        column_names = [desc[0] for desc in cursor.description]

        # 将结果封装到字典中
        sub_groups = [dict(zip(column_names, row)) for row in result_set]

        return sub_groups