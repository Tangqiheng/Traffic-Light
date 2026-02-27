from flask import request, jsonify
from database import db
from auth import User, verify_token

def admin_auth_check():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None, jsonify({'error': '未提供有效的认证令牌'}), 401
    token = auth_header.split(' ')[1]
    username = verify_token(token)
    if not username:
        return None, jsonify({'error': '无效的认证令牌'}), 401
    user = db.session.query(User).filter_by(username=username).first()
    if not user or not (getattr(user, 'is_admin', False) is True):
        return None, jsonify({'error': '无权限，仅管理员可用'}), 403
    return user, None, None
