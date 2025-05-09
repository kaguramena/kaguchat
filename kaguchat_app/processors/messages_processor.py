# kaguchat_app/processors/messages_processor.py
from .base_processor import BaseTableProcessor
from ..extensions import table_service
from ..exceptions import InvalidDataError, PermissionDeniedError

class MessagesTableProcessor(BaseTableProcessor):
    def __init__(self):
        super().__init__(table_name_actual="Messages", table_name_display="messages")

    def validate_add(self, raw_values, form_data):
        super().validate_add(raw_values, form_data)
        content = raw_values.get('content')
        sender_id = raw_values.get('sender_id')
        receiver_id = raw_values.get('receiver_id')
        group_id = raw_values.get('group_id')

        if not content:
            raise InvalidDataError("Message content cannot be empty.", field_name='content')
        if not sender_id: # 假设 sender_id 是从 select 来的，已经是 user_id
            raise InvalidDataError("Sender ID is required.", field_name='sender_id')
        if not receiver_id and not group_id: # 私聊或群聊必须有一个
            raise InvalidDataError("Either Receiver ID or Group ID must be provided.", field_name='receiver_id')

        # 进一步验证: sender_id, receiver_id, group_id 是否存在于各自的表中
        if sender_id and not table_service.record_exists("Users", { "user_id": sender_id }):
            raise InvalidDataError(f"Sender with ID '{sender_id}' does not exist.", field_name='sender_id')
        if receiver_id and not table_service.record_exists("Users", { "user_id": receiver_id }):
            raise InvalidDataError(f"Receiver with ID '{receiver_id}' does not exist.", field_name='receiver_id')
        if group_id and not table_service.record_exists("Groups", { "group_id": group_id }):
            raise InvalidDataError(f"Group with ID '{group_id}' does not exist.", field_name='group_id')

    def prepare_data_for_add(self, raw_values, form_data):
        prepared = raw_values.copy()
        # 确保 message_type 有默认值，如果表单没提供的话
        if 'message_type' not in prepared or prepared['message_type'] is None:
            prepared['message_type'] = 0 # 例如，0 代表文本消息
        # sent_at 通常由数据库的 NOW() 或 DEFAULT CURRENT_TIMESTAMP 处理，不需要在这里设置
        return prepared

    # 对于 Messages 表，编辑和删除可能通常不被允许或有非常严格的规则
    # 这里可以覆盖 validate_edit, prepare_data_for_edit, validate_delete 来禁止或限制操作

    def validate_edit(self, record_id, raw_values_from_form, current_record_dict, form_data):
        raise PermissionDeniedError("Messages cannot be edited directly through this interface.")

    def validate_delete(self, record_id, current_record_dict):
        # 可以添加逻辑，例如只允许特定角色的用户删除，或者只允许删除自己的消息（如果适用）
        # super().validate_delete(record_id, current_record_dict)
        pass # 示例：暂时允许删除