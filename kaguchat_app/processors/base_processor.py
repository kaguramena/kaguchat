# kaguchat_app/processors/base_processor.py
from abc import ABC, abstractmethod
from ..extensions import table_service # 依赖注入或直接导入
from ..exceptions import ValidationError, NotFoundError

class BaseTableProcessor(ABC):
    """
    表数据处理器的抽象基类。
    子类应实现特定于表的验证和数据准备逻辑。
    """
    def __init__(self, table_name_actual, table_name_display):
        if not table_name_actual or not table_name_display:
            raise ValueError("Actual table name and display name must be provided.")
        self.table_name_actual = table_name_actual
        self.table_name_display = table_name_display
        self._columns = None
        self._primary_key = None
        self._datetime_fields = self._get_auto_datetime_fields()

    @property
    def columns(self):
        if self._columns is None:
            self._columns = table_service.get_table_columns(self.table_name_actual)
        return self._columns

    @property
    def primary_key(self):
        if self._primary_key is None:
            self._primary_key = table_service.get_primary_key(self.table_name_actual)
        return self._primary_key

    def _get_auto_datetime_fields(self):
        """定义哪些字段是数据库自动管理的日期时间字段 (通常不应由用户直接编辑)。"""
        # 这个映射可以更集中地管理，例如在配置中
        auto_fields_map = {
            "Users": ["created_at", "updated_at"], # 假设 Users 表有 updated_at
            "Friends": ["created_at"],
            "Groups": ["created_at"],
            "Group_Members": ["join_at"],
            "Messages": ["sent_at"],
            "Message_Attachments": ["uploaded_at"]
        }
        return auto_fields_map.get(self.table_name_actual, [])

    def get_display_columns(self):
        """返回在 admin 界面上显示的列 (可以被子类覆盖以排除某些列)。"""
        return self.columns

    def get_form_fields_add(self):
        """返回用于“添加”表单的字段列表 (排除主键和自动日期时间字段)。"""
        return [col for col in self.columns if col != self.primary_key and col not in self._datetime_fields]

    def get_form_fields_edit(self, record):
        """返回用于“编辑”表单的字段列表 (可以根据记录内容动态调整)。"""
        return [col for col in self.columns if col != self.primary_key and col not in self._datetime_fields]


    def get_all_data(self):
        """获取表的所有数据用于显示。"""
        return table_service.get_table_data(self.table_name_actual)

    def get_record_by_id(self, record_id):
        """根据主键获取单条记录。"""
        if not self.primary_key:
            raise ValueError(f"No primary key defined for table {self.table_name_actual}")
        # table_service 需要一个 get_record 方法
        record = table_service.get_record_by_primary_key(self.table_name_actual, self.primary_key, record_id)
        if not record:
            raise NotFoundError(f"Record with ID {record_id} not found in {self.table_name_display}.")
        return record


    def _extract_values_from_form(self, form_data, fields_to_extract, record_id_for_edit=None):
        """
        从表单数据中提取指定字段的值。
        如果提供了 record_id_for_edit，则字段名会加上 _record_id 后缀。
        """
        values = {}
        for col in fields_to_extract:
            form_field_name = f"{col}_{record_id_for_edit}" if record_id_for_edit else col
            value = form_data.get(form_field_name, '').strip()
            values[col] = value if value else None # 空字符串视为 None，或根据需要处理
        return values

    def process_add(self, form_data):
        """处理添加记录的通用流程。"""
        fields_for_add = self.get_form_fields_add()
        raw_values = self._extract_values_from_form(form_data, fields_for_add)

        self.validate_add(raw_values, form_data) # 验证原始输入
        prepared_values = self.prepare_data_for_add(raw_values.copy(), form_data) # 准备数据

        return table_service.add_record(self.table_name_actual, prepared_values)

    def process_edit(self, record_id, form_data):
        """处理编辑记录的通用流程。"""
        # 首先获取当前记录，确保它存在
        current_record_dict = self.get_record_by_id(record_id) # 假设返回字典

        fields_for_edit = self.get_form_fields_edit(current_record_dict) #可以传递当前记录用于动态字段
        raw_values_from_form = self._extract_values_from_form(form_data, fields_for_edit, record_id_for_edit=record_id)

        self.validate_edit(record_id, raw_values_from_form, current_record_dict, form_data)
        prepared_values_for_update = self.prepare_data_for_edit(record_id, raw_values_from_form.copy(), current_record_dict, form_data)

        if prepared_values_for_update: # 只有当有值需要更新时才执行
            return table_service.update_record(self.table_name_actual, self.primary_key, record_id, prepared_values_for_update)
        return True # 如果没有需要更新的字段，也视为成功 (无操作)

    def process_delete(self, record_id):
        """处理删除记录的通用流程。"""
        current_record = self.get_record_by_id(record_id) # 确保记录存在
        self.validate_delete(record_id, current_record)
        return table_service.delete_record(self.table_name_actual, self.primary_key, record_id)

    # ---- 抽象或可被子类覆盖的验证和准备方法 ----
    # raw_values: 从表单提取并初步处理的字典 {column_name: value}
    # form_data: 原始的 request.form MultiDict，用于需要访问原始表单数据的情况
    # current_record_dict: (仅用于编辑/删除) 当前数据库中记录的字典表示

    def validate_add(self, raw_values, form_data):
        """
        在添加前验证数据。如果无效则抛出 ValidationError 或其子类。
        :param raw_values: 从表单提取并初步处理的字典 {column_name: value}
        :param form_data: 原始的 request.form MultiDict
        """
        pass # 默认无额外验证

    def prepare_data_for_add(self, raw_values, form_data):
        """
        在添加到数据库前准备/转换数据 (例如哈希密码, 设置默认值等)。
        应返回处理后的值字典。
        """
        return raw_values # 默认不处理

    def validate_edit(self, record_id, raw_values_from_form, current_record_dict, form_data):
        """
        在编辑前验证数据。
        :param record_id: 正在编辑的记录的主键值
        :param raw_values_from_form: 从表单提取的待更新值字典
        :param current_record_dict: 数据库中当前记录的字典
        :param form_data: 原始的 request.form MultiDict
        """
        pass # 默认无额外验证

    def prepare_data_for_edit(self, record_id, raw_values_from_form, current_record_dict, form_data):
        """
        在更新到数据库前准备/转换数据。
        应返回仅包含需要更新的字段的字典。如果返回空字典，则不执行更新。
        """
        # 默认情况下，只有当表单中的值与当前数据库中的值不同时，才包含该字段
        update_payload = {}
        for key, new_value in raw_values_from_form.items():
            # 注意: current_record_dict 的值可能是数据库类型 (如 Decimal, datetime),
            # 而 new_value 是字符串。需要合适的比较或转换。
            # 为简单起见，这里假设 current_record_dict 的值已经是可比较的类型，
            # 或者 new_value 在 _extract_values_from_form 中已做适当转换。
            # 或者，可以不比较，直接更新所有提交的字段（除非特定字段不允许修改）
            current_value = current_record_dict.get(key)
            if str(new_value or '') != str(current_value or ''): # 简单比较，注意 None 和空字符串
                 update_payload[key] = new_value
        return update_payload


    def validate_delete(self, record_id, current_record_dict):
        """
        在删除前验证 (例如，检查是否有依赖关系不允许删除)。
        :param record_id: 待删除记录的主键值
        :param current_record_dict: 数据库中当前记录的字典
        """
        pass # 默认无额外验证