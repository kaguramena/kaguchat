from data.db_access import DatabaseAccess

class ChatService:
    def __init__(self):
        self.db_access = DatabaseAccess()

    def authenticate_user(self, username, password):
        """验证用户登录"""
        query = "SELECT user_id FROM Users WHERE username = %s AND password = %s"
        result = self.db_access.execute_query(query, (username, password))
        return result[0][0] if result else None

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
                'contact_id': row[0],
                'type': row[1],
                'name': row[2],
                'avatar_url': row[3],
                'last_message': row[4],
                'last_message_time': row[5].strftime('%H:%M') if row[5] else None
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
                'id': msg[0],
                'sender_id': msg[1],
                'receiver_id': msg[2],
                'group_id': msg[3],
                'content': msg[4],
                'sent_at': msg[5].strftime('%H:%M'),
                'is_self': msg[6]
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