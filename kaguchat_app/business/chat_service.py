from ..data.db_access import DatabaseAccess
from werkzeug.security import generate_password_hash, check_password_hash

class ChatService:
    def __init__(self):
        self.db_access = DatabaseAccess()

    def get_contact_list(self, user_id):
        """获取联系人列表（基于 ContactListView）"""
        query = """
            SELECT contact_id, type, name, avatar_url, last_message, last_message_time
            FROM ContactListView
            WHERE user_id = %s
        """
        results = self.db_access.execute_query(query, (user_id,))
        # 格式化 last_message_time
        return [
            {
                'contact_id': row['contact_id'],
                'type': row['type'],
                'name': row['name'],
                'avatar_url': row['avatar_url'],
                'last_message': row['last_message'],
                'last_message_time': row['last_message_time'].strftime('%H:%M') if row['last_message_time'] else None
            } for row in results
        ]

    def get_messages(self, user_id, contact_id, contact_type):
        """获取与某个联系人的消息"""
        if contact_type == 'friend':
            query = """
                SELECT message_id, sender_id, receiver_id, group_id, content, sent_at,
                       CASE WHEN sender_id = %s THEN 1 ELSE 0 END AS is_self
                FROM Messages
                WHERE (sender_id = %s AND receiver_id = %s)
                   OR (sender_id = %s AND receiver_id = %s)
                ORDER BY sent_at ASC
            """
            params = (user_id, user_id, contact_id, contact_id, user_id)
        else:  # group
            query = """
                SELECT message_id, sender_id, receiver_id, group_id, content, sent_at,
                       CASE WHEN sender_id = %s THEN 1 ELSE 0 END AS is_self
                FROM Messages
                WHERE group_id = %s
                ORDER BY sent_at ASC
            """
            params = (user_id, contact_id)
        messages = self.db_access.execute_query(query, params)
        return [
            {
                'id': msg['message_id'],
                'sender_id': msg['sender_id'],
                'receiver_id': msg['receiver_id'],
                'group_id': msg['group_id'],
                'content': msg['content'],
                'sent_at': msg['sent_at'].strftime('%H:%M'),
                'is_self': msg['is_self']
            } for msg in messages
        ]

    def send_message(self, sender_id, receiver_id, group_id, content):
        """发送消息"""
        query = """
            INSERT INTO Messages (sender_id, receiver_id, group_id, content, message_type, sent_at)
            VALUES (%s, %s, %s, %s, 0, NOW())
        """
        params = (sender_id, receiver_id, group_id, content)
        self.db_access.execute_update(query, params)