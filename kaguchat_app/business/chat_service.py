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
                'last_message_time': row['last_message_time'].strftime('%Y-%m-%dT%H:%M:%S.%f') if row['last_message_time'] else None
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
                'sent_at': msg['sent_at'].strftime('%Y-%m-%dT%H:%M:%S.%f'),
                'is_self': msg['is_self']
            } for msg in messages
        ]

    """TODO: 目前只支持文本消息, 如需扩展需要链接 Attachment 表"""
    def send_message(self, sender_id, contact_id, contact_type, content):
        if contact_type == 'firend':
            receiver_id = contact_id
            group_id = None
        else:  # group
            receiver_id = None
            group_id = contact_id
        """发送消息"""
        query = """
            INSERT INTO Messages (sender_id, receiver_id, group_id, content, message_type, sent_at)
            VALUES (%s, %s, %s, %s, 0, NOW())
        """
        params = (sender_id, receiver_id, group_id, content)
        message_id = self.db_access.execute_update(query, params)
        return message_id

    def send_message_and_get_info(self, sender_id, contact_id, contact_type, content):
        receiver_id = None
        group_id = None
        if contact_type == 'friend':
            receiver_id = contact_id
            group_id = None
        elif contact_type == 'group':  # group
            receiver_id = None
            group_id = contact_id
        """发送消息"""
        query = """
            INSERT INTO Messages (sender_id, receiver_id, group_id, content, message_type, sent_at)
            VALUES (%s, %s, %s, %s, 0, NOW())
        """
        params = (sender_id, receiver_id, group_id, content)
        message_id = self.db_access.execute_update(query, params, fetch_id=True)
        query = """
            SELECT message_id, sender_id, receiver_id, group_id, content, sent_at
            FROM Messages
            WHERE message_id = %s
        """
        params = (message_id,)
        message = self.db_access.execute_query(query, params)
        # print(message)
        return {
            'message_id': message[0]['message_id'],
            'sender_id': message[0]['sender_id'],
            'receiver_id': message[0]['receiver_id'],
            'group_id': message[0]['group_id'],
            'content': message[0]['content'],
            'sent_at': message[0]['sent_at'].strftime('%Y-%m-%dT%H:%M:%S.%f')
        }