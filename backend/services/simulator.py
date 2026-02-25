import time
import random
from datetime import datetime

class SimulatedHardware:
    """模拟硬件设备类，用于生成交通数据"""
    
    @staticmethod
    def get_simulated_traffic_data():
        """获取模拟交通数据"""
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
            'timestamp': datetime.utcnow(),
            'lanes': lanes
        }