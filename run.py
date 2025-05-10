# kaguchat_app/run.py
import os
from kaguchat_app import create_app # 从 kaguchat_app 包导入 create_app
from kaguchat_app.extensions import socketio, logger # 导入 socketio 和 logger

# 根据环境变量选择配置，或直接指定
# config_name = os.getenv('FLASK_CONFIG') or 'default'
# app = create_app(config_name) # 如果你有不同的配置类

app = create_app()

if __name__ == '__main__':
    host = os.environ.get('FLASK_RUN_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_RUN_PORT', 5001))
    debug = app.config.get('DEBUG', True) # 从应用配置获取debug状态

    logger.info(f"Starting KaguChat server on {host}:{port} with debug={debug}")
    # 使用 socketio.run() 来启动，它会处理 Flask app 和 SocketIO 服务器
    # allow_unsafe_werkzeug=True 在 debug 模式下通常是需要的，以便 reloader 工作
    # 在生产环境中，你会用 Gunicorn + eventlet/gevent
    socketio.run(app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=debug)