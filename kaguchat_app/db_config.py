# db_config.py
import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    'host': 'localhost',
    'user': 'db_admin',       # 替换为您的数据库用户名
    'password': 'Db$789101112', # 替换为您的数据库密码
    'database': 'kaguchat',     # 替换为您的数据库名
    'charset': 'utf8mb4'
}


def get_db_connection():
    try:
        connection = mysql.connector.connect(
            **DB_CONFIG
        )
        if connection.is_connected():
            print("Successfully connected to MySQL database")
            return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None