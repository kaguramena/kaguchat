# kaguchat_app/routes/auth_routes.py
from flask import Blueprint, request, session, jsonify
from flask_jwt_extended import create_access_token, unset_jwt_cookies, jwt_required, get_jwt_identity,decode_token
from ..extensions import login_service, chat_service, logger # 使用 .. 从父目录导入
import json, uuid, os
from werkzeug.utils import secure_filename
from flask import current_app

auth_bp = Blueprint('auth_bp', __name__, url_prefix="/api/auth")

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

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
    print(f"Decoded token payload: {decoded_token_payload}")
    print(f"CSRF token value: {csrf_token_value}")
    
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
    if user_data.get("avatar_url"):
        user_data["avatar_url"] = "http://localhost:5001" + user_data["avatar_url"] # 这里假设你在本地开发，实际部署时需要根据你的域名或IP来设置
    return jsonify(user_data), 200
    

@auth_bp.route('/logout', methods = ['POST'])
@jwt_required()
def logout_api():
    logger.debug(f"Logout request for user_id: {get_jwt_identity()}")
    return jsonify({"msg": "Logout successful"}), 200

# --- 新增注册 API 端点 ---
@auth_bp.route('/signup', methods=['POST'])
def signup_api():
    if 'avatar' in request.files:
        logger.debug("Avatar file found in request.files")
    else:
        logger.debug("No avatar file in request.files")
    logger.debug(f"Request form data: {request.form}")


    # 从 request.form 获取文本字段
    username = request.form.get('username')
    password = request.form.get('password')
    phone = request.form.get('phone')
    nickname = request.form.get('nickname', username) # 如果没提供昵称，默认为用户名

    avatar_file = request.files.get('avatar') # 获取头像文件

    if not username or not password or not phone:
        return jsonify({"msg": "Username, password, and phone are required"}), 400
    
    # 1. 先尝试注册用户（不包含头像URL，因为头像还未处理）
    # login_service.register_user 需要修改，允许 avatar_url 为 None 或在之后更新
    registration_result = login_service.register_user(
        username,
        password,
        nickname,
        phone,
        avatar_url=None # 初始注册时不提供头像 URL
    )

    if not registration_result.get("success"):
        return jsonify({"msg": registration_result.get("error", "Registration failed")}), 400

    new_user_id = registration_result.get("user_id")
    final_avatar_url = None # 初始化最终的头像 URL

    # 2. 如果用户注册成功并且上传了头像文件，则处理头像
    if new_user_id and avatar_file and avatar_file.filename != '' and allowed_file(avatar_file.filename):
        try:
            original_filename = secure_filename(avatar_file.filename)
            print(f"Original filename: {original_filename}")
            extension = original_filename.rsplit('.', 1)[1].lower()
            print(f"File extension: {extension}")
            unique_filename = f"user_{new_user_id}_{uuid.uuid4().hex}.{extension}"
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
            
            avatar_file.save(filepath)
            logger.info(f"Avatar for new user {new_user_id} saved to {filepath}")
            
            # 构建头像的相对 URL (相对于 static 目录)
            # 前端通常会拼接上域名，或者 Flask 配置为可以直接服务 /static/...
            final_avatar_url  = "/static/avatars/" + unique_filename

            # 更新刚创建的用户的 avatar_url
            update_success = login_service.upload_avatar(new_user_id, final_avatar_url) 

            if not update_success:
                logger.error(f"Failed to update avatar_url in DB for new user {new_user_id}")
                # 注意：这里可以选择是否回滚用户创建，或者仅仅是头像上传失败。
                # 为了简单，我们这里只记录错误，用户已创建但没有头像。
                final_avatar_url = None # 更新失败，则头像URL为空
            else:
                 logger.info(f"Avatar_url for user {new_user_id} updated to {final_avatar_url}")


        except Exception as e:
            logger.error(f"Error processing avatar for new user {new_user_id}: {str(e)}")
            final_avatar_url = None # 出错则头像URL为空
    elif avatar_file and (avatar_file.filename == '' or not allowed_file(avatar_file.filename)):
        logger.warning(f"Avatar file provided but was empty or not allowed for user {username}")

    # 返回成功信息
    response_data = {
        "msg": "User created successfully",
        "user_id": new_user_id
    }
    if final_avatar_url: # 如果头像处理成功，也返回头像 URL
        response_data["avatar_url"] = final_avatar_url
        response_data["msg"] += " Avatar uploaded."
    
    return jsonify(response_data), 201
