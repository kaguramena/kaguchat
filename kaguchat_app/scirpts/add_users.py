import json
import os
import sys
import datetime
from werkzeug.security import generate_password_hash

current_script_path = os.path.abspath(__file__)
scripts_dir = os.path.dirname(current_script_path)
kaguchat_app_dir = os.path.dirname(scripts_dir)
project_root = os.path.dirname(kaguchat_app_dir)

if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from kaguchat_app.data.db_access import DatabaseAccess
except ModuleNotFoundError as e:
    print(f"Error: {e}. Please ensure the script is run from the correct directory.")
    sys.exit(1)
except Exception as e:
    print(f"Unexpected error: {e}")
    sys.exit(1)

DEFAULT_JSON_FILE_PATHS = os.path.join(current_script_path,"user_data.json")

def batch_add_users_from_json(json_file_path=DEFAULT_JSON_FILE_PATHS):
    db = None
    successful_inserts = 0
    failed_inserts = 0

    try:
        db = DatabaseAccess()
        if not db.connection:
            print("Failed to connect to the database.")
            return
        with open(json_file_path, 'r', encoding='utf-8') as file:
            users_data = json.load(file)
        
        for user_data in users_data:
            username = user_data.get("username")
            email = user_data.get("email")
            plain_password = user_data.get("password")
            phone = user_data.get("phone") # 会是 None 如果键不存在或值为 null
            avatar_url = user_data.get("avatar_url") # 会是 None 如果键不存在或值为 null

            hashed_password = generate_password_hash(plain_password)
            insert_data = {
                "username": username,
                "email": email,
                "password": hashed_password,
                "phone": phone, # 如果数据库允许 NULL，None 会被正确处理
                "avatar_url": avatar_url, # 同上
                # 添加 Users 表中其他必要的字段（如果它们没有默认值且非空）
            }

            columns = []
            values_tuple = []
            for col_name, col_val in insert_data.items():
                columns.append(col_name)
                values_tuple.append(col_val)
            sql_columns_str = ", ".join(columns)
            placeholders = ", ".join(["%s"] * len(columns))
            query = f"INSERT INTO Users ({sql_columns_str}) VALUES ({placeholders})"
            params = tuple(values_tuple)
            try:
                db.execute_update(query, params)
                successful_inserts += 1
            except Exception as e:
                print(f"Failed to insert user {username}: {e}")
                failed_inserts += 1
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    batch_add_users_from_json()