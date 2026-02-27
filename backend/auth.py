from sqlalchemy import Column, Integer, String, DateTime, Boolean
from database import db
from datetime import datetime
import hashlib
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import os




# JWT配置
SECRET_KEY = "your-secret-key-here"  # 生产环境应该使用环境变量
REFRESH_SECRET_KEY = "your-refresh-secret-key-here"  # 刷新令牌的密钥
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

class User(db.Model):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(200), nullable=False)
    full_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, username, email, full_name='', is_active=True, is_admin=False, **kwargs):
        self.username = username
        self.email = email
        self.full_name = full_name
        self.is_active = is_active
        self.is_admin = is_admin
        for k, v in kwargs.items():
            setattr(self, k, v)

    def to_dict(self):
        try:
            print("=== user.to_dict() 调用，当前属性 ===")
            print(vars(self))
            created_at = getattr(self, 'created_at', None)
            updated_at = getattr(self, 'updated_at', None)
            created_at_str = created_at.isoformat() if created_at and hasattr(created_at, 'isoformat') else str(created_at) if created_at else None
            updated_at_str = updated_at.isoformat() if updated_at and hasattr(updated_at, 'isoformat') else str(updated_at) if updated_at else None
            return {
                'id': getattr(self, 'id', None),
                'username': getattr(self, 'username', None),
                'email': getattr(self, 'email', None),
                'full_name': getattr(self, 'full_name', None),
                'is_active': getattr(self, 'is_active', None),
                'is_admin': getattr(self, 'is_admin', None),
                'created_at': created_at_str,
                'updated_at': updated_at_str
            }
        except Exception as e:
            import traceback
            print("=== user.to_dict() 异常 ===")
            print(traceback.format_exc())
            print(f"Exception: {e}")
            return {'error': f'user.to_dict() error: {str(e)}'}
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


    def verify_password(self, password: str) -> bool:
        """
        明文密码校验（仅演示用，生产环境请勿使用！）
        """
        # 直接明文比对
        return password == getattr(self, 'hashed_password', '')

    def set_password(self, password: str):
        """
        明文存储密码（仅演示用，生产环境请勿使用！）
        """
        self.hashed_password = password

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    """创建刷新令牌"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str, token_type: str = "access"):
    """验证令牌"""
    try:
        if token_type == "access":
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        else:
            payload = jwt.decode(token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])

        if payload.get("type") != token_type:
            return None

        sub = payload.get("sub")
        if not isinstance(sub, str):
            return None
        username: str = sub
        return payload
    except JWTError:
        return None

def get_token_from_header(authorization: str) -> Optional[str]:
    """从Authorization头中提取令牌"""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    return authorization.split(" ")[1]