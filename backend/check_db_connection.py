import sqlite3

def check_database():
    try:
        conn = sqlite3.connect('traffic_control.db')
        cursor = conn.cursor()

        # 获取所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print("数据库中的表:")
        for table in tables:
            print(f"  - {table[0]}")

        # 检查traffic_data表
        if ('traffic_data',) in tables:
            cursor.execute("SELECT COUNT(*) FROM traffic_data")
            count = cursor.fetchone()[0]
            print(f"traffic_data表中有 {count} 条记录")

        # 检查traffic_light_status表
        if ('traffic_light_status',) in tables:
            cursor.execute("SELECT COUNT(*) FROM traffic_light_status")
            count = cursor.fetchone()[0]
            print(f"traffic_light_status表中有 {count} 条记录")

        conn.close()
        print("数据库连接正常")

    except Exception as e:
        print(f"数据库连接失败: {e}")

if __name__ == "__main__":
    check_database()