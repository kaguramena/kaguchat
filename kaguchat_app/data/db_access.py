# kaguchat_app/data/db_access.py
from ..db_config import get_db_connection
import mysql.connector # 显式导入，以便可以引用 mysql.connector.Error

class DatabaseAccess:
    def __init__(self):
        self.connection = None
        self.cursor = None
        # print("DB_ACCESS: Initialized") # 调试

    def _get_connection_and_cursor(self):
        """获取新的连接和游标。"""
        # print("DB_ACCESS: _get_connection_and_cursor called") # 调试
        connection = get_db_connection()
        if connection and connection.is_connected(): # 确保连接是活动的
            # print("DB_ACCESS: Connection successful, getting cursor.") # 调试
            return connection, connection.cursor(dictionary=True, buffered=True)
        # print("DB_ACCESS: Database connection failed in _get_connection_and_cursor") # 调试
        raise Exception("Database connection failed in _get_connection_and_cursor")

    def __enter__(self):
        """上下文管理器进入方法：获取连接和游标。"""
        # print("DB_ACCESS: __enter__ called") # 调试
        # 每次进入上下文时，都确保我们有一个有效的连接和游标
        # 如果已有连接但可能已关闭（例如网络问题），get_db_connection 应该处理重连或返回新连接
        if not self.connection or not self.connection.is_connected():
            # print("DB_ACCESS: __enter__ - No active connection, getting new one.") # 调试
            self.connection, self.cursor = self._get_connection_and_cursor()
        elif self.cursor is None: # 连接可能存在，但上次的游标已关闭并设为 None
            # print("DB_ACCESS: __enter__ - Connection exists, but no cursor, creating new cursor.") # 调试
            try:
                self.cursor = self.connection.cursor(dictionary=True, buffered=True)
            except mysql.connector.Error as e: # 如果连接在两次调用之间断开
                # print(f"DB_ACCESS: __enter__ - Error creating cursor on existing connection ({e}), trying to get new connection.") # 调试
                self.connection, self.cursor = self._get_connection_and_cursor() # 尝试重新获取连接和游标
        # else:
            # print("DB_ACCESS: __enter__ - Using existing active connection and cursor.") # 调试
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出方法：提交/回滚并关闭连接和游_cursor。"""
        # print(f"DB_ACCESS: __exit__ called. exc_type: {exc_type}") # 调试
        cursor_closed_successfully = False
        if self.cursor:
            try:
                self.cursor.close()
                cursor_closed_successfully = True
                # print("DB_ACCESS: __exit__ - Cursor closed.") # 调试
            except mysql.connector.Error as e:
                print(f"DB_ACCESS: Error closing cursor: {e}")
            finally:
                self.cursor = None # 总是将游标引用设为 None

        if self.connection:
            try:
                if self.connection.is_connected(): # 只有连接活动时才操作
                    if exc_type is None: # 如果没有异常发生
                        self.connection.commit()
                        # print("DB_ACCESS: __exit__ - Transaction committed.") # 调试
                    else: # 如果在 with 块中发生了异常
                        self.connection.rollback()
                        print(f"DB_ACCESS: Transaction rolled back due to exception: {exc_val}")
                    self.connection.close()
                    # print("DB_ACCESS: __exit__ - Connection closed.") # 调试
            except mysql.connector.Error as e:
                print(f"DB_ACCESS: Error during commit/rollback or closing connection: {e}")
            finally:
                self.connection = None # 总是将连接引用设为 None
        return False # 不抑制异常 (如果 exc_type 不是 None)

    def execute_query(self, query, params=None):
        # ... (此方法内部的 try/with self/except 保持不变) ...
        # print(f"DB_DEBUG: execute_query: {query} with params {params}") # 调试
        try:
            with self: # 使用上下文管理器确保连接和游标
                self.cursor.execute(query, params or ())
                results = self.cursor.fetchall()
                # print(f"DB_DEBUG: execute_query results: {results}") # 调试
                return results
        except mysql.connector.Error as e:
            print(f"Database query error: {e}\nQuery: {query}\nParams: {params}")
            return [] 
        except Exception as e_general:
            print(f"General error in execute_query: {e_general}\nQuery: {query}\nParams: {params}")
            return []

    def execute_update(self, query, params=None, fetch_id=False):
        # ... (此方法内部的 try/with self/except _fetch_id 保持不变) ...
        # print(f"DB_DEBUG: execute_update: {query} with params {params}, fetch_id={fetch_id}") # 调试
        try:
            with self: # 使用上下文管理器
                self.cursor.execute(query, params or ())
                if fetch_id and "INSERT" in query.upper():
                    # print(f"DB_DEBUG: execute_update lastrowid: {self.cursor.lastrowid}") # 调试
                    return self.cursor.lastrowid 
                # print(f"DB_DEBUG: execute_update rowcount: {self.cursor.rowcount}") # 调试
                return self.cursor.rowcount 
        except mysql.connector.Error as e:
            print(f"Database update error: {e}\nQuery: {query}\nParams: {params}")
            return None if fetch_id else 0 
        except Exception as e_general:
            print(f"General error in execute_update: {e_general}\nQuery: {query}\nParams: {params}")
            return None if fetch_id else 0
            
    # --- 确保其他方法 (get_table_columns等) 也使用 with self: ---
    def get_table_columns(self, table_name_actual):
        allowed_tables = ["Users", "Friends", "Groups", "Group_Members", "Messages", "Message_Attachments"]
        if table_name_actual not in allowed_tables:
            raise ValueError(f"Invalid table name: {table_name_actual}")
        query = f"DESCRIBE `{table_name_actual}`"
        # 使用 self.execute_query 以利用其内置的 with self 上下文管理
        results = self.execute_query(query)
        return [row['Field'] for row in results] if results else []

    def get_primary_key(self, table_name_actual):
        allowed_tables = ["Users", "Friends", "Groups", "Group_Members", "Messages", "Message_Attachments"]
        if table_name_actual not in allowed_tables:
            raise ValueError(f"Invalid table name: {table_name_actual}")
        query = f"""
            SELECT kcu.COLUMN_NAME
            FROM information_schema.TABLE_CONSTRAINTS AS tc
            JOIN information_schema.KEY_COLUMN_USAGE AS kcu
              ON tc.CONSTRAINT_NAME = kcu.CONSTRAINT_NAME
              AND tc.TABLE_SCHEMA = kcu.TABLE_SCHEMA
              AND tc.TABLE_NAME = kcu.TABLE_NAME
            WHERE tc.CONSTRAINT_TYPE = 'PRIMARY KEY'
              AND tc.TABLE_SCHEMA = DATABASE()
              AND tc.TABLE_NAME = %s;
        """
        results = self.execute_query(query, (table_name_actual,))
        return results[0]['COLUMN_NAME'] if results and results[0] else None

    def get_table_data(self, table_name_actual, order_by=None, limit=None):
        allowed_tables = ["Users", "Friends", "Groups", "Group_Members", "Messages", "Message_Attachments"]
        if table_name_actual not in allowed_tables:
            raise ValueError(f"Invalid table name: {table_name_actual}")
        query = f"SELECT * FROM `{table_name_actual}`"
        params = []
        if order_by:
            safe_order_by = "".join(c for c in order_by if c.isalnum() or c == '_' or c.isspace() or c == ',')
            if safe_order_by: query += f" ORDER BY {safe_order_by}"
        if limit is not None:
            try:
                safe_limit = int(limit)
                if safe_limit >= 0:
                    query += " LIMIT %s"
                    params.append(safe_limit)
            except ValueError: print(f"Warning: Invalid limit value '{limit}', ignoring.")
        return self.execute_query(query, tuple(params) if params else None)

    def get_record_by_primary_key(self, table_name_actual, primary_key_column, record_id):
        allowed_tables = ["Users", "Friends", "Groups", "Group_Members", "Messages", "Message_Attachments"]
        if table_name_actual not in allowed_tables: raise ValueError(f"Invalid table name: {table_name_actual}")
        if not primary_key_column: return None
        safe_pk_column = "".join(c for c in primary_key_column if c.isalnum() or c == '_')
        if not safe_pk_column: raise ValueError(f"Invalid primary key column name: {primary_key_column}")
        query = f"SELECT * FROM `{table_name_actual}` WHERE `{safe_pk_column}` = %s"
        results = self.execute_query(query, (record_id,))
        return results[0] if results else None

    def record_exists(self, table_name_actual, conditions_dict):
        allowed_tables = ["Users", "Friends", "Groups", "Group_Members", "Messages", "Message_Attachments"]
        if table_name_actual not in allowed_tables: raise ValueError(f"Invalid table name: {table_name_actual}")
        if not conditions_dict: return False
        clauses, params = [], []
        for col_with_op, val in conditions_dict.items():
            parts = col_with_op.split(maxsplit=1)
            column_name_raw, operator = parts[0], parts[1].strip() if len(parts) > 1 else "="
            safe_column_name = "".join(c for c in column_name_raw if c.isalnum() or c == '_')
            if not safe_column_name: raise ValueError(f"Invalid column name: {column_name_raw}")
            allowed_operators = ["=", "!=", ">", "<", ">=", "<=", "LIKE", "IS NULL", "IS NOT NULL"]
            op_upper = operator.upper()
            if op_upper not in allowed_operators: raise ValueError(f"Invalid operator: '{operator}'")
            if op_upper in ["IS NULL", "IS NOT NULL"]: clauses.append(f"`{safe_column_name}` {op_upper}")
            else:
                clauses.append(f"`{safe_column_name}` {operator} %s")
                params.append(val)
        if not clauses: return False
        query = f"SELECT 1 FROM `{table_name_actual}` WHERE {' AND '.join(clauses)} LIMIT 1"
        result = self.execute_query(query, tuple(params) if params else None)
        return bool(result)