import pymysql

# 该脚本将重置 admin 用户的密码为 admin123（明文存储，适配当前逻辑）
# 适用于 backend/database.py 默认的 SQLite 数据库 traffic_control.db

def reset_admin_password(
    host='localhost', port=3306, user='root', password='123456', db='traffic_db',
    username='admin', new_password='admin123'):
    conn = pymysql.connect(host=host, port=port, user=user, password=password, db=db, charset='utf8mb4')
    cursor = conn.cursor()
    from datetime import datetime
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # 检查用户是否存在
    cursor.execute("SELECT id FROM users WHERE username=%s", (username,))
    row = cursor.fetchone()
    if row:
        sql = "UPDATE users SET hashed_password=%s, is_active=1, is_admin=1, updated_at=%s WHERE username=%s"
        cursor.execute(sql, (new_password, now, username))
        print(f"[INFO] 用户 '{username}' 密码已重置为: {new_password}")
    else:
        sql = ("INSERT INTO users (username, hashed_password, is_admin, is_active, email, created_at, updated_at) "
               "VALUES (%s, %s, 1, 1, %s, %s, %s)")
        email = f"{username}@traffic.com"
        cursor.execute(sql, (username, new_password, email, now, now))
        print(f"[INFO] 用户 '{username}' 不存在，已创建新管理员，密码: {new_password}")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    reset_admin_password()
