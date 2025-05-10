from flask import (
    Blueprint, render_template, request, redirect, url_for, session, flash, current_app
)
# 导入我们创建的 Table Processor 相关模块
from ..processors import get_table_processor
# 导入自定义异常
from ..exceptions import (
    ValidationError, PermissionDeniedError, NotFoundError,
    DuplicateEntryError, InvalidDataError, IntegrityError
)
# 导入日志记录器 (假设在 extensions.py 中定义了 logger)
from ..extensions import logger

# 创建 admin 蓝图，并指定模板文件夹为 'admin' (相对于 templates 目录)
admin_bp = Blueprint(
    'admin_bp',
    __name__,
    url_prefix='/admin',
    template_folder='../templates/admin' # 确保 Flask 能找到 admin 子目录下的模板
)


# 辅助函数：检查用户是否登录以及是否为管理员 (需要您自己实现具体逻辑)
def admin_required(func):
    """
    装饰器，用于保护需要管理员权限的路由。
    """
    from functools import wraps
    @wraps(func)
    def decorated_view(*args, **kwargs):
        session_id = session.get('session_id') # 用于重定向
        if 'user_id' not in session:
            flash("Please log in to access the admin area.", "warning")
            return redirect(url_for('auth_bp.login', sid=session_id))

        # TODO: 实现一个更健壮的管理员检查逻辑
        # 例如，查询 Users 表，检查当前 session['user_id'] 是否有关联的 admin 角色
        # current_user_id = session.get('user_id')
        # if not user_is_admin(current_user_id): # user_is_admin() 是您需要实现的函数
        #     flash("You do not have sufficient permissions to access this page.", "danger")
        #     return redirect(url_for('chat_bp.chat_interface', sid=session_id)) # 或重定向到其他非管理员页面

        return func(*args, **kwargs)
    return decorated_view


@admin_bp.route('/')
@admin_bp.route('/dashboard')
@admin_required # 应用权限检查装饰器
def admin_dashboard():
    """显示 Admin 后台的仪表盘/首页。"""
    session_id = session.get('session_id')
    # TABLE_NAME_MAPPING_FOR_ADMIN 应该从 app.config 获取
    # 它在 admin_base.html 中用于生成侧边栏列表
    # 这个变量会在 __init__.py 中通过 context_processor 注入模板上下文
    return render_template('admin_dashboard.html', sid=session_id)


@admin_bp.route('/manage/<table_name_display>', methods=['GET', 'POST'])
@admin_required # 应用权限检查装饰器
def manage_table(table_name_display):
    """
    通用路由，用于管理指定表的数据（显示、添加、编辑、删除）。
    <table_name_display> 是URL中使用的、用户友好的表名 (例如 "users", "messages")。
    """
    session_id = session.get('session_id')
    processor = get_table_processor(table_name_display)

    if not processor:
        flash(f"Table '{table_name_display}' is not managed or not configured correctly.", "danger")
        return redirect(url_for('admin_bp.admin_dashboard', sid=session_id))

    try:
        if request.method == 'POST':
            action = request.form.get('action')
            # 从表单中获取 record_id，这对于 edit 和 delete 是必须的
            record_id_str = request.form.get('record_id')

            if action == 'add':
                processor.process_add(request.form) # processor 内部会处理表单数据
                flash(f"Record successfully added to {processor.table_name_display.replace('_', ' ').title()}.", "success")
            
            elif action == 'edit':
                if not record_id_str:
                    flash("Record ID is missing for the edit action.", "danger")
                else:
                    # processor 的 process_edit 方法需要 record_id 和整个 request.form
                    # 因为它内部会解析形如 "fieldname_recordid" 的表单字段名
                    processor.process_edit(record_id_str, request.form)
                    flash(f"Record {record_id_str} in {processor.table_name_display.replace('_', ' ').title()} updated successfully.", "success")
            
            elif action == 'delete':
                if not record_id_str:
                    flash("Record ID is missing for the delete action.", "danger")
                else:
                    processor.process_delete(record_id_str)
                    flash(f"Record {record_id_str} from {processor.table_name_display.replace('_', ' ').title()} deleted successfully.", "success")
            else:
                flash(f"Unknown action received: {action}", "warning")

            # 操作完成后重定向回当前表的管理页面，避免表单重复提交
            return redirect(url_for('admin_bp.manage_table', table_name_display=table_name_display, sid=session_id))

    # 捕获自定义的验证错误和其他可能的异常
    except PermissionDeniedError as e:
        flash(str(e), "danger")
    except DuplicateEntryError as e:
        flash(f"Error: {str(e)} (Field: {e.field_name or 'N/A'})", "danger")
    except InvalidDataError as e:
        flash(f"Invalid data: {str(e)} (Field: {e.field_name or 'N/A'})", "danger")
    except NotFoundError as e:
        flash(str(e), "warning") # 记录未找到通常是警告级别
    except IntegrityError as e:
        flash(f"Database Integrity Error: {str(e)}. This might be due to a conflict with related data or a required field being empty.", "danger")
    except ValidationError as e: # 捕获其他未被上面特定捕获的 ValidationError
        flash(f"Validation Error: {str(e)}", "danger")
    except Exception as e:
        # 对于所有其他 Python 或数据库驱动的意外错误
        logger.error(f"Unexpected error managing table '{table_name_display}': {str(e)}", exc_info=True)
        flash("An unexpected error occurred. Please check the server logs or contact an administrator.", "danger")
        # 发生严重错误时，可以选择重定向回仪表盘，而不是尝试重新渲染可能有问题的表视图
        # return redirect(url_for('admin_bp.admin_dashboard', sid=session_id))


    # --- 为 GET 请求或 POST 发生错误后重新渲染页面准备数据 ---
    # 确保即使在 POST 失败后，页面也能用最新的数据（或尝试获取的数据）重新渲染
    try:
        columns_for_display = processor.get_display_columns()
        all_table_data = processor.get_all_data() # 这应该是字典列表
        primary_key_column = processor.primary_key
        form_fields_for_add = processor.get_form_fields_add() # 用于添加表单的字段列表
    except Exception as e_data_fetch:
        logger.error(f"Error fetching data or schema for table '{table_name_display}': {str(e_data_fetch)}", exc_info=True)
        flash(f"Could not load data or schema for table '{table_name_display}'. Displaying an empty table.", "danger")
        columns_for_display, all_table_data, primary_key_column, form_fields_for_add = [], [], None, []
        # 如果数据获取失败，可以选择重定向或显示空状态
        # return redirect(url_for('admin_bp.admin_dashboard', sid=session_id))

    return render_template(
        'table_manager.html',  # 使用新的模板文件名
        table_name=table_name_display, # URL中的显示名，用于模板中显示标题等
        actual_table_name=processor.table_name_actual, # 实际数据库表名，可能用于某些逻辑
        columns=columns_for_display, # 要在表格中显示的列名列表
        data=all_table_data, # 表数据，应该是字典列表
        primary_key=primary_key_column, # 主键列的名称
        form_fields_add=form_fields_for_add, # 用于构建“添加记录”表单的字段列表
        sid=session_id # 用于模板中生成其他链接的 sid
    )