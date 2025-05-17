# kaguchat_app/data/db_access.py
from ..db_config import get_db_connection
import mysql.connector # 显式导入，以便可以引用 mysql.connector.Error

from flask import g

import logging
logger = logging.getLogger(__name__)

def get_request_db_connection():
    """获取或创建当前请求的数据库连接，并存储在 g 中。"""
    if 'db_conn' not in g or g.db_conn is None or not g.db_conn.is_connected():
        logger.debug("Creating new DB connection for this request.")
        g.db_conn = get_db_connection() # get_db_connection() 来自你的 db_config.py
        if not g.db_conn:
            raise Exception("Failed to establish database connection for request.")
    return g.db_conn

def close_request_db_connection(e=None):
    """关闭当前请求的数据库连接（如果存在）。"""
    db_conn = g.pop('db_conn', None)
    if db_conn is not None and db_conn.is_connected():
        try:
            # 根据是否有异常决定 commit 或 rollback
            if e is None: # Flask 在 teardown_appcontext 时会传递异常信息
                db_conn.commit()
                logger.debug("DB connection committed and closed for request.")
            else:
                db_conn.rollback()
                logger.warning(f"DB connection rolled back due to exception and closed for request: {e}")
        except mysql.connector.Error as db_err:
            logger.error(f"Error during DB commit/rollback or close: {db_err}")
        finally:
            db_conn.close()

class DatabaseAccess:
    def _get_cursor(self):
        """从请求的连接获取游标"""
        conn = get_request_db_connection()
        # 每次执行查询都应该获取一个新的游标，或者确保游标在上次使用后已关闭
        # 为了简单，我们每次都获取新的，但要注意 buffered=True 的影响，或者在之后关闭它
        return conn.cursor(dictionary=True, buffered=True) # buffered=True 允许在不获取所有行的情况下关闭游标

    def execute_query(self, query, params=None):
        logger.debug(f"DB_EXECUTE_QUERY: {query} with params {params}")
        cursor = None
        try:
            cursor = self._get_cursor()
            cursor.execute(query, params or ())
            results = cursor.fetchall()
            return results
        except mysql.connector.Error as e:
            logger.error(f"Database query error: {e}\nQuery: {query}\nParams: {params}", exc_info=True)
            raise # 重新抛出，让上层处理或记录
        except Exception as e_general:
            logger.error(f"General error in execute_query: {e_general}\nQuery: {query}\nParams: {params}", exc_info=True)
            raise
        finally:
            if cursor:
                try:
                    cursor.close()
                except mysql.connector.Error as ce:
                     logger.error(f"Error closing cursor in execute_query: {ce}")


    def execute_update(self, query, params=None, fetch_id=False):
        logger.debug(f"DB_EXECUTE_UPDATE: {query} with params {params}, fetch_id={fetch_id}")
        cursor = None
        try:
            cursor = self._get_cursor()
            cursor.execute(query, params or ())
            # 对于 execute_update，通常在 close_request_db_connection 中进行 commit
            # 如果需要立即获取 lastrowid，则需要在 commit 之前
            conn = get_request_db_connection() # 获取连接以准备可能的 commit
            if fetch_id and "INSERT" in query.upper():
                last_id = cursor.lastrowid
                # conn.commit() # 可以在这里提交，或者依赖 teardown
                return last_id
            row_count = cursor.rowcount
            # conn.commit() # 可以在这里提交，或者依赖 teardown
            return row_count
        except mysql.connector.Error as e:
            logger.error(f"Database update error: {e}\nQuery: {query}\nParams: {params}", exc_info=True)
            # conn = g.get('db_conn', None) # 尝试获取连接进行回滚
            # if conn and conn.is_connected():
            #     conn.rollback()
            raise
        except Exception as e_general:
            logger.error(f"General error in execute_update: {e_general}\nQuery: {query}\nParams: {params}", exc_info=True)
            # conn = g.get('db_conn', None)
            # if conn and conn.is_connected():
            #     conn.rollback()
            raise
        finally:
            if cursor:
                try:
                    cursor.close()
                except mysql.connector.Error as ce:
                     logger.error(f"Error closing cursor in execute_update: {ce}")

    # get_table_columns, get_primary_key 等方法会调用 execute_query，所以它们会自动使用新的连接管理

    def get_table_columns(self, table_name_actual):
        # ... (逻辑不变，但它调用的 execute_query 行为变了) ...
        allowed_tables = ["Users", "Friends", "Groups", "Group_Members", "Messages", "Message_Attachments"] # 保持这个列表最新
        if table_name_actual not in allowed_tables:
            raise ValueError(f"Invalid table name: {table_name_actual}")
        query = f"DESCRIBE `{table_name_actual}`"
        results = self.execute_query(query) # This will now use the request-scoped connection
        return [row['Field'] for row in results] if results else []

    def get_primary_key(self, table_name_actual):
        # ... (逻辑不变) ...
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
        # DATABASE() 在某些MySQL版本/配置中可能需要替换为实际的数据库名，或确保连接时已指定数据库
        results = self.execute_query(query, (table_name_actual,))
        return results[0]['COLUMN_NAME'] if results and results[0] else None

    # ... (其他方法类似) ...
    def get_table_data(self, table_name_actual, order_by=None, limit=None):
        allowed_tables = ["Users", "Friends", "Groups", "Group_Members", "Messages", "Message_Attachments"]
        if table_name_actual not in allowed_tables:
            raise ValueError(f"Invalid table name: {table_name_actual}")
        query = f"SELECT * FROM `{table_name_actual}`" # Ensure table name is backticked
        params = []
        # ... (rest of the logic remains the same)
        return self.execute_query(query, tuple(params) if params else None)

    def get_record_by_primary_key(self, table_name_actual, primary_key_column, record_id):
        allowed_tables = ["Users", "Friends", "Groups", "Group_Members", "Messages", "Message_Attachments"]
        if table_name_actual not in allowed_tables: raise ValueError(f"Invalid table name: {table_name_actual}")
        if not primary_key_column: return None # Or raise error
        # Basic sanitization for column name (though ideally from a known list)
        safe_pk_column = "".join(c for c in primary_key_column if c.isalnum() or c == '_')
        if not safe_pk_column: raise ValueError(f"Invalid primary key column name: {primary_key_column}")

        query = f"SELECT * FROM `{table_name_actual}` WHERE `{safe_pk_column}` = %s"
        results = self.execute_query(query, (record_id,))
        return results[0] if results else None


    def record_exists(self, table_name_actual, conditions_dict):
        allowed_tables = ["Users", "Friends", "Groups", "Group_Members", "Messages", "Message_Attachments"]
        if table_name_actual not in allowed_tables: raise ValueError(f"Invalid table name: {table_name_actual}")
        if not conditions_dict: return False

        clauses = []
        params = []
        for col_with_op, val in conditions_dict.items():
            # Basic split for column and operator, e.g., "user_id !="
            parts = col_with_op.split(maxsplit=1)
            column_name_raw = parts[0]
            operator = parts[1].strip() if len(parts) > 1 else "="

            # Sanitize column name (simple version, be cautious)
            safe_column_name = "".join(c for c in column_name_raw if c.isalnum() or c == '_')
            if not safe_column_name:
                raise ValueError(f"Invalid column name for record_exists: {column_name_raw}")

            allowed_operators = ["=", "!=", ">", "<", ">=", "<=", "LIKE", "IS NULL", "IS NOT NULL"]
            op_upper = operator.upper()
            if op_upper not in allowed_operators:
                raise ValueError(f"Invalid operator for record_exists: '{operator}'")

            if op_upper in ["IS NULL", "IS NOT NULL"]:
                clauses.append(f"`{safe_column_name}` {op_upper}")
            else:
                clauses.append(f"`{safe_column_name}` {operator} %s")
                params.append(val)

        if not clauses: return False # Should not happen if conditions_dict is not empty

        query = f"SELECT 1 FROM `{table_name_actual}` WHERE {' AND '.join(clauses)} LIMIT 1"
        result = self.execute_query(query, tuple(params) if params else None)
        return bool(result)