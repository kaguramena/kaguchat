# db_config.py
import mysql.connector
from mysql.connector import Error

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",  # 开发阶段：localhost；生产阶段：数据库服务器 IP
            user="db_admin",
            password="Db$789101112",
            database="kaguchat"
        )
        if connection.is_connected():
            print("Successfully connected to MySQL database")
            return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None