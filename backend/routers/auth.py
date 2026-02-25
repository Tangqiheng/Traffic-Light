from flask import Blueprint, request, jsonify
from sqlalchemy.orm import sessionmaker
from database import db
from auth import User, create_access_token, create_refresh_token, verify_token, get_token_from_header
from datetime import timedelta

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'error': '用户名和密码不能为空'}), 400

        # 查询用户
        user = db.session.query(User).filter_by(username=username).first()
        if not user or not user.verify_password(password):
            return jsonify({'error': '用户名或密码错误'}), 401

        # 使用getattr安全地获取布尔值
        is_user_active = getattr(user, 'is_active', False)
        if not is_user_active:
            return jsonify({'error': '用户已被禁用'}), 401

        # 创建令牌
        access_token = create_access_token(
            data={"sub": user.username, "user_id": user.id}
        )
        refresh_token = create_refresh_token(
            data={"sub": user.username, "user_id": user.id}
        )

        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'bearer',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': user.full_name,
                'is_admin': user.is_admin
            }
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    """获取当前用户信息"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': '缺少认证头'}), 401
            
        token = get_token_from_header(auth_header)  # auth_header已经检查过不为None
        if not token:
            return jsonify({'error': '无效的认证格式'}), 401

        payload = verify_token(token, "access")
        if not payload:
            return jsonify({'error': '无效的访问令牌'}), 401

        username = payload.get('sub')
        user = db.session.query(User).filter_by(username=username).first()
        if not user:
            return jsonify({'error': '用户不存在'}), 404

        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'full_name': user.full_name,
            'is_admin': user.is_admin
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/refresh', methods=['POST'])
def refresh_token():
    """刷新访问令牌"""
    try:
        data = request.get_json()
        refresh_token = data.get('refresh_token')

        if not refresh_token:
            return jsonify({'error': '未提供刷新令牌'}), 400

        payload = verify_token(refresh_token, "refresh")
        if not payload:
            return jsonify({'error': '无效的刷新令牌'}), 401

        username = payload.get('sub')
        user = db.session.query(User).filter_by(username=username).first()
        if not user:
            return jsonify({'error': '用户不存在'}), 404

        # 创建新的访问令牌
        access_token = create_access_token(
            data={"sub": user.username, "user_id": user.id}
        )

        return jsonify({
            'access_token': access_token,
            'token_type': 'bearer'
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500