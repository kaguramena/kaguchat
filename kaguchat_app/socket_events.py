# kaguchat_app/socket_events.py
from flask import request, current_app # 移除了 flask.session
from flask_socketio import emit, join_room, leave_room
from flask import session as socketio_session
# 确保 login_service 包含 verify_jwt_token 和 get_profile 方法
from .extensions import socketio, chat_service, login_service, logger
from datetime import datetime
import jwt # 直接使用 PyJWT 来解码和验证
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError, DecodeError # PyJWT 的异常

# 辅助函数：JWT 验证和用户身份提取 (可以放在 login_service 或 chat_service 中)
# 为清晰起见，我们先在这里定义，你可以后续移到 service 层
def verify_and_extract_user_from_token(token_string):
    """
    验证JWT token并返回包含 user_id 和 username 的字典。
    如果验证失败，则抛出相应的JWT异常。
    """
    if not token_string:
        raise InvalidTokenError("No token provided.")
    try:
        payload = jwt.decode(
            token_string,
            current_app.config['JWT_SECRET_KEY'],
            algorithms=[current_app.config.get('JWT_ALGORITHM', 'HS256')]
        )
        # Flask-JWT-Extended 默认使用 'sub' 作为身份标识
        user_id = str(payload['sub']) # 确保 user_id 是字符串，与 login_api 中创建token时一致
        
        # 尝试从 payload 中获取更多用户信息，例如 username 或 nickname
        # 这些需要在生成 JWT token 时就包含进去
        username = payload.get('username') # 假设 token 中有 username claim
        nickname = payload.get('nickname') # 假设 token 中有 nickname claim
        avatar_url = payload.get('avatar_url') # 假设 token 中有 avatar_url claim

        if not username: # 如果JWT中没有username，可以尝试从数据库查询
            # 注意：频繁在connect时查库可能影响性能，最好JWT中包含足够信息
            user_profile_list = login_service.get_profile(user_id) # get_profile 返回的是列表
            if user_profile_list:
                user_profile = user_profile_list[0]
                username = user_profile.get('username')
                if not nickname: # 如果JWT和DB都没有nickname，用username
                    nickname = user_profile.get('nickname', username)
                if not avatar_url:
                    avatar_url = user_profile.get('avatar_url')
            else: # 如果数据库也查不到（理论上不应该发生，因为JWT是基于存在的用户生成的）
                raise InvalidTokenError("User identity in token not found in database.")


        return {
            'user_id': user_id,
            'username': username or f"user_{user_id}", # 提供一个备用 username
            'nickname': nickname or username or f"User {user_id}",
            'avatar_url': avatar_url
        }
    except ExpiredSignatureError:
        logger.warning("JWT token has expired.")
        raise # 重新抛出给 connect handler
    except InvalidTokenError as e: # 包括 DecodeError, InvalidSignatureError 等
        logger.warning(f"Invalid JWT token: {e}")
        raise # 重新抛出给 connect handler
    except Exception as e: # 其他可能的错误
        logger.error(f"Unexpected error decoding JWT: {e}", exc_info=True)
        raise InvalidTokenError(f"Unexpected error during token decoding: {e}")


# 这个函数将在 __init__.py 中被调用来注册事件处理器
def register_socketio_events(socketio_instance):

    @socketio_instance.on('connect')
    def handle_connect(auth_data=None): # auth_data 是客户端通过 socket = io({ auth: {token: ...}}) 传递的
        token = None
        # 优先从 auth_data (推荐方式)
        if auth_data and isinstance(auth_data, dict) and 'token' in auth_data:
            token = auth_data.get('token')
        # 备用：从查询参数获取 (旧的或特定客户端可能使用的方式)
        elif request.args.get('token'):
            token = request.args.get('token')
            logger.info(f"Client {request.sid} connected using token from query parameter.")

        if not token:
            logger.warning(f"SocketIO 连接尝试，但缺少 JWT token。SID: {request.sid}")
            return False # 拒绝连接

        try:
            user_info = verify_and_extract_user_from_token(token) # 使用上面定义的辅助函数
            
            # 将用户信息存储在 Flask-SocketIO 的会话中
            socketio_session['user_id'] = user_info['user_id']
            socketio_session['username'] = user_info['username']
            socketio_session['nickname'] = user_info.get('nickname', user_info['username'])
            socketio_session['avatar_url'] = user_info.get('avatar_url')

            print("socketio_session:", socketio_session) # 调试用
            logger.info(f"客户端连接成功: {request.sid}, user_id: {user_info['user_id']}, username: {user_info['username']} (JWT认证)")
            join_room(str(user_info['user_id'])) # 加入以用户ID命名的房间

        except (ExpiredSignatureError, InvalidTokenError, DecodeError) as e:
            logger.warning(f"SocketIO 连接认证失败 for SID {request.sid}: {str(e)}")
            return False # 拒绝连接
        except Exception as e:
            logger.error(f"SocketIO 'connect' 事件中发生未知错误: {e}. SID: {request.sid}", exc_info=True)
            return False


    @socketio_instance.on('disconnect')
    def handle_disconnect():
        user_id = socketio_session.get('user_id') # 从 socketio_session 获取
        logger.info(f"客户端断开连接: {request.sid}, user_id: {user_id if user_id else 'N/A'}")
        if user_id:
            # 离开个人房间
            leave_room(str(user_id))
            # 如果有 current_chat_room，也应该离开
            current_room = socketio_session.pop('current_chat_room', None)
            if current_room:
                leave_room(current_room)
                logger.info(f"User {user_id} (SID: {request.sid}) left room {current_room} on disconnect.")
            # 清理 socketio_session (可选, 因为连接断开后这个session也就失效了)
            # socketio_session.clear()


    @socketio_instance.on('join_chat')
    def handle_join_chat(data):
        user_id_str = socketio_session.get('user_id') # 从 socketio_session 获取
        if not user_id_str:
            logger.warning(f"未认证用户 (SID: {request.sid}) 尝试加入聊天。")
            emit('auth_error', {'message': 'Authentication required to join chat.'}, room=request.sid)
            return

        contact_type = data.get('contact_type')
        contact_id_str = str(data.get('contact_id')) # 确保 contact_id 是字符串以便统一处理
        
        if not contact_type or not contact_id_str:
            logger.warning(f"加入聊天尝试，但缺少 contact_type 或 contact_id: {data}。SID: {request.sid}")
            emit('chat_error', {'message': 'contact_type and contact_id are required.'}, room=request.sid)
            return

        try:
            user_id = int(user_id_str)
            contact_id = int(contact_id_str)
        except ValueError:
            logger.error(f"加入聊天时ID格式无效。 UserID: {user_id_str}, ContactID: {contact_id_str}。SID: {request.sid}")
            emit('chat_error', {'message': 'Invalid ID format.'}, room=request.sid)
            return

        room_name = None
        if contact_type == 'friend':
            # 对用户ID进行排序，确保房间名对于两个用户是唯一的且相同的
            user1 = min(user_id, contact_id)
            user2 = max(user_id, contact_id)
            room_name = f"friend_{user1}_{user2}"
        elif contact_type == 'group':
            room_name = f"group_{contact_id}"
        else:
            logger.warning(f"无效的 contact_type: {contact_type}。SID: {request.sid}")
            emit('chat_error', {'message': 'Invalid contact type.'}, room=request.sid)
            return

        # （可选）离开旧的聊天房间
        old_room = socketio_session.get('current_chat_room')
        if old_room and old_room != room_name:
            leave_room(old_room)
            logger.info(f"用户 {user_id} (SID: {request.sid}) 离开旧房间 {old_room}。")

        join_room(room_name)
        socketio_session['current_chat_room'] = room_name # 在 socketio_session 中记录当前聊天室
        logger.info(f"用户 {user_id} (SID: {request.sid}) 加入房间 {room_name} (与 {contact_type} {contact_id} 聊天)。")
        emit('joined_chat_room', {'room_name': room_name, 'message': f'Successfully joined chat with {contact_id}.'}, room=request.sid)


    @socketio_instance.on('leave_chat')
    def handle_leave_chat(data): # data 可以包含 room_name 或 contact_id/contact_type
        user_id = socketio_session.get('user_id') # 从 socketio_session 获取
        if not user_id:
            # 一般来说，如果用户未认证，他们不应该能触发这个事件
            return

        room_name_to_leave = None
        if data and data.get('room_name'):
            room_name_to_leave = data.get('room_name')
        elif socketio_session.get('current_chat_room'):
             room_name_to_leave = socketio_session.get('current_chat_room')
        # 你也可以根据 data 中的 contact_id/contact_type 来重新计算 room_name

        if room_name_to_leave:
            leave_room(room_name_to_leave)
            logger.info(f"用户 {user_id} (SID: {request.sid}) 离开房间 {room_name_to_leave}")
            # 如果离开的是当前聊天室，则从 session 中移除
            if socketio_session.get('current_chat_room') == room_name_to_leave:
                socketio_session.pop('current_chat_room', None)
            emit('left_chat_room', {'room_name': room_name_to_leave, 'message': 'Successfully left chat room.'}, room=request.sid)
        else:
            logger.info(f"用户 {user_id} (SID: {request.sid}) 尝试离开聊天，但未指定房间或在session中未找到。")


    @socketio_instance.on('send_message')
    def handle_send_message(data):
        logger.info(f"SocketIO: >>>>>>> Received Sending attempt. SID: {request.sid}")
        sender_id_str = socketio_session.get('user_id')
        # 从 socketio_session 获取更完整的用户信息
        sender_username = socketio_session.get('username')
        sender_nickname = socketio_session.get('nickname', sender_username) # 优先用昵称
        sender_avatar_url = socketio_session.get('avatar_url')

        if not sender_id_str:
            logger.warning(f"发送消息尝试，但 socketio_session 中缺少 user_id。SID: {request.sid}")
            emit('unauthorized', {'error': 'Authentication required to send messages.'}, room=request.sid)
            return

        content = data.get('message_content')
        selected_contact_id_str = str(data.get('contact_id')) # 确保是字符串
        selected_contact_type = data.get('contact_type')

        if not content or not selected_contact_id_str or not selected_contact_type:
            logger.warning(f"发送消息尝试，但缺少数据: {data}。SID: {request.sid}")
            emit('message_error', {'error': 'Message content, contact_id, or contact_type missing.'}, room=request.sid)
            return

        try:
            sender_id = int(sender_id_str)
            selected_contact_id = int(selected_contact_id_str)

            receiver_id_db = None
            group_id_db = None

            if selected_contact_type == 'friend':
                receiver_id_db = selected_contact_id
            elif selected_contact_type == 'group':
                group_id_db = selected_contact_id
            else:
                logger.error(f"无效的 contact_type: {selected_contact_type}。数据: {data}。SID: {request.sid}")
                emit('message_error', {'error': 'Invalid contact type.'}, room=request.sid)
                return

            # 1. 保存消息到数据库
            # 修改 chat_service.send_message 以便它返回包含 message_id 和 sent_at 的完整消息对象或字典
            saved_message_info = chat_service.send_message_and_get_info(
                sender_id, 
                selected_contact_id,
                selected_contact_type,
                content
            )
            #print("sender_id:", sender_id," selected_contact_id:", selected_contact_id, "selected_contact_type:", selected_contact_type, "content:", content)
            
            # print(saved_message_info)
            if not saved_message_info or 'message_id' not in saved_message_info or 'sent_at' not in saved_message_info:
                logger.error(f"消息保存失败或未能返回必要信息。Sender: {sender_id}。SID: {request.sid}")
                emit('message_error', {'error': 'Failed to save message.'}, room=request.sid)
                return
                
            message_id = saved_message_info['message_id']
            sent_at_from_db = saved_message_info['sent_at']

            logger.info(f"消息 (ID: {message_id}) 从 {sender_id} 发往 {selected_contact_type} {selected_contact_id} 已保存至数据库。")

            # 2. 准备要发送给客户端的消息数据
            # 使用从数据库获取的精确时间，并格式化
            sent_at_formatted = sent_at_from_db # ISO 8601 格式

            message_payload = {
                'id': message_id, # 通常前端列表使用 id 作为 key
                'message_id': message_id, 
                'sender_id': sender_id,
                'sender_username': sender_username, # 登录名
                'sender_nickname': sender_nickname, # 显示昵称
                'sender_avatar_url': sender_avatar_url, # 发送者头像
                'receiver_id': receiver_id_db, # 明确是数据库用的 receiver_id
                'group_id': group_id_db,       # 明确是数据库用的 group_id
                'content': content,
                'sent_at': sent_at_formatted, # ISO 格式时间戳
                # is_self 将由客户端根据 sender_id === currentUser.user_id 判断
                'contact_id': selected_contact_id, # 前端可能需要这个来更新特定对话
                'contact_type': selected_contact_type
            }

            # 3. 确定消息要发送到哪个房间
            target_room = None
            if selected_contact_type == 'friend':
                user1 = min(sender_id, selected_contact_id)
                user2 = max(sender_id, selected_contact_id)
                target_room = f"friend_{user1}_{user2}"
            elif selected_contact_type == 'group':
                target_room = f"group_{selected_contact_id}"

            if target_room:
                logger.info(f"向房间 {target_room} 广播 'new_message'。Payload: {message_payload}。SID: {request.sid}")
                socketio_instance.emit('new_message', message_payload, room=target_room)
                
                # （可选）如果需要，也可以给发送者一个单独的确认事件，但通常广播到房间已包含发送者
                # emit('message_sent_confirmation', {'message_id': message_id, 'status': 'success'}, room=request.sid)
            else:
                logger.error(f"无法确定消息的目标房间。数据: {data}。SID: {request.sid}")
                # 这种情况理论上不应发生，因为 contact_type 已被验证

        except ValueError:
            logger.error(f"发送消息时ID格式无效。 UserID: {sender_id_str}, ContactID: {selected_contact_id_str}。SID: {request.sid}")
            emit('message_error', {'error': 'Invalid ID format.'}, room=request.sid)
        except Exception as e:
            logger.error(f"send_message 事件处理出错: {e}. 数据: {data}. SID: {request.sid}", exc_info=True)
            emit('message_error', {'error': 'An error occurred while sending the message.'}, room=request.sid)

    # --- （可选）用户正在输入状态 ---
    @socketio_instance.on('user_typing')
    def handle_user_typing(data):
        user_id = socketio_session.get('user_id')
        nickname = socketio_session.get('nickname', socketio_session.get('username'))
        
        if not user_id or not nickname:
            return # 未认证用户不能发送此事件

        target_room = socketio_session.get('current_chat_room') # 直接用当前用户所在的聊天室
        # 或者，如果客户端明确指定了房间/联系人：
        # contact_type = data.get('contact_type')
        # contact_id = data.get('contact_id')
        # target_room = calculate_room_name(user_id, contact_id, contact_type) # 你需要一个计算房间名的函数

        if target_room:
            # include_self=False 确保 "正在输入" 的提示不会显示给输入者自己
            socketio_instance.emit('is_typing', {'user_id': user_id, 'nickname': nickname}, room=target_room, include_self=False)
            logger.debug(f"User {user_id} ({nickname}) is typing in room {target_room}")

    @socketio_instance.on('user_stopped_typing')
    def handle_user_stopped_typing(data):
        user_id = socketio_session.get('user_id')
        nickname = socketio_session.get('nickname', socketio_session.get('username'))

        if not user_id or not nickname:
            return

        target_room = socketio_session.get('current_chat_room')
        # 或者同上，从 data 中获取

        if target_room:
            socketio_instance.emit('is_not_typing', {'user_id': user_id, 'nickname': nickname}, room=target_room, include_self=False)
            logger.debug(f"User {user_id} ({nickname}) stopped typing in room {target_room}")