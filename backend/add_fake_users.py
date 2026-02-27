fake = Faker('zh_CN')


import random
from faker import Faker
from app import create_app

fake = Faker('zh_CN')
app = create_app()

def print_flush(msg):
    print(msg, flush=True)

with app.app_context():
    from auth import User
    from database import db
    # 删除所有非管理员用户
    non_admin_users = db.session.query(User).filter(User.is_admin == False).all()
    for user in non_admin_users:
        print_flush(f"删除用户: {user.username} ({user.email})")
        db.session.delete(user)
    db.session.commit()
    print_flush(f"已删除{len(non_admin_users)}个非管理员用户")

    # 生成20条faker测试用户数据，字段带明显随机特征
    created_count = 0
    for i in range(50):  # 最多尝试50次，确保20条
        if created_count >= 20:
            break
        username = f"user{random.randint(1000,9999)}_{fake.user_name()}"
        email = fake.unique.email()
        full_name = fake.name()
        password = fake.password(length=10, special_chars=True, digits=True, upper_case=True, lower_case=True)
        is_admin = False
        is_active = random.choice([True, True, True, False])
        # 避免用户名/邮箱重复
        if db.session.query(User).filter_by(username=username).first() or db.session.query(User).filter_by(email=email).first():
            continue
        user = User(
            username=username,
            email=email,
            full_name=full_name,
            is_admin=is_admin,
            is_active=is_active
        )
        user.set_password(password)
        db.session.add(user)
        print_flush(f"添加用户: {username}, 邮箱: {email}, 姓名: {full_name}, 密码: {password}, 激活: {is_active}")
        created_count += 1
    db.session.commit()
    print_flush(f"已批量生成并替换{created_count}个faker测试用户（不影响管理员账户）")
