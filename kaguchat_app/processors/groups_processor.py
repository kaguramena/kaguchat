# kaguchat_app/processors/groups_processor.py
from .base_processor import BaseTableProcessor
# from ..exceptions import InvalidDataError # 如果需要自定义验证

class GroupsTableProcessor(BaseTableProcessor):
    def __init__(self):
        # "Groups" 是数据库中的实际表名, "groups" 是 URL 和显示中使用的名称
        super().__init__(table_name_actual="Groups", table_name_display="groups")

    # 如果 Groups 表有特殊的添加验证逻辑，可以覆盖 validate_add
    # def validate_add(self, raw_values, form_data):
    #     super().validate_add(raw_values, form_data)
    #     group_name = raw_values.get('name') # 假设 Groups 表有 'name' 字段
    #     if not group_name:
    #         raise InvalidDataError("Group name cannot be empty.", field_name='name')
    #     # ... 其他验证 ...

    # 如果有特殊的数据准备逻辑
    # def prepare_data_for_add(self, raw_values, form_data):
    #     prepared = super().prepare_data_for_add(raw_values, form_data)
    #     # ... 对 prepared 进行修改 ...
    #     return prepared

    # 同样可以覆盖 validate_edit, prepare_data_for_edit, validate_delete