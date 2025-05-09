# kaguchat_app/routes/auth_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, session, make_response
import uuid
from ..extensions import chat_service, logger # 使用 .. 从父目录导入

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.before_request
def ensure_session_id_for_auth():
    # 这个 before_request 只对 auth_bp 下的路由生效
    # 如果 session_id 的逻辑是全局的，应该在 app 层面或对所有蓝图应用
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
        logger.debug(f"Generated new session_id for auth: {session['session_id']}")

@auth_bp.route('/', methods=['GET', 'POST'])
def login():
    session_id = session.get('session_id')
    logger.debug(f"Login request with session_id: {session_id}")

    if 'user_id' in session:
        return redirect(url_for('chat_bp.chat_interface', sid=session_id)) # 注意蓝图名称

    error_message = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user_id = chat_service.authenticate_user(username, password)
        if user_id:
            session['user_id'] = user_id
            session['username'] = username
            logger.debug(f"Login successful for user_id: {user_id}, session_id: {session_id}")
            resp = make_response(redirect(url_for('chat_bp.chat_interface', sid=session_id))) # 注意蓝图名称
            if not request.cookies.get('session_id'):
                resp.set_cookie('session_id', session_id, max_age=3600, samesite='Lax')
            return resp
        else:
            error_message = 'Invalid username or password'
            logger.debug(f"Login failed for username: {username}")

    rendered_page = make_response(render_template('login.html', error_message=error_message, sid=session_id))
    if not request.cookies.get('session_id') and session_id:
        rendered_page.set_cookie('session_id', session_id, max_age=3600, samesite='Lax')
    return rendered_page

@auth_bp.route('/logout')
def logout():
    session_id = session.get('session_id')
    logger.debug(f"Logout request with session_id: {session_id}")
    # current_user = session.get('username', 'Unknown user') # 可选日志
    # socketio.emit('user_logged_out', {'username': current_user}, broadcast=True) # 示例：通知其他用户有人登出

    session.clear()
    response = make_response(redirect(url_for('auth_bp.login', sid=session_id))) # 注意蓝图名称
    response.delete_cookie('session_id')
    logger.debug(f"Session cleared for session_id: {session_id}")
    return response