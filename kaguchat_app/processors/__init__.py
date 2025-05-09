# kaguchat_app/processors/__init__.py
from ..extensions import TABLE_NAME_MAPPING # 实际表名到显示名的映射
from .users_processor import UsersTableProcessor
from .messages_processor import MessagesTableProcessor
from .groups_processor import GroupsTableProcessor
from .friends_processor import FriendsTableProcessor
# 为其他表导入相应的处理器
# from .friends_processor import FriendsTableProcessor
# from .groups_processor import GroupsTableProcessor
# ...

# 映射显示名 (URL中的table_name) 到处理器类
# 注意键是小写的显示名
PROCESSOR_CLASSES = {
    "users": UsersTableProcessor,
    "messages": MessagesTableProcessor,
    "friends": FriendsTableProcessor,
    "groups": GroupsTableProcessor,
}

# 也可以创建一个通用的处理器，用于那些没有特定逻辑的表
from .base_processor import BaseTableProcessor

class GenericTableProcessor(BaseTableProcessor):
    """一个通用的处理器，用于没有特殊逻辑的表。"""
    def __init__(self, table_name_actual, table_name_display):
        super().__init__(table_name_actual, table_name_display)
    # 它将使用 BaseTableProcessor 的默认验证和准备方法


def get_table_processor(table_name_display_url):
    """
    工厂函数，根据URL中的表名显示名获取相应的表处理器实例。
    """
    table_name_key = table_name_display_url.lower()

    processor_class = PROCESSOR_CLASSES.get(table_name_key)

    if processor_class:
        return processor_class() # 实例化特定的处理器

    # 如果没有找到特定处理器，尝试查找实际表名并使用通用处理器
    # TABLE_NAME_MAPPING 的键是小写的显示名，值是数据库实际表名
    actual_table_name = TABLE_NAME_MAPPING.get(table_name_key)
    if actual_table_name:
        # print(f"No specific processor for '{table_name_key}', using GenericTableProcessor for actual table '{actual_table_name}'.")
        return GenericTableProcessor(actual_table_name, table_name_key)

    # 如果连实际表名都找不到，则该表不受支持
    print(f"Warning: No processor or actual table name found for display name '{table_name_key}'.")
    return None