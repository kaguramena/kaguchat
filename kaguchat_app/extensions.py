# kaguchat_app/extensions.py
from flask_socketio import SocketIO
from flask_session import Session
from flask_jwt_extended import JWTManager
from .business.chat_service import ChatService
from .business.table_service import TableService
from .business.login_service import LoginService
import logging

# 初始化 SocketIO，但不绑定 app
# app 的绑定将在 create_app 函数中完成
socketio = SocketIO(manage_session=False, cors_allowed_origins="*") # 允许所有来源的 CORS，生产环境请配置具体来源
                                                                  # manage_session=False 因为我们用了 Flask-Session
session_ext = Session()
chat_service = ChatService() # 可以在这里实例化，或者在 app context 中
table_service = TableService() 
login_service = LoginService()

logger = logging.getLogger(__name__)
jwt = JWTManager()

# 表名映射 (也可以移到这里或config.py)
TABLE_NAME_MAPPING = {
    "users": "Users",
    "friends": "Friends",
    "groups": "Groups",
    "group_members": "Group_Members",
    "messages": "Messages",
    "message_attachments": "Message_Attachments"
}

class ValidationError(Exception):
    """基础验证错误类，用于表单或数据验证失败。"""
    def __init__(self, message, field_name=None, error_code=None):
        super().__init__(message)
        self.message = message
        self.field_name = field_name  # 可选，指明哪个字段出错
        self.error_code = error_code  # 可选，用于更具体的错误分类

    def to_dict(self):
        data = {'message': self.message}
        if self.field_name:
            data['field_name'] = self.field_name
        if self.error_code:
            data['error_code'] = self.error_code
        return data
