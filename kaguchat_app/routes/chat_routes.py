# kaguchat_app/routes/chat_routes.py
from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import get_jwt_identity, jwt_required
from ..extensions import chat_service, logger # socketio # 导入 socketio (如果这个蓝图用不到socketio实例，可以不导)


# 注意你这里蓝图名称是 chat_bp，但 url_prefix 是 /api/chat
chat_bp = Blueprint('chat_bp', __name__, url_prefix="/api/chat") 

@chat_bp.route('/contacts', methods=['GET']) # API端点: GET /api/chat/contacts
@jwt_required() # 需要JWT认证
def get_contacts():
    FLASK_URL = current_app.config['FLASK_URL']
    user_id_str = get_jwt_identity() # 从JWT获取用户ID (通常是字符串)
    # logger.debug(f"API /contacts called by user_id: {user_id_str}")
    if not user_id_str:
        # jwt_required 应该已经处理了token不存在或无效的情况，这里理论上不会执行
        return jsonify({"error": "Authentication required, user_id missing from token"}), 401
    try:
        # chat_service.get_contact_list 期望的是 user_id
        # 确保你的 chat_service.get_contact_list 能正确处理字符串或整数类型的user_id
        # 或者在这里转换: user_id_int = int(user_id_str)
        contacts = chat_service.get_contact_list(user_id_str) # 直接使用 chat_service 全局实例
        
        contacts = [
    {**contact, "avatar_url": f"{FLASK_URL}{contact['avatar_url']}"} if contact.get("avatar_url") else contact
    for contact in contacts
]

        print(contacts)
        return jsonify(contacts=contacts), 200 # 返回 { "contacts": [...] }
    except Exception as e:
        logger.error(f"Chat: Error fetching contacts for user_id {user_id_str}: {e}", exc_info=True)
        return jsonify({"error": "Internal server error fetching contacts"}), 500

# @jwt_required() # 这个装饰器应该在 @chat_bp.route 下面
@chat_bp.route('/messages/<contact_type>/<contact_id_str>', methods=['GET']) # API端点
@jwt_required() # 需要JWT认证
def get_messages(contact_type, contact_id_str): # 从URL路径获取参数
    user_id_str = get_jwt_identity()
    if not user_id_str:
        return jsonify({"error": "Authentication required, user_id missing from token"}), 401

    if contact_type not in ['friend', 'group']:
        logger.warning(f"Chat: Invalid contact_type: {contact_type}")
        return jsonify({"error": "Invalid contact type"}), 400

    try:
        user_id_int = int(user_id_str)
        contact_id_int = int(contact_id_str) # 从路径参数转换
    except ValueError:
        logger.error(f"Chat: Invalid ID format. UserID: {user_id_str}, ContactID: {contact_id_str}")
        return jsonify({"error": "Invalid ID format for user or contact"}), 400
    
    try:
        # 确保 chat_service.get_messages 接收正确的参数类型
        messages = chat_service.get_messages(user_id_int, contact_id_int, contact_type)
        # messages.map(lambda msg: msg.update({"contact_avatar_url": f"http://localhost:5001/{msg['contact_avatar_url']}"}) if msg.get("contact_avatar_url") else None) # 处理消息中的头像URL
        return jsonify(messages=messages), 200 # 返回 { "messages": [...] }
    except Exception as e:
        logger.error(f"Error fetching messages for user_id {user_id_str} and contact {contact_type}/{contact_id_str}: {e}", exc_info=True)
        return jsonify({"error": "Internal server error fetching messages"}), 500
    
@chat_bp.route('/send_message', methods=['POST']) # API端点
@jwt_required() # 需要JWT认证
def send_message():
    user_id_str = get_jwt_identity()
    if not user_id_str:
        return jsonify({"error": "Authentication required, user_id missing from token"}), 401

    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON in request"}), 400

    contact_type = data.get('contact_type')
    contact_id_str = data.get('contact_id')
    message_content = data.get('message')

    if not contact_type or not contact_id_str or not message_content:
        return jsonify({"error": "Missing required fields"}), 400

    if contact_type not in ['friend', 'group']:
        logger.warning(f"Chat: Invalid contact_type: {contact_type}")
        return jsonify({"error": "Invalid contact type"}), 400

    try:
        user_id_int = int(user_id_str)
        contact_id_int = int(contact_id_str) # 从路径参数转换
    except ValueError:
        logger.error(f"Chat: Invalid ID format. UserID: {user_id_str}, ContactID: {contact_id_str}")
        return jsonify({"error": "Invalid ID format for user or contact"}), 400
    
    try:
        # 确保 chat_service.send_message 接收正确的参数类型
        chat_service.send_message(user_id_int, contact_id_int, contact_type, message_content)
        return jsonify({"status": "Message sent successfully"}), 200
    except Exception as e:
        logger.error(f"Error sending message for user_id {user_id_str} to {contact_type}/{contact_id_str}: {e}", exc_info=True)
        return jsonify({"error": "Internal server error sending message"}), 500