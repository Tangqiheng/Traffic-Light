import numpy as np
import time
import serial
import threading
from typing import List, Dict, Tuple
import logging
import math

logger = logging.getLogger(__name__)

class RadarSensor:
    def __init__(self, sensor_id: str, port: str = None, baudrate: int = 115200):
        self.sensor_id = sensor_id
        self.port = port
        self.baudrate = baudrate
        self.serial_conn = None
        self.is_running = False
        
        # 雷达参数
        self.max_range = 100  # 最大检测距离（米）
        self.max_speed = 200  # 最大速度检测（km/h）
        self.angle_range = (-45, 45)  # 角度范围（度）
        
        # 数据缓存
        self.last_detection = {
            'timestamp': 0,
            'targets': [],
            'traffic_density': 0.0,
            'average_speed': 0.0
        }
        
        # 线程锁
        self.data_lock = threading.Lock()
    
    def initialize(self) -> bool:
        try:
            if self.port:
                # 真实硬件连接
                self.serial_conn = serial.Serial(
                    port=self.port,
                    baudrate=self.baudrate,
                    timeout=1
                )
                logger.info(f"毫米波雷达 {self.sensor_id} 连接成功 (端口: {self.port})")
            else:
                # 模拟模式
                logger.info(f"毫米波雷达 {self.sensor_id} 初始化为模拟模式")
            
            return True
            
        except Exception as e:
            logger.error(f"毫米波雷达初始化失败: {e}")
            return False
    
    def start_detection(self):
        if not self.initialize():
            return
            
        self.is_running = True
        logger.info(f"开始雷达检测 - 传感器 {self.sensor_id}")
        
        if self.serial_conn:
            # 真实硬件模式
            threading.Thread(target=self._read_hardware_data, daemon=True).start()
        else:
            # 模拟模式
            threading.Thread(target=self._generate_mock_data, daemon=True).start()
    
    def _read_hardware_data(self):
        try:
            while self.is_running:
                if self.serial_conn and self.serial_conn.in_waiting:
                    # 读取雷达数据（根据实际协议解析）
                    raw_data = self.serial_conn.readline()
                    parsed_data = self._parse_radar_data(raw_data)
                    
                    with self.data_lock:
                        self.last_detection = {
                            'timestamp': time.time(),
                            **parsed_data
                        }
                
                time.sleep(0.1)
                
        except Exception as e:
            logger.error(f"读取雷达硬件数据失败: {e}")
    
    def _parse_radar_data(self, raw_data: bytes) -> Dict:
        # 这里需要根据实际雷达协议解析数据
        # 示例解析（需要根据具体雷达型号调整）
        try:
            # 假设数据格式为: distance,speed,angle,distance,speed,angle,...
            data_str = raw_data.decode('utf-8').strip()
            values = [float(x) for x in data_str.split(',')]
            
            targets = []
            for i in range(0, len(values), 3):
                if i + 2 < len(values):
                    distance, speed, angle = values[i:i+3]
                    if distance <= self.max_range and abs(angle) <= max(abs(self.angle_range)):
                        targets.append({
                            'distance': distance,
                            'speed': speed,
                            'angle': angle,
                            'id': len(targets)
                        })
            
            # 计算交通密度和平均速度
            traffic_density = len(targets) / (self.max_range * math.radians(abs(self.angle_range[1] - self.angle_range[0])))
            average_speed = np.mean([t['speed'] for t in targets]) if targets else 0.0
            
            return {
                'targets': targets,
                'traffic_density': traffic_density,
                'average_speed': average_speed
            }
            
        except Exception as e:
            logger.error(f"解析雷达数据失败: {e}")
            return {'targets': [], 'traffic_density': 0.0, 'average_speed': 0.0}
    
    def _generate_mock_data(self):
        try:
            while self.is_running:
                # 生成模拟雷达数据
                num_targets = np.random.poisson(3)  # 泊松分布模拟目标数量
                
                targets = []
                for i in range(num_targets):
                    distance = np.random.uniform(5, self.max_range)
                    speed = np.random.normal(40, 15)  # 正态分布速度
                    speed = np.clip(speed, -self.max_speed, self.max_speed)
                    angle = np.random.uniform(self.angle_range[0], self.angle_range[1])
                    
                    targets.append({
                        'distance': distance,
                        'speed': speed,
                        'angle': angle,
                        'id': i
                    })
                
                # 计算交通密度
                traffic_density = len(targets) / (self.max_range * math.radians(abs(self.angle_range[1] - self.angle_range[0])))
                average_speed = np.mean([t['speed'] for t in targets]) if targets else 0.0
                
                with self.data_lock:
                    self.last_detection = {
                        'timestamp': time.time(),
                        'targets': targets,
                        'traffic_density': traffic_density,
                        'average_speed': average_speed
                    }
                
                time.sleep(0.2)  # 模拟数据更新频率
                
        except Exception as e:
            logger.error(f"生成模拟雷达数据失败: {e}")
    
    def get_detection_data(self) -> Dict:
        with self.data_lock:
            return self.last_detection.copy()
    
    def stop_detection(self):
        self.is_running = False
        if self.serial_conn:
            self.serial_conn.close()
        logger.info(f"停止雷达检测 - 传感器 {self.sensor_id}")

# 模拟雷达传感器（用于测试）
class MockRadarSensor(RadarSensor):
    def __init__(self, sensor_id: str):
        super().__init__(sensor_id, port=None)
    
    def initialize(self) -> bool:
        logger.info(f"模拟雷达传感器 {self.sensor_id} 初始化成功")
        return True
    
    def start_detection(self):
        self.is_running = True
        logger.info(f"开始模拟雷达检测 - 传感器 {self.sensor_id}")
        threading.Thread(target=self._generate_mock_data, daemon=True).start()
    
    def _generate_mock_data(self):
        try:
            while self.is_running:
                # 生成更真实的模拟数据
                targets = [
                    {'distance': 25.3, 'speed': 45.2, 'angle': -15.3, 'id': 0},
                    {'distance': 42.1, 'speed': 38.7, 'angle': 8.9, 'id': 1},
                    {'distance': 67.8, 'speed': 52.1, 'angle': -22.4, 'id': 2}
                ]
                
                # 添加随机噪声
                for target in targets:
                    target['distance'] += np.random.normal(0, 2)
                    target['speed'] += np.random.normal(0, 5)
                    target['angle'] += np.random.normal(0, 3)
                
                traffic_density = len(targets) / (self.max_range * math.radians(90))
                average_speed = np.mean([t['speed'] for t in targets])
                
                with self.data_lock:
                    self.last_detection = {
                        'timestamp': time.time(),
                        'targets': targets,
                        'traffic_density': traffic_density,
                        'average_speed': average_speed
                    }
                
                time.sleep(0.2)
                
        except Exception as e:
            logger.error(f"生成模拟雷达数据失败: {e}")
