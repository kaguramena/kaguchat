from flask import Blueprint, request, session, jsonify, current_app, url_for # 新增 current_app, url_for
from flask_jwt_extended import create_access_token, unset_jwt_cookies, jwt_required, get_jwt_identity, decode_token
from werkzeug.utils import secure_filename # 用于安全地获取文件名
import os # 新增 os
import uuid # 用于生成唯一文件名
from ..extensions import logger, table_service # 假设 table_service 已经可以更新 Users 表
# ... (其他导入) ...

user_bp = Blueprint('user_bp', __name__, url_prefix="/api/user")

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@user_bp.route('/upload_avatar', methods=['POST'])
@jwt_required() # 确保用户已登录
def upload_avatar_api():
    current_user_id_str = get_jwt_identity()
    if not current_user_id_str:
        return jsonify({"msg": "Authentication required"}), 401

    if 'avatar' not in request.files:
        return jsonify({"msg": "No avatar file part in the request"}), 400

    file = request.files['avatar']

    if file.filename == '':
        return jsonify({"msg": "No selected file"}), 400

    if file and allowed_file(file.filename):
        # 生成安全的文件名，并添加唯一前缀防止重名
        original_filename = secure_filename(file.filename)
        extension = original_filename.rsplit('.', 1)[1].lower()
        # 使用 UUID 生成唯一文件名，保留原始扩展名
        unique_filename = f"user_{current_user_id_str}_{uuid.uuid4().hex}.{extension}"
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)

        try:
            file.save(filepath) # 保存用户头像
            logger.info(f"Avatar for user {current_user_id_str} saved to {filepath}")

            # 更新数据库中的 avatar_url
            avatar_url = filepath
            
            update_success = table_service.update_record("Users", "user_id", int(current_user_id_str), {"avatar_url": avatar_url})

            if update_success:
                return jsonify({"msg": "Avatar uploaded successfully", "avatar_url": avatar_url}), 200
            else:
                # 如果更新失败，可能需要删除已保存的文件
                os.remove(filepath)
                logger.error(f"Failed to update avatar_url in DB for user {current_user_id_str}")
                return jsonify({"msg": "Failed to update avatar information in database"}), 500

        except Exception as e:
            logger.error(f"Error saving avatar for user {current_user_id_str}: {str(e)}")
            # 如果保存文件或更新数据库时出错，确保不会留下未处理的文件（如果已保存）
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except Exception as remove_e:
                    logger.error(f"Error cleaning up avatar file {filepath} after error: {remove_e}")
            return jsonify({"msg": f"Error uploading avatar: {str(e)}"}), 500
    else:
        return jsonify({"msg": "File type not allowed"}), 400