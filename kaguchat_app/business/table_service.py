import re
import logging
from data.db_access import DatabaseAccess

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class TableService:
    def __init__(self):
        self.db_access = DatabaseAccess()

    def get_table_columns(self, table_name):
        query = f"DESCRIBE `{table_name}`"
        columns_data = self.db_access.execute_query(query)
        return [col[0] for col in columns_data]

    def get_primary_key(self, table_name):
        query = f"SHOW KEYS FROM `{table_name}` WHERE Key_name = 'PRIMARY'"
        keys_data = self.db_access.execute_query(query)
        columns = self.get_table_columns(table_name)
        return keys_data[0][4] if keys_data else columns[0]

    def get_table_data(self, table_name):
        query = f"SELECT * FROM `{table_name}`"
        return self.db_access.execute_query(query)

    def add_record(self, table_name, values):
        logger.debug(f"Table Name: {table_name}")
        logger.debug(f"Values before processing: {values}")

        auto_datetime_fields = {
            "users": "created_at",
            "friends": "created_at",
            "groups": "created_at",
            "group_members": "join_at",
            "messages": "sent_at",
            "message_attachments": "uploaded_at"
        }
        datetime_field = auto_datetime_fields.get(table_name.lower())
        if datetime_field and datetime_field in values:
            values.pop(datetime_field)

        if table_name.lower() == "messages":
            if "receiver_id" in values and (values["receiver_id"] == "" or values["receiver_id"].isspace()):
                values["receiver_id"] = None
            if "group_id" in values and (values["group_id"] == "" or values["group_id"].isspace()):
                values["group_id"] = None

            receiver_id = values.get("receiver_id")
            group_id = values.get("group_id")
            if receiver_id is None and group_id is None:
                raise ValueError("Either Receiver ID or Group ID must be provided")
            if receiver_id is not None and group_id is not None:
                raise ValueError("Receiver ID and Group ID cannot both be provided; one must be empty")

        logger.debug(f"Values after processing: {values}")

        if table_name.lower() == "users":
            if "phone" in values and values["phone"]:
                if not re.match(r"^[0-9]{11}$", values["phone"]):
                    raise ValueError("Phone must be exactly 11 digits (e.g., 12345678901)")
            for col in ["username", "password"]:
                if col in values and not values[col]:
                    raise ValueError(f"{col} is required")

        elif table_name.lower() == "friends":
            if "status" in values and values["status"] not in ["0", "1"]:
                raise ValueError("Status must be 0 or 1")

        elif table_name.lower() == "groups":
            if "group_name" in values and not values["group_name"]:
                raise ValueError("Group Name is required")

        elif table_name.lower() == "group_members":
            if "role" in values and values["role"] not in ["0", "1", "2"]:
                raise ValueError("Role must be 0, 1, or 2")

        elif table_name.lower() == "messages":
            if "message_type" in values and values["message_type"] not in ["0", "1", "2"]:
                raise ValueError("Message Type must be 0, 1, or 2")
            if "content" in values and not values["content"]:
                raise ValueError("Content is required")

        elif table_name.lower() == "message_attachments":
            if "file_type" in values and values["file_type"] and values["file_type"] not in ["image", "file"]:
                raise ValueError("File Type must be 'image', 'file', or empty")
            if "file_url" in values and not values["file_url"]:
                raise ValueError("File URL is required")

        columns = [col for col in values.keys()]
        filtered_columns = [col for col in columns if values[col] is not None]
        filtered_values = [values[col] for col in columns if values[col] is not None]
        placeholders = ",".join(["%s"] * len(filtered_columns))
        query = f"INSERT INTO `{table_name}` ({','.join(filtered_columns)}) VALUES ({placeholders})"
        logger.debug(f"Generated SQL Query: {query}")
        self.db_access.execute_update(query, filtered_values)

    def update_record(self, table_name, primary_key, record_id, values):
        logger.debug(f"Table Name: {table_name}")
        logger.debug(f"Values before processing: {values}")

        auto_datetime_fields = {
            "users": "created_at",
            "friends": "created_at",
            "groups": "created_at",
            "group_members": "join_at",
            "messages": "sent_at",
            "message_attachments": "uploaded_at"
        }
        datetime_field = auto_datetime_fields.get(table_name.lower())
        if datetime_field and datetime_field in values:
            values.pop(datetime_field)

        if table_name.lower() == "messages":
            if "receiver_id" in values and (values["receiver_id"] == "" or values["receiver_id"].isspace()):
                values["receiver_id"] = None
            if "group_id" in values and (values["group_id"] == "" or values["group_id"].isspace()):
                values["group_id"] = None

            receiver_id = values.get("receiver_id")
            group_id = values.get("group_id")
            if receiver_id is None and group_id is None:
                raise ValueError("Either Receiver ID or Group ID must be provided")
            if receiver_id is not None and group_id is not None:
                raise ValueError("Receiver ID and Group ID cannot both be provided; one must be empty")

        logger.debug(f"Values after processing: {values}")

        if table_name.lower() == "users":
            if "phone" in values and values["phone"]:
                if not re.match(r"^[0-9]{11}$", values["phone"]):
                    raise ValueError("Phone must be exactly 11 digits (e.g., 12345678901)")
            for col in ["username", "password"]:
                if col in values and not values[col]:
                    raise ValueError(f"{col} is required")

        elif table_name.lower() == "friends":
            if "status" in values and values["status"] not in ["0", "1"]:
                raise ValueError("Status must be 0 or 1")

        elif table_name.lower() == "groups":
            if "group_name" in values and not values["group_name"]:
                raise ValueError("Group Name is required")

        elif table_name.lower() == "group_members":
            if "role" in values and values["role"] not in ["0", "1", "2"]:
                raise ValueError("Role must be 0, 1, or 2")

        elif table_name.lower() == "messages":
            if "message_type" in values and values["message_type"] not in ["0", "1", "2"]:
                raise ValueError("Message Type must be 0, 1, or 2")
            if "content" in values and not values["content"]:
                raise ValueError("Content is required")

        elif table_name.lower() == "message_attachments":
            if "file_type" in values and values["file_type"] and values["file_type"] not in ["image", "file"]:
                raise ValueError("File Type must be 'image', 'file', or empty")
            if "file_url" in values and not values["file_url"]:
                raise ValueError("File URL is required")

        filtered_columns = [col for col in values.keys() if values[col] is not None]
        filtered_values = [values[col] for col in values.keys() if values[col] is not None]
        set_clause = [f"{col} = %s" for col in filtered_columns]
        query = f"UPDATE `{table_name}` SET {','.join(set_clause)} WHERE {primary_key} = %s"
        logger.debug(f"Generated SQL Query: {query}")
        self.db_access.execute_update(query, filtered_values + [record_id])

    def delete_record(self, table_name, primary_key, record_id):
        query = f"DELETE FROM `{table_name}` WHERE {primary_key} = %s"
        self.db_access.execute_update(query, [record_id])