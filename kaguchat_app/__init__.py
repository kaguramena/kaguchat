# kaguchat_app/__init__.py
from flask import Flask, session as flask_session, request, make_response # 重命名 session 防止冲突
import logging
import uuid
from .config import current_config # 使用 . 从当前包导入
from .extensions import socketio, session_ext, jwt, chat_service, table_service, logger
from .socket_events import register_socketio_events
from .processors import get_table_processor as get_processor_func
from flask_cors import CORS
import os

def create_app(config_object=current_config):
    app = Flask(__name__)
    app.config.from_object(config_object)

    # 初始化扩展
    session_ext.init_app(app)
    socketio.init_app(app) 
    jwt.init_app(app)

    CORS(
        app,
        resources={r"/api/*": {"origins": ["http://localhost:3000", "http://localhost:5173"]}}, # 确保列出所有可能的 React 开发服务器源
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"], # 允许的方法，OPTIONS 很重要
        allow_headers=["Content-Type", "Authorization", "X-Requested-With"], # 允许的请求头，Authorization 用于JWT
        supports_credentials=True # 如果你需要发送/接收 cookies
    )
    logger.info(f"CORS configured for origins: {app.config.get('CORS_ORIGINS', ['http://localhost:3000', 'http://localhost:5173'])} on /api/* routes")


    # 配置日志 (可以做得更细致)
    logging.basicConfig(level=app.config.get('LOG_LEVEL', 'INFO'))
    # 如果 extensions.py 中的 logger 和这里的 logger 冲突，可以重命名或只用一个
    # app.logger.handlers.extend(ext_logger.handlers) # 合并 handler
    # app.logger.setLevel(ext_logger.level)


    # 注册蓝图
    from .routes.auth_routes import auth_bp
    from .routes.chat_routes import chat_bp
    from .routes.admin_routes import admin_bp
    from .routes.user_routes import user_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(user_bp)

    # 注册 SocketIO 事件 (从 socket_events.py)
    register_socketio_events(socketio)

    # 头像上传文件夹
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
        logger.info(f"Created upload folder: {app.config['UPLOAD_FOLDER']}")

    logger.info("Flask App created and configured.")
    return app