from flask import Flask, render_template, request, redirect, url_for, session, make_response
from business.chat_service import ChatService
from business.table_service import TableService
from flask_session import Session
from redis import Redis
import uuid
import logging

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'wyt153hh'  # 确保是安全的随机字符串

# 配置 Redis 作为会话存储
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = Redis(host='localhost', port=6379, db=0)
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
Session(app)

chat_service = ChatService()
table_service = TableService()

# 表名映射
TABLE_NAME_MAPPING = {
    "users": "Users",
    "friends": "Friends",
    "groups": "Groups",
    "group_members": "Group_Members",
    "messages": "Messages",
    "message_attachments": "Message_Attachments"
}

# 每次请求检查或生成唯一的 session_id
@app.before_request
def ensure_session_id():
    # 从查询参数或 Cookie 中获取 session_id
    session_id = request.args.get('sid') or request.cookies.get('session_id')
    if not session_id:
        session_id = str(uuid.uuid4())
        logger.debug(f"Generated new session_id: {session_id}")
    
    # 将 session_id 存储到 session 中
    if 'session_id' not in session or session['session_id'] != session_id:
        session['session_id'] = session_id
    
    # 如果是新生成的 session_id，设置到 Cookie 中
    if 'session_id' not in request.cookies:
        response = make_response()
        response.set_cookie('session_id', session_id, max_age=3600, samesite='lax')
        logger.debug(f"Set session_id Cookie: {session_id}")

# 聊天功能路由
@app.route('/', methods=['GET', 'POST'])
def login():
    session_id = session.get('session_id')
    logger.debug(f"Login request with session_id: {session_id}")
    
    # 如果已经登录，直接跳转到 chat
    if 'user_id' in session:
        return redirect(url_for('chat', sid=session_id))
    
    error_message = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user_id = chat_service.authenticate_user(username, password)
        if user_id:
            session['user_id'] = user_id
            session['username'] = username
            logger.debug(f"Login successful for user_id: {user_id}, session_id: {session_id}")
            return redirect(url_for('chat', sid=session_id))
        else:
            error_message = 'Invalid username or password'
            logger.debug(f"Login failed for username: {username}")
    
    return render_template('login.html', error_message=error_message)

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    session_id = session.get('session_id')
    logger.debug(f"Chat request with session_id: {session_id}, session: {session}")
    
    if 'user_id' not in session:
        logger.debug("No valid session, redirecting to login")
        return redirect(url_for('login', sid=session_id))
    
    user_id = session['user_id']
    username = session['username']
    logger.debug(f"Chat loaded for user_id: {user_id}, session_id: {session_id}")
    
    # 获取联系人列表
    contacts = chat_service.get_contact_list(user_id)
    
    # 默认选中第一个联系人，如果 contacts 为空则使用 None
    selected_contact_id = request.args.get('contact_id')
    selected_contact_type = request.args.get('contact_type')
    if not selected_contact_id and contacts:
        selected_contact_id = str(contacts[0]['contact_id'])
        selected_contact_type = contacts[0]['type']
    
    # 获取消息
    messages = []
    if selected_contact_id and selected_contact_type:
        messages = chat_service.get_messages(user_id, int(selected_contact_id), selected_contact_type)
    
    # 发送消息
    if request.method == 'POST':
        content = request.form.get('message_content')
        if content:
            receiver_id = int(selected_contact_id) if selected_contact_type == 'friend' else None
            group_id = int(selected_contact_id) if selected_contact_type == 'group' else None
            chat_service.send_message(user_id, receiver_id, group_id, content)
            return redirect(url_for('chat', contact_id=selected_contact_id, contact_type=selected_contact_type, sid=session_id))
    
    return render_template('chat.html', username=username, contacts=contacts, messages=messages, 
                         selected_contact_id=selected_contact_id, selected_contact_type=selected_contact_type, sid=session_id)

@app.route('/logout')
def logout():
    session_id = session.get('session_id')
    logger.debug(f"Logout request with session_id: {session_id}")
    session.clear()
    response = make_response(redirect(url_for('login', sid=session_id)))
    response.delete_cookie('session_id')
    logger.debug(f"Session cleared for session_id: {session_id}")
    return response

# 后台管理路由
@app.route('/admin/<table_name>', methods=['GET', 'POST'])
def manage_table(table_name):
    session_id = session.get('session_id')
    logger.debug(f"Manage table request with session_id: {session_id}")
    if 'user_id' not in session:
        logger.debug("No valid session, redirecting to login")
        return redirect(url_for('login', sid=session_id))
    
    actual_table_name = TABLE_NAME_MAPPING.get(table_name.lower())
    if not actual_table_name:
        return render_template('table_view.html', table_name=table_name, columns=[], data=[], 
                             primary_key=None, error_message="Invalid table name")

    columns = []
    primary_key = None
    data = []
    error_message = None

    try:
        columns = table_service.get_table_columns(actual_table_name)
        primary_key = table_service.get_primary_key(actual_table_name)
        data = table_service.get_table_data(actual_table_name)

        auto_datetime_fields = {
            "users": "created_at",
            "friends": "created_at",
            "groups": "created_at",
            "group_members": "join_at",
            "messages": "sent_at",
            "message_attachments": "uploaded_at"
        }
        datetime_field = auto_datetime_fields.get(table_name.lower())

        if request.method == 'POST':
            action = request.form.get('action')

            if action == 'add':
                values = {}
                for col in columns:
                    if col != primary_key and col != datetime_field:
                        value = request.form.get(col, '')
                        values[col] = None if (value == '' or value.isspace()) else value
                table_service.add_record(actual_table_name, values)
                return redirect(url_for('manage_table', table_name=table_name, sid=session_id))

            elif action == 'edit':
                record_id = request.form.get('record_id')
                values = {}
                for col in columns:
                    if col != primary_key and col != datetime_field:
                        value = request.form.get(f"{col}_{record_id}", '')
                        values[col] = None if (value == '' or value.isspace()) else value
                table_service.update_record(actual_table_name, primary_key, record_id, values)
                return redirect(url_for('manage_table', table_name=table_name, sid=session_id))

            elif action == 'delete':
                record_id = request.form.get('record_id')
                table_service.delete_record(actual_table_name, primary_key, record_id)
                return redirect(url_for('manage_table', table_name=table_name, sid=session_id))

    except Exception as e:
        error_message = str(e)

    return render_template('table_view.html', table_name=table_name, columns=columns, data=data, 
                         primary_key=primary_key, error_message=error_message)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)