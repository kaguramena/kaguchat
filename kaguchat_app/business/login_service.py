from ..data.db_access import DatabaseAccess
from werkzeug.security import generate_password_hash, check_password_hash

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