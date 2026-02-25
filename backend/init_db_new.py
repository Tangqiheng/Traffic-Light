from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()

class User(Base):
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

    def set_password(self, password: str):
        """设置密码"""
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.hashed_password = pwd_context.hash(password)

# 创建内存数据库用于演示
SQLALCHEMY_DATABASE_URL = "sqlite:///./traffic_control.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成")

def create_default_admin():
    """创建默认管理员用户"""
    session = SessionLocal()
    try:
        # 检查是否已存在管理员
        admin_user = session.query(User).filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@example.com',
                full_name='系统管理员',
                is_admin=True
            )
            admin_user.set_password('admin123')
            session.add(admin_user)
            session.commit()
            print("默认管理员账户已创建: admin / admin123")
        else:
            print("管理员账户已存在")
    finally:
        session.close()

if __name__ == "__main__":
    create_tables()
    create_default_admin()