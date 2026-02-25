import time
import random
import json
from datetime import datetime
import requests

def generate_traffic_data():
    """生成模拟交通数据"""
    directions = ['north', 'south', 'east', 'west']

    lanes = []
    for i, direction in enumerate(directions):
        # 根据时间段模拟不同的车流量
        current_hour = datetime.now().hour
        if 7 <= current_hour <= 9 or 17 <= current_hour <= 19:  # 高峰期
            vehicle_count = random.randint(15, 30)
            avg_speed = random.uniform(15, 30)
        elif 10 <= current_hour <= 16:  # 平峰期
            vehicle_count = random.randint(5, 15)
            avg_speed = random.uniform(30, 45)
        else:  # 夜间低峰期
            vehicle_count = random.randint(1, 8)
            avg_speed = random.uniform(40, 60)

        # 确定交通状态
        if vehicle_count > 20:
            status = "congested"
        elif vehicle_count > 10:
            status = "heavy"
        else:
            status = "light"

        queue_length = vehicle_count * random.uniform(0.8, 1.5)
        occupancy_rate = min(vehicle_count / 50.0, 1.0)

        lane = {
            'id': f'lane_{direction}_1',
            'direction': direction,
            'vehicle_count': vehicle_count,
            'average_speed': round(avg_speed, 1),
            'queue_length': round(queue_length, 1),
            'occupancy_rate': round(occupancy_rate, 2),
            'status': status
        }
        lanes.append(lane)

    return {
        'intersection_id': 'intersection_001',
        'timestamp': datetime.utcnow().isoformat(),
        'lanes': lanes
    }

def send_data_to_backend(data):
    """向后端发送数据"""
    try:
        url = "http://localhost:8000/update_traffic_data"
        response = requests.post(url, json=data, timeout=5)
        if response.status_code == 200:
            return True
        else:
            print(f"发送数据失败: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"发送数据异常: {e}")
        return False

def run_simulation():
    """运行交通数据模拟"""
    print("🚀 启动交通数据模拟器...")
    print("📊 模拟器将每5秒生成一次交通数据并发送到后端")
    print("🔄 按 Ctrl+C 停止模拟")

    try:
        while True:
            # 生成数据
            data = generate_traffic_data()

            # 发送数据到后端
            if send_data_to_backend(data):
                # 打印数据摘要
                total_vehicles = sum(lane['vehicle_count'] for lane in data['lanes'])
                avg_speed = sum(lane['average_speed'] for lane in data['lanes']) / len(data['lanes'])
                congested_lanes = sum(1 for lane in data['lanes'] if lane['status'] == 'congested')

                print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                      f"✅ 数据已发送 - 总车流量: {total_vehicles}, 平均速度: {avg_speed:.1f}km/h, "
                      f"拥堵车道: {congested_lanes}")
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ 数据发送失败")

            # 等待5秒
            time.sleep(5)

    except KeyboardInterrupt:
        print("\n🛑 模拟器已停止")

if __name__ == "__main__":
    run_simulation()