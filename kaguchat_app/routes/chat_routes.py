# kaguchat_app/routes/chat_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, session, make_response
from ..extensions import chat_service, logger, socketio # 导入 socketio

chat_bp = Blueprint('chat_bp', __name__)

# @chat_bp.before_request # 如果有针对此蓝图的特定逻辑
# def before_chat_request():
#     pass

@chat_bp.route('/chat', methods=['GET'])
def chat_interface(): # 重命名函数以避免与可能的 'chat' 模块冲突
    session_id = session.get('session_id')
    logger.debug(f"Chat interface request with session_id: {session_id}, session: {session}")

    if 'user_id' not in session:
        logger.debug("No valid session for chat, redirecting to login")
        login_url = url_for('auth_bp.login') # 使用蓝图名称
        if session_id:
            login_url = url_for('auth_bp.login', sid=session_id)
        return redirect(login_url)

    user_id = session['user_id']
    username = session['username']
    logger.debug(f"Chat interface loaded for user_id: {user_id}, session_id: {session_id}")

    contacts = chat_service.get_contact_list(user_id)
    selected_contact_id = request.args.get('contact_id')
    selected_contact_type = request.args.get('contact_type')

    if not selected_contact_id and contacts:
        selected_contact_id = str(contacts[0]['contact_id'])
        selected_contact_type = contacts[0]['type']

    messages = []
    if selected_contact_id and selected_contact_type:
        messages = chat_service.get_messages(user_id, int(selected_contact_id), selected_contact_type)

    rendered_chat = make_response(render_template('chat.html', username=username, contacts=contacts, messages=messages,
                               selected_contact_id=selected_contact_id, selected_contact_type=selected_contact_type,
                               sid=session_id, user_id=user_id))
    if not request.cookies.get('session_id') and session_id:
        rendered_chat.set_cookie('session_id', session_id, max_age=3600, samesite='Lax')
    return rendered_chat