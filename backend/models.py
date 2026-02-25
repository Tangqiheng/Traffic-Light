from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
import os

def create_access_token(username):
    """创建访问令牌"""
    payload = {
        'sub': username,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24),
        'iat': datetime.datetime.utcnow()
    }
    secret_key = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
    return jwt.encode(payload, secret_key, algorithm='HS256')

def create_refresh_token(username):
    """创建刷新令牌"""
    payload = {
        'sub': username,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7),
        'iat': datetime.datetime.utcnow()
    }
    secret_key = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
    return jwt.encode(payload, secret_key, algorithm='HS256')

def verify_token(token):
    """验证令牌"""
    try:
        secret_key = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        return payload['sub']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

# 延迟导入db，避免循环导入
def get_db():
    from database import db
    return db

class UserMixin:
    """用户模型混入类"""
    id = None
    username = None
    email = None
    password_hash = None
    full_name = None
    is_active = None
    is_admin = None
    created_at = None
    
    def set_password(self, password):
        """设置密码哈希"""
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        """验证密码"""
        if self.password_hash is None:
            return False
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'is_active': self.is_active,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# 注意：JWT相关的函数(create_access_token, create_refresh_token, verify_token)
# 已经移到auth.py文件中，避免重复定义