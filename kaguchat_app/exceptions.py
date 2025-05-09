# kaguchat_app/exceptions.py

class ValidationError(Exception):
    """基础验证错误类，用于表单或数据验证失败。"""
    def __init__(self, message, field_name=None, error_code=None):
        super().__init__(message)
        self.message = message
        self.field_name = field_name  # 可选，指明哪个字段出错
        self.error_code = error_code  # 可选，用于更具体的错误分类

    def to_dict(self):
        data = {'message': self.message}
        if self.field_name:
            data['field_name'] = self.field_name
        if self.error_code:
            data['error_code'] = self.error_code
        return data

class DuplicateEntryError(ValidationError):
    """针对数据库中条目重复的错误。"""
    def __init__(self, message="An entry with this value already exists.", field_name=None):
        super().__init__(message, field_name=field_name, error_code="DUPLICATE_ENTRY")

class InvalidDataError(ValidationError):
    """针对数据格式或内容无效的错误。"""
    def __init__(self, message="The provided data is invalid.", field_name=None):
        super().__init__(message, field_name=field_name, error_code="INVALID_DATA")

class NotFoundError(ValidationError):
    """当期望的记录未找到时。"""
    def __init__(self, message="The requested resource was not found.", field_name=None):
        super().__init__(message, field_name=field_name, error_code="NOT_FOUND")

class IntegrityError(ValidationError):
    """针对违反数据库完整性约束的错误 (例如外键约束)。"""
    def __init__(self, message="A database integrity error occurred.", field_name=None):
        super().__init__(message, field_name=field_name, error_code="INTEGRITY_ERROR")

class PermissionDeniedError(ValidationError):
    """当用户没有权限执行操作时。"""
    def __init__(self, message="You do not have permission to perform this action."):
        super().__init__(message, error_code="PERMISSION_DENIED")

# 您可以根据需要添加更多特定的异常。