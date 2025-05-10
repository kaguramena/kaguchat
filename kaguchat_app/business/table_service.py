from ..data.db_access import DatabaseAccess

class TableService:
    def __init__(self):
        self.db_access = DatabaseAccess()

    def get_table_columns(self, table_name_actual):
        return self.db_access.get_table_columns(table_name_actual)

    def get_primary_key(self, table_name_actual):
        return self.db_access.get_primary_key(table_name_actual)

    def get_table_data(self, table_name_actual):
        return self.db_access.get_table_data(table_name_actual)

    def add_record(self, table_name_actual, values_dict):
        # values_dict 是 {column_name: value}
        # 需要将其转换为适合 db_access.execute_update 的格式
        columns = list(values_dict.keys())
        placeholders = ', '.join(['%s'] * len(columns))
        sql_columns = ', '.join(columns)
        query = f"INSERT INTO {table_name_actual} ({sql_columns}) VALUES ({placeholders})"
        params = tuple(values_dict.values())
        return self.db_access.execute_update(query, params, fetch_id=True) # 假设返回ID

    def update_record(self, table_name_actual, primary_key_column, record_id, values_dict):
        if not values_dict:
            return True # 没有要更新的
        set_clauses = [f"{col} = %s" for col in values_dict.keys()]
        query = f"UPDATE {table_name_actual} SET {', '.join(set_clauses)} WHERE {primary_key_column} = %s"
        params = tuple(list(values_dict.values()) + [record_id])
        return self.db_access.execute_update(query, params)

    def delete_record(self, table_name_actual, primary_key_column, record_id):
        query = f"DELETE FROM {table_name_actual} WHERE {primary_key_column} = %s"
        return self.db_access.execute_update(query, (record_id,))

    def record_exists(self, table_name_actual, conditions_dict):
        """
        检查满足条件的记录是否存在。
        conditions_dict: {'column_name': value, 'column_name2 !=': value2}
        """
        if not conditions_dict:
            return False
        clauses = []
        params = []
        for col, val in conditions_dict.items():
            operator = "=" # 默认操作符
            column_name = col
            if col.endswith(" !="):
                operator = "!="
                column_name = col[:-3].strip()
            elif col.endswith(" >"):
                operator = ">"
                column_name = col[:-2].strip()
            # ...可以添加更多操作符支持
            clauses.append(f"{column_name} {operator} %s")
            params.append(val)

        query = f"SELECT COUNT(1) AS count_exists FROM {table_name_actual} WHERE {' AND '.join(clauses)}"
        result = self.db_access.execute_query(query, tuple(params))
        return result[0]['count_exists'] > 0 if result and result[0] else False

    def get_record_by_primary_key(self, table_name_actual, primary_key_column, record_id):
        """根据主键获取单条记录，返回字典形式。"""
        query = f"SELECT * FROM {table_name_actual} WHERE {primary_key_column} = %s"
        result_rows = self.db_access.execute_query(query, (record_id,))
        if result_rows:
            columns = self.get_table_columns(table_name_actual)
            return dict(zip(columns, result_rows[0]))
        return None

    def get_record_by_field(self, table_name_actual, field_name, field_value):
        """根据特定字段和值获取单条记录（假设该字段唯一或取第一条），返回字典。"""
        query = f"SELECT * FROM {table_name_actual} WHERE {field_name} = %s LIMIT 1"
        result_rows = self.db_access.execute_query(query, (field_value,))
        if result_rows:
            columns = self.get_table_columns(table_name_actual)
            return dict(zip(columns, result_rows[0]))
        return None