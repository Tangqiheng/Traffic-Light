#!/usr/bin/env python3
"""
初始化数据库和创建管理员账户
"""

from database import db
from auth import User
from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./traffic_users.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app

def init_database(app):
    """初始化数据库"""
    with app.app_context():
        print("正在创建数据库表...")
        db.create_all()
        print("数据库表创建完成")

def create_admin_user(app):
    """创建管理员账户"""
    with app.app_context():
        admin_user = db.session.query(User).filter_by(username="admin").first()
        if admin_user:
            print("管理员账户已存在")
            return
        admin = User(
            username="admin",
            email="admin@traffic.com",
            full_name="系统管理员",
            is_admin=True,
            is_active=True
        )
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()
        print("管理员账户已创建")

    app = create_app()
    init_database(app)
    create_admin_user(app)
    with app.app_context():
        # 创建测试用户
        test_users = [
            {"username": "user1", "email": "user1@example.com", "password": "123456", "full_name": "测试用户1"},
            {"username": "user2", "email": "user2@example.com", "password": "123456", "full_name": "测试用户2"},
        ]
        for user_data in test_users:
            existing_user = db.session.query(User).filter_by(username=user_data["username"]).first()
            if existing_user:
                print(f"用户 {user_data['username']} 已存在，跳过")
                continue
            user = User(
                username=user_data["username"],
                email=user_data["email"],
                full_name=user_data["full_name"],
                is_admin=False,
                is_active=True
            )
            user.set_password(user_data["password"])
            db.session.add(user)
            db.session.commit()
            print(f"创建用户: {user_data['username']}")
        print("测试用户创建完成")


if __name__ == "__main__":
    print("开始初始化数据库...")
    app = create_app()
    init_database(app)
    create_admin_user(app)
    with app.app_context():
        # 创建测试用户
        test_users = [
            {"username": "user1", "email": "user1@example.com", "password": "123456", "full_name": "测试用户1"},
            {"username": "user2", "email": "user2@example.com", "password": "123456", "full_name": "测试用户2"},
        ]
        for user_data in test_users:
            existing_user = db.session.query(User).filter_by(username=user_data["username"]).first()
            if existing_user:
                print(f"用户 {user_data['username']} 已存在，跳过")
                continue
            user = User(
                username=user_data["username"],
                email=user_data["email"],
                full_name=user_data["full_name"],
                is_admin=False,
                is_active=True
            )
            user.set_password(user_data["password"])
            db.session.add(user)
            db.session.commit()
            print(f"创建用户: {user_data['username']}")
    print("初始化完成！")