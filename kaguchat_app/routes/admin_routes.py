# kaguchat_app/routes/admin_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, session
from ..extensions import table_service, logger, TABLE_NAME_MAPPING
from werkzeug.security import generate_password_hash # 用于密码哈希处理

admin_bp = Blueprint('admin_bp', __name__, url_prefix='/admin') # 给蓝图加URL前缀

@admin_bp.route('/<table_name>', methods=['GET', 'POST'])
def manage_table(table_name):
    session_id = session.get('session_id') # 确保 sid 仍然可用
    logger.debug(f"Manage table request with session_id: {session_id}")
    if 'user_id' not in session: # 简单的权限检查，后续可以改进
        logger.debug("No valid session for admin, redirecting to login")
        login_url = url_for('auth_bp.login') # 使用蓝图名称
        if session_id:
            login_url = url_for('auth_bp.login', sid=session_id)
        return redirect(login_url)

    # 可以在这里加入更严格的权限检查，例如检查 user_id 是否为管理员
    # if session['user_id'] not in ADMIN_USER_IDS:
    #     return "Access Denied", 403

    actual_table_name = TABLE_NAME_MAPPING.get(table_name.lower())
    if not actual_table_name:
        return render_template('table_view.html', table_name=table_name, columns=[], data=[],
                             primary_key=None, error_message="Invalid table name", sid=session_id)

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
                    if col != primary_key and col != datetime_field: # 排除主键和自动日期时间字段
                        value = request.form.get(col, '')
                        
                        # 对于 users 表的 password 字段，应该进行哈希处理
                        if actual_table_name == "Users" and col == "password":
                            value = generate_password_hash(value) # 需要导入werkzeug.security

                        values[col] = None if (value == '' or value.isspace()) else value
                table_service.add_record(actual_table_name, values)
                return redirect(url_for('admin_bp.manage_table', table_name=table_name, sid=session_id))

            elif action == 'edit':
                record_id = request.form.get('record_id')
                values = {}
                for col in columns:
                    if col != primary_key and col != datetime_field: # 排除主键和自动日期时间字段
                        value = request.form.get(f"{col}_{record_id}", '')
                        # if actual_table_name == "Users" and col == "password" and value: # 仅当密码字段有值时更新
                        #     value = generate_password_hash(value)
                        # elif actual_table_name == "Users" and col == "password" and not value:
                        #     continue # 如果密码为空，则不更新密码
                        values[col] = None if (value == '' or value.isspace()) else value
                if values: # 只有当有值需要更新时才执行
                    table_service.update_record(actual_table_name, primary_key, record_id, values)
                return redirect(url_for('admin_bp.manage_table', table_name=table_name, sid=session_id))

            elif action == 'delete':
                record_id = request.form.get('record_id')
                table_service.delete_record(actual_table_name, primary_key, record_id)
                return redirect(url_for('admin_bp.manage_table', table_name=table_name, sid=session_id))

    except Exception as e:
        error_message = str(e)
        logger.error(f"Error managing table {actual_table_name}: {e}")


    return render_template('table_view.html', table_name=table_name, columns=columns, data=data,
                         primary_key=primary_key, error_message=error_message, sid=session_id)