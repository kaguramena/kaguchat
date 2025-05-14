from ..data.db_access import DatabaseAccess
from werkzeug.security import generate_password_hash, check_password_hash
from ..exceptions import IntegrityError

class LoginService:
    def __init__(self):
        self.db_access = DatabaseAccess()
    
    def authenticate_user(self, username, password):
        """验证用户登录"""
        query = "SELECT user_id, password FROM Users WHERE username = %s"
        user_record = self.db_access.execute_query(query,(username,))
        if not user_record:
            return None
        
        user_id, stored_password = user_record[0]['user_id'], user_record[0]['password']
        if stored_password == password or check_password_hash(stored_password, password): #哈希密码匹配成功
            return user_id
        else:
            return None # 密码错误
        
    def get_profile(self,user_id):
        query = "SELECT user_id, username, nickname, avatar_url FROM Users WHERE user_id = %s"
        user_record = self.db_access.execute_query(query,(user_id,))
        if not user_record:
            return None
        return user_record
    
    def register_user(self, username, password, nickname, phone, avatar_url= None):
        """注册用户"""
        if not username or not password or not phone:
            return {"success": False, "error": "Username, password, and phone are required."}

        # 检查用户名或手机号是否已存在
        # 注意：这里的 self.db_access.execute_query 每次都会开关一个物理连接
        check_username_query = "SELECT user_id FROM Users WHERE username = %s"
        if self.db_access.execute_query(check_username_query, (username,)):
            return {"success": False, "error": "Username already exists."}

        check_phone_query = "SELECT user_id FROM Users WHERE phone = %s"
        if self.db_access.execute_query(check_phone_query, (phone,)):
            return {"success": False, "error": "Phone number already registered."}

        hashed_password = generate_password_hash(password)
        
        insert_query = """
            INSERT INTO Users (username, password, phone, nickname, avatar_url)
            VALUES (%s, %s, %s, %s, %s)
        """
        # 如果 nickname 或 avatar_url 为 None，数据库中对应的列需要允许 NULL
        params = (username, hashed_password, phone, nickname or username, avatar_url) # 如果nickname为空，默认用username

        try:
            # execute_update 内部的 with self 会管理连接
            new_user_id = self.db_access.execute_update(insert_query, params, fetch_id=True)
            if new_user_id:
                return {"success": True, "user_id": new_user_id}
            else:
                return {"success": False, "error": "User creation failed at database level."}
        except IntegrityError as ie: # 捕获 mysql.connector 的 IntegrityError
            # 这通常是由于唯一约束（比如 username 或 phone）再次被违反（并发情况下）
            return {"success": False, "error": "Username or phone number might already be taken (integrity error)."}
        except Exception as e:
            return {"success": False, "error": "An unexpected error occurred during registration."}
