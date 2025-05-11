# kaguchat_app/__init__.py
from flask import Flask, session as flask_session, request, make_response # 重命名 session 防止冲突
import logging
import uuid
from .config import current_config # 使用 . 从当前包导入
from .extensions import socketio, session_ext, jwt, chat_service, table_service, logger
from .socket_events import register_socketio_events
from .processors import get_table_processor as get_processor_func
from flask_cors import CORS

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

    # 全局的 before_request 处理器，如果需要
    @app.before_request
    def ensure_global_session_id():
        # 确保 session_id 在每个请求（HTTP 和潜在的 SocketIO 初始握手）中都存在
        # SocketIO 的 session 是基于 HTTP session 的，所以这里设置的会影响 SocketIO
        # 注意：对于纯 SocketIO 事件，request.cookies 可能不可用，依赖 flask.session
        if 'session_id' not in flask_session: # 使用导入的 flask_session
            flask_session['session_id'] = str(uuid.uuid4())
            logger.debug(f"Generated new global session_id: {flask_session['session_id']}")

        # 对于 HTTP 请求，确保 cookie 也被设置
        # 这是一个棘手的地方，因为 before_request 不能直接返回 response 来设置 cookie
        # 通常在 after_request 中处理，或者在每个返回 response 的视图函数中处理
        # 我们在各个视图函数返回 response 前检查并设置 cookie

    @app.after_request
    def set_session_cookie(response):
        # 确保 session_id cookie 在响应中被设置，如果它在 session 中但不在 cookie 中
        if 'session_id' in flask_session and 'session_id' not in request.cookies:
            if hasattr(response, 'set_cookie'): # 确保是 Flask Response 对象
                 response.set_cookie('session_id', flask_session['session_id'], max_age=3600, samesite='Lax')
                 logger.debug(f"Set session_id cookie in after_request: {flask_session['session_id']}")
        return response
    
    @app.context_processor
    def inject_utilities():
        # 这个函数会在每个请求的模板渲染之前执行
        # 它返回一个字典，字典中的键值对会成为模板中的全局变量
        # 'get_processor' 是模板中使用的名字
        # get_processor_func 是我们导入的实际 Python 函数
        # 'config' 变量指向 app.config 对象
        # app.logger.debug("Injecting utilities: get_processor and config into template context.") # 调试日志
        return dict(get_processor=get_processor_func, config=app.config)


    # 注册蓝图
    from .routes.auth_routes import auth_bp
    from .routes.chat_routes import chat_bp
    from .routes.admin_routes import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(admin_bp)

    # 注册 SocketIO 事件 (从 socket_events.py)
    register_socketio_events(socketio)

    logger.info("Flask App created and configured.")
    return app