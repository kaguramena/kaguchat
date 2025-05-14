# kaguchat_app/processors/users_processor.py
from werkzeug.security import generate_password_hash
from .base_processor import BaseTableProcessor
from ..extensions import table_service # 依赖注入或直接导入
from ..exceptions import InvalidDataError, DuplicateEntryError

class UsersTableProcessor(BaseTableProcessor):
    def __init__(self):
        # "Users" 是数据库中的实际表名, "users" 是 URL 和显示中使用的名称
        super().__init__(table_name_actual="Users", table_name_display="users")

    def _validate_common_user_fields(self, values, is_edit=False, record_id=None):
        username = values.get('username')
        phone = values.get('phone')

        if not is_edit and not username: # 添加时用户名必填
            raise InvalidDataError("Username is required.", field_name='username')

        if not is_edit and not values.get('password'): # 添加时密码必填
             raise InvalidDataError("Password is required for new user.", field_name='password')
        # if values.get('password') and len(values['password']) < 6: # 如果提供了密码，检查长度
        #      raise InvalidDataError("Password must be at least 6 characters long.", field_name='password')

        # if phone: # 假设 phone 是可选的，但如果提供，则验证格式
        #     if not phone.isdigit() or len(phone) != 11: # 简单示例
        #         raise InvalidDataError("Phone must be exactly 11 digits.", field_name='phone')

        # 检查唯一性约束
        if username:
            condition_username = {"username": username}
            if is_edit: # 编辑时，如果用户名是自己的，则不算重复
                condition_username[f"{self.primary_key} !="] = record_id # 假设 table_service 支持这种条件
            if table_service.record_exists("Users", condition_username):
                raise DuplicateEntryError(f"Username '{username}' already exists.", field_name='username')


    def validate_add(self, raw_values, form_data):
        super().validate_add(raw_values, form_data)
        self._validate_common_user_fields(raw_values)
        # raw_values['password'] 在这里还是明文

    def prepare_data_for_add(self, raw_values, form_data):
        """哈希密码，并准备其他字段。"""
        prepared = raw_values.copy()
        if prepared.get('password'):
            prepared['password'] = generate_password_hash(prepared['password'])
        else:
            # validate_add 应该已经捕获了密码为空的情况
            # 如果出于某种原因密码仍然是 None 或空，这里可以抛出错误或设置默认（不推荐）
            raise InvalidDataError("Password hashing failed: password was not provided.")

        # 确保 avatar_url, created_at 等其他字段被正确处理
        # BaseTableProcessor._extract_values_from_form 已经将空字符串转为 None
        # 如果有默认值逻辑，可以在这里添加
        return prepared

    def validate_edit(self, record_id, raw_values_from_form, current_record_dict, form_data):
        super().validate_edit(record_id, raw_values_from_form, current_record_dict, form_data)
        self._validate_common_user_fields(raw_values_from_form, is_edit=True, record_id=record_id)
        # raw_values_from_form['password'] 在这里还是明文 (如果用户输入了的话)

    def prepare_data_for_edit(self, record_id, raw_values_from_form, current_record_dict, form_data):
        """如果提供了新密码，则哈希它。只返回需要更新的字段。"""
        update_payload = {}
        for key, new_value in raw_values_from_form.items():
            current_db_value = current_record_dict.get(key)

            if key == 'password':
                if new_value: # 用户输入了新密码
                    hashed_new_password = generate_password_hash(new_value)
                    # 只有当新哈希与旧哈希不同时才更新 (虽然通常直接更新也可以)
                    # Werkzeug 的 check_password_hash 不能用来比较两个哈希，所以直接更新
                    update_payload[key] = hashed_new_password
                # else: 密码为空，表示不修改密码，所以不加入 update_payload
            elif str(new_value or '') != str(current_db_value or ''):
                 update_payload[key] = new_value # 其他字段，如果改变了就加入更新列表

        return update_payload

    def get_display_columns(self):
        """从admin视图中排除密码列的直接显示。"""
        cols = super().get_display_columns()
        return [col for col in cols if col != 'password']

    def get_form_fields_edit(self, record):
        """编辑表单中，密码字段可以留空表示不修改。"""
        fields = super().get_form_fields_edit(record)
        # 可以根据需要进一步定制编辑表单字段
        return fields