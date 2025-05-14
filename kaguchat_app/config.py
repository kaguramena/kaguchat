# kaguchat_app/config.py
from datetime import timedelta
import os
from redis import Redis

class Config:
    TABLE_NAME_MAPPING_FOR_ADMIN = {
        "users": "Users",
        "friends": "Friends",
        "groups": "Groups",
        "group_members": "Group Members",
        "messages": "Messages",
        "message_attachments": "Message Attachments"
    }

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'wyt153hh-default-secret-key' # 建议从环境变量读取

    # Redis Session 配置
    SESSION_TYPE = 'redis'
    SESSION_REDIS = Redis(host='localhost', port=6379, db=0)
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SESSION_KEY_PREFIX = 'kaguchat:session:' # 可选，但推荐

    # JWT 配置
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'your-jwt-secret-key-for-development' # 必须设置
    JWT_TOKEN_LOCATION = ['headers', 'cookies'] # (可选) 定义 Token 的位置
    JWT_COOKIE_SECURE = False # 开发时设为 False, 生产环境HTTPS应为True
    JWT_COOKIE_SAMESITE = "Lax"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1) # (可选) Token 过期时间
    JWT_CSRF_METHODS = ['POST', 'PUT', 'PATCH', 'DELETE'] # <--- 这是关键修改
    JWT_CSRF_IN_COOKIES = False
    
    # 其他应用配置可以放在这里
    DEBUG = True # 开发时设为True，生产环境设为False
    LOG_LEVEL = 'DEBUG'

    # 用户头像配置
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static/avatars')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'} # 允许的图片类型
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 可选：限制上传文件大小，例如16MB

# 可以根据需要创建不同的配置类，例如 DevelopmentConfig, ProductionConfig
class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
    LOG_LEVEL = 'INFO'
    # 生产环境中 SECRET_KEY 必须从环境变量获取
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        SECRET_KEY = 'a-different-default-production-key-that-is-still-not-ideal'
        # raise ValueError("No SECRET_KEY set for production")

# 选择一个配置
# current_config = DevelopmentConfig
current_config = Config # 简单起见，我们先用基础 Config