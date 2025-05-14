# kaguchat_app/routes/auth_routes.py
from flask import Blueprint, request, session, jsonify
from flask_jwt_extended import create_access_token, unset_jwt_cookies, jwt_required, get_jwt_identity,decode_token
from ..extensions import login_service, chat_service, logger # 使用 .. 从父目录导入

auth_bp = Blueprint('auth_bp', __name__, url_prefix="/api/auth")

@auth_bp.route('/login', methods=['POST'])
def login_api():
    data = request.get_json()
    if not data:
        return jsonify({"msg":"Missing JSON in request"}) , 400
    
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"msg" : "Missing username or password"}), 400
    
    user_id = login_service.authenticate_user(username, password)
    if not user_id:
        logger.debug(f"Login failed for username : {username} - User not found")
        return jsonify({"msg" : "Bad username or password"}), 401
    
    user_id = str(user_id)
    access_token = create_access_token(identity=user_id)
    logger.debug(f"Login successful for user_id : {user_id}, username : {username}")

    decoded_token_payload = decode_token(access_token)
    csrf_token_value = decoded_token_payload.get('csrf')

    
    return jsonify(
        access_token = access_token,
        user_id = user_id,
        csrf_tokne = csrf_token_value
    ), 200

@auth_bp.route('/me', methods = ['GET'])
@jwt_required()
def get_current_user_info_api():
    current_user_id = get_jwt_identity()
    user_record = login_service.get_profile(current_user_id)
    if not user_record:
        logger.debug(f"Get profile Failed for user_id : {current_user_id}")
        return jsonify({"msg":"User not found for current token"}), 404
    user_data = user_record[0]
    return jsonify(user_data), 200
    

@auth_bp.route('/logout', methods = ['POST'])
@jwt_required()
def logout_api():
    logger.debug(f"Logout request for user_id: {get_jwt_identity()}")
    return jsonify({"msg": "Logout successful"}), 200

# --- 新增注册 API 端点 ---
@auth_bp.route('/signup', methods=['POST'])
def signup_api():
    data = request.get_json()
    if not data:
        return jsonify({"msg": "Missing JSON in request"}), 400

    username = data.get('username')
    password = data.get('password')
    phone = data.get('phone')
    nickname = data.get('nickname', username) # 如果没提供昵称，默认为用户名
    avatar_url = data.get('avatar_url', None) # 可选

    if not username or not password or not phone:
        return jsonify({"msg": "Username, password, and phone are required"}), 400
    
    result = login_service.register_user(username, password, nickname,phone, avatar_url)

    if result.get("success"):
        return jsonify({"msg": "User created successfully", "user_id": result.get("user_id")}), 201
    else:
        return jsonify({"msg": result.get("error", "Registration failed")}), 400 # 或 409 Conflict 如果是重复条目
