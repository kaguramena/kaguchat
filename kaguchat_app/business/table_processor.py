# kaguchat_app/business/table_processors.py
from abc import ABC, abstractmethod
from werkzeug.security import generate_password_hash
from ..extensions import table_service # 假设 table_service 包含底层的DB操作方法
from ..exceptions import ValidationError, DuplicateEntryError, InvalidDataError # 自定义异常

class BaseTableProcessor(ABC):
    def __init__(self, table_name_actual, table_name_display):
        self.table_name_actual = table_name_actual # 数据库中的实际表名
        self.table_name_display = table_name_display # 用于显示的表名 (如 users)
        self.columns = table_service.get_table_columns(self.table_name_actual)
        self.primary_key = table_service.get_primary_key(self.table_name_actual)
        self.datetime_fields = self._get_auto_datetime_fields()

    def _get_auto_datetime_fields(self):
        # 这个可以从一个配置中获取，或者在这里硬编码
        auto_fields = {
            "Users": ["created_at", "updated_at"], # 假设 Users 表有 updated_at
            "Friends": ["created_at"],
            "Groups": ["created_at"],
            "Group_Members": ["join_at"],
            "Messages": ["sent_at"],
            "Message_Attachments": ["uploaded_at"]
        }
        return auto_fields.get(self.table_name_actual, [])

    def get_columns(self):
        return self.columns

    def get_primary_key(self):
        return self.primary_key

    def get_data(self):
        return table_service.get_table_data(self.table_name_actual)

    def _prepare_common_values(self, form_data):
        """通用值准备，排除主键和自动日期时间字段"""
        values = {}
        for col in self.columns:
            if col != self.primary_key and col not in self.datetime_fields:
                value = form_data.get(col, '')
                values[col] = None if (value == '' or value.isspace()) else value
        return values

    def process_add(self, form_data):
        """处理添加记录的通用流程"""
        values = self._prepare_common_values(form_data)
        self.validate_add(values) # 调用特定验证
        # 调用特定于表的预处理数据 (例如哈希密码)
        processed_values = self.prepare_data_for_add(values.copy()) # 传递副本以防修改影响其他逻辑
        return table_service.add_record(self.table_name_actual, processed_values)

    def process_edit(self, record_id, form_data_prefixed):
        """处理编辑记录的通用流程"""
        # form_data_prefixed 的键可能是 col_recordid，需要解析
        values = {}
        for col in self.columns:
            if col != self.primary_key and col not in self.datetime_fields:
                # 从 form_data_prefixed 中提取正确的字段值
                # request.form.get(f"{col}_{record_id}", '')
                value = form_data_prefixed.get(f"{col}_{record_id}", '') # 假设 admin_routes 已经这样传递
                values[col] = None if (value == '' or value.isspace()) else value

        self.validate_edit(record_id, values) # 调用特定验证
        processed_values = self.prepare_data_for_edit(record_id, values.copy())

        if processed_values: # 只有当有值需要更新时才执行
            return table_service.update_record(self.table_name_actual, self.primary_key, record_id, processed_values)
        return True # 如果没有需要更新的字段，也视为成功

    def process_delete(self, record_id):
        """处理删除记录的通用流程"""
        self.validate_delete(record_id)
        return table_service.delete_record(self.table_name_actual, self.primary_key, record_id)

    # ---- 需要子类根据需求覆盖的方法 ----
    def validate_add(self, values):
        """在添加前验证数据。如果无效则抛出 ValidationError 或其子类。"""
        # 默认无额外验证
        pass

    def prepare_data_for_add(self, values):
        """在添加到数据库前准备/转换数据 (例如哈希密码)。"""
        # 默认不处理
        return values

    def validate_edit(self, record_id, values):
        """在编辑前验证数据。"""
        # 默认无额外验证
        pass

    def prepare_data_for_edit(self, record_id, values):
        """在更新到数据库前准备/转换数据。"""
        # 默认不处理
        return values

    def validate_delete(self, record_id):
        """在删除前验证 (例如，检查是否有依赖关系不允许删除)。"""
        # 默认无额外验证
        pass


class UsersTableProcessor(BaseTableProcessor):
    def __init__(self):
        super().__init__("Users", "users") # 实际表名 "Users", 显示名 "users"

    def validate_add(self, values):
        super().validate_add(values)
        username = values.get('username')
        email = values.get('email')
        password = values.get('password') # 这里是明文密码，将在 prepare_data_for_add 中哈希

        if not username:
            raise InvalidDataError("Username is required.", field_name='username')
        if not password: # 确保明文密码在验证阶段存在
            raise InvalidDataError("Password is required for new user.", field_name='password')
        if not email: # 简单示例
            raise InvalidDataError("Email is required.", field_name='email')

        # 检查用户名或邮箱是否已存在 (需要 table_service 支持)
        if table_service.record_exists("Users", {"username": username}):
            raise DuplicateEntryError(f"Username '{username}' already exists.", field_name='username')
        if table_service.record_exists("Users", {"email": email}): # 假设有 record_exists 方法
            raise DuplicateEntryError(f"Email '{email}' already exists.", field_name='email')
        # 其他验证，如密码复杂度、邮箱格式等

    def prepare_data_for_add(self, values):
        """哈希密码"""
        if 'password' in values and values['password']: # 确保密码字段存在且不为空
            values['password'] = generate_password_hash(values['password'])
        else:
            # 如果验证阶段允许密码为空（不推荐用于添加），这里要处理
            # 或者在 validate_add 中就已抛出错误
            pass
        return values

    def validate_edit(self, record_id, values):
        super().validate_edit(record_id, values)
        # 编辑时可以允许密码为空 (表示不修改)
        # 其他验证，例如不能修改自己的用户名等 (如果需要)
        email = values.get('email')
        if email:
            # 检查邮箱是否已存在 (且不是当前用户自己的)
            existing_user = table_service.get_record_by_field("Users", "email", email)
            if existing_user and str(existing_user.get(self.primary_key)) != str(record_id): # 假设 get_record_by_field 返回字典或对象
                raise DuplicateEntryError(f"Email '{email}' is already in use by another user.", field_name='email')


    def prepare_data_for_edit(self, record_id, values):
        """如果提供了新密码，则哈希它"""
        if 'password' in values and values['password']:
            values['password'] = generate_password_hash(values['password'])
        elif 'password' in values and not values['password']:
            # 如果密码字段存在但为空字符串，表示不更新密码，从values中移除
            del values['password']
        return values

class MessagesTableProcessor(BaseTableProcessor):
    def __init__(self):
        super().__init__("Messages", "messages")

    def validate_add(self, values):
        super().validate_add(values)
        content = values.get('content')
        sender_id = values.get('sender_id')
        receiver_id = values.get('receiver_id')
        group_id = values.get('group_id')

        if not content:
            raise InvalidDataError("Message content cannot be empty.", field_name='content')
        if not sender_id:
            raise InvalidDataError("Sender ID is required.", field_name='sender_id')
        if not receiver_id and not group_id:
            raise InvalidDataError("Either Receiver ID or Group ID must be provided.", field_name='receiver_id')
        # 进一步检查 sender_id, receiver_id, group_id 是否在对应表中存在等

# 可以为其他表创建类似的处理器
# ...

# 工厂函数或字典来获取处理器实例
PROCESSOR_MAPPING = {
    "users": UsersTableProcessor,
    "messages": MessagesTableProcessor,
    # "friends": FriendsTableProcessor, # 如果有特殊逻辑
    # 如果某个表没有特殊逻辑，可以返回一个 BaseTableProcessor 实例，
    # 或者 BaseTableProcessor 本身就能处理（如果它的默认方法足够通用）
}

def get_table_processor(table_name_display):
    # table_name_display 是 URL 中的表名，如 'users'
    # 需要一个映射到实际表名和处理器类
    # 例如，从 TABLE_NAME_MAPPING (在 extensions.py 中) 获取实际表名
    from ..extensions import TABLE_NAME_MAPPING as ACTUAL_TABLE_NAMES
    actual_table_name = ACTUAL_TABLE_NAMES.get(table_name_display.lower())
    if not actual_table_name:
        return None # 或抛出异常

    processor_class = PROCESSOR_MAPPING.get(table_name_display.lower())
    if processor_class:
        return processor_class() # 实例化
    else:
        # 对于没有特定处理器的表，可以使用一个通用的 BaseTableProcessor
        # 但你需要确保 BaseTableProcessor 的方法能够处理这些表，或者调整它
        # 为了安全，如果找不到特定处理器，最好返回 None 或抛出错误，而不是默认处理
        # 或者创建一个 GenericTableProcessor(BaseTableProcessor)
        # return BaseTableProcessor(actual_table_name, table_name_display) # 示例
        print(f"No specific processor for {table_name_display}, using generic (if BaseTableProcessor is designed for it).")
        # 更好的做法是确保所有表都有一个处理器，哪怕是继承自Base且无额外逻辑的
        return None # 或者抛出 NotImplementedError