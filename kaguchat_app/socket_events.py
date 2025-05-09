# kaguchat_app/socket_events.py
from flask import session, request
from flask_socketio import emit, join_room, leave_room
from .extensions import socketio, chat_service, logger # 使用 . 从当前包导入
from datetime import datetime

# 这个函数将在 __init__.py 中被调用来注册事件处理器
def register_socketio_events(socketio_instance):

    @socketio_instance.on('connect')
    def handle_connect():
        user_id = session.get('user_id')
        if not user_id:
            logger.warning(f"SocketIO connection attempt without user_id. SID: {request.sid}")
            return False # 拒绝连接
        logger.info(f"Client connected: {request.sid}, user_id: {user_id}")
        join_room(str(user_id)) # 加入以用户ID命名的房间，用于可能的私信或通知

    @socketio_instance.on('disconnect')
    def handle_disconnect():
        user_id = session.get('user_id')
        logger.info(f"Client disconnected: {request.sid}, user_id: {user_id}")
        if user_id:
            # 离开所有与此用户相关的聊天室
            # (这是一个简化的例子，实际应用中可能需要更复杂的房间管理)
            # for room_name in list_user_chat_rooms(user_id): # 你需要一个函数来获取用户所在的所有聊天室
            #     leave_room(room_name)
            #     logger.info(f"User {user_id} left room {room_name} on disconnect.")
            leave_room(str(user_id)) # 离开个人房间

    @socketio_instance.on('join_chat')
    def handle_join_chat(data):
        user_id = session.get('user_id')
        if not user_id:
            logger.warning(f"Join chat attempt from unauthenticated user. SID: {request.sid}")
            return

        contact_type = data.get('contact_type')
        contact_id = data.get('contact_id')
        if not contact_type or not contact_id:
            logger.warning(f"Join chat attempt with missing data: {data}. SID: {request.sid}")
            return

        room_name = None
        if contact_type == 'friend':
            user1 = min(int(user_id), int(contact_id))
            user2 = max(int(user_id), int(contact_id))
            room_name = f"friend_{user1}_{user2}"
        elif contact_type == 'group':
            room_name = f"group_{contact_id}"

        if room_name:
            # 用户可能已经在之前的某个房间，先离开 (可选，取决于你的逻辑)
            # old_room = session.get('current_chat_room')
            # if old_room and old_room != room_name:
            #     leave_room(old_room)
            #     logger.info(f"User {user_id} left old room {old_room}. SID: {request.sid}")

            join_room(room_name)
            session['current_chat_room'] = room_name # 记录当前聊天室
            logger.info(f"User {user_id} (SID: {request.sid}) joined room {room_name} for contact {contact_id}")
        else:
            logger.warning(f"Could not determine room name for join_chat: {data}. SID: {request.sid}")


    @socketio_instance.on('leave_chat')
    def handle_leave_chat(data): # data 可以包含之前的 room_name
        user_id = session.get('user_id')
        if not user_id:
            return

        room_name_to_leave = data.get('room_name') or session.get('current_chat_room')

        if room_name_to_leave:
            leave_room(room_name_to_leave)
            logger.info(f"User {user_id} (SID: {request.sid}) left room {room_name_to_leave}")
            if session.get('current_chat_room') == room_name_to_leave:
                session.pop('current_chat_room', None)
        else:
            logger.info(f"User {user_id} (SID: {request.sid}) tried to leave chat but no room was specified or found in session.")


    @socketio_instance.on('send_message')
    def handle_send_message(data):
        user_id = session.get('user_id')
        username = session.get('username')
        if not user_id or not username:
            logger.warning(f"Send message attempt without user_id or username in session. SID: {request.sid}")
            # emit('message_error', {'error': 'Authentication required.'}, room=request.sid)
            return

        content = data.get('message_content')
        selected_contact_id = data.get('contact_id')
        selected_contact_type = data.get('contact_type')

        if not content or not selected_contact_id or not selected_contact_type:
            logger.warning(f"Message sending attempt with missing data: {data}. SID: {request.sid}")
            # emit('message_error', {'error': 'Message content, contact_id, or contact_type missing.'}, room=request.sid)
            return

        try:
            receiver_id = int(selected_contact_id) if selected_contact_type == 'friend' else None
            group_id = int(selected_contact_id) if selected_contact_type == 'group' else None

            # 1. 保存消息到数据库
            # send_message 应该返回创建的消息ID或完整消息对象，以便包含准确的 sent_at 和 message_id
            # 为简化，我们先假设它只执行操作
            message_id = chat_service.send_message(user_id, receiver_id, group_id, content) # 假设返回 message_id
            logger.info(f"Message from {user_id} to {selected_contact_type} {selected_contact_id} saved to DB (ID: {message_id}).")

            # 2. 准备要发送给客户端的消息数据
            sent_at_formatted = datetime.now().strftime('%H:%M') # 理想情况下，这个时间应该来自数据库
            message_payload = {
                'message_id': message_id, # 新增
                'sender_id': user_id,
                'sender_username': username,
                'receiver_id': receiver_id,
                'group_id': group_id,
                'content': content,
                'sent_at': sent_at_formatted,
                # 'is_self' 将由客户端判断或在发送给不同用户时设置
                'contact_id': selected_contact_id,
                'contact_type': selected_contact_type
            }

            # 3. 确定消息要发送到哪个房间
            target_room = None
            if selected_contact_type == 'friend':
                user1 = min(int(user_id), int(selected_contact_id))
                user2 = max(int(user_id), int(selected_contact_id))
                target_room = f"friend_{user1}_{user2}"
            elif selected_contact_type == 'group':
                target_room = f"group_{selected_contact_id}"

            if target_room:
                logger.info(f"Emitting 'new_message' to room {target_room}. Payload: {message_payload}. SID: {request.sid}")
                # 向目标房间广播，所有客户端（包括发送者）都会收到
                # 客户端JS将根据 sender_id === current_user_id 来判断 is_self
                socketio_instance.emit('new_message', message_payload, room=target_room)
            else:
                logger.error(f"Could not determine target_room for message. Data: {data}. SID: {request.sid}")

        except Exception as e:
            logger.error(f"Error in send_message event: {e}. Data: {data}. SID: {request.sid}")
            # emit('message_error', {'error': 'An error occurred while sending the message.'}, room=request.sid)

    # 可以添加更多的 SocketIO 事件处理器
    # @socketio_instance.on('user_typing')
    # def handle_user_typing(data):
    #     room = data.get('room')
    #     username = session.get('username')
    #     if room and username:
    #         emit('is_typing', {'username': username}, room=room, include_self=False)

    # @socketio_instance.on('user_stopped_typing')
    # def handle_user_stopped_typing(data):
    #     room = data.get('room')
    #     username = session.get('username')
    #     if room and username:
    #         emit('is_not_typing', {'username': username}, room=room, include_self=False)