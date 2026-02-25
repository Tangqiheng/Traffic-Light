import numpy as np
import time
import serial
import threading
from typing import List, Dict, Tuple
import logging
from collections import deque

logger = logging.getLogger(__name__)

class MagneticSensor:
    def __init__(self, sensor_id: str, port: str = None, baudrate: int = 9600):
        self.sensor_id = sensor_id
        self.port = port
        self.baudrate = baudrate
        self.serial_conn = None
        self.is_running = False
        
        # 传感器参数
        self.baseline_value = 0  # 基准磁场值
        self.threshold = 50  # 检测阈值
        self.calibration_samples = 100  # 校准样本数
        
        # 车辆检测参数
        self.vehicle_present = False
        self.last_vehicle_time = 0
        self.vehicle_count = 0
        
        # 数据缓存
        self.last_detection = {
            'timestamp': 0,
            'magnetic_field': 0.0,
            'vehicle_present': False,
            'vehicle_count': 0,
            'occupancy_rate': 0.0
        }
        
        # 历史数据用于计算占用率
        self.occupancy_history = deque(maxlen=3600)  # 1小时的历史数据
        
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
                logger.info(f"地磁传感器 {self.sensor_id} 连接成功 (端口: {self.port})")
                
                # 校准传感器
                self._calibrate_sensor()
            else:
                # 模拟模式
                logger.info(f"地磁传感器 {self.sensor_id} 初始化为模拟模式")
                self.baseline_value = 1000  # 模拟基准值
            
            return True
            
        except Exception as e:
            logger.error(f"地磁传感器初始化失败: {e}")
            return False
    
    def _calibrate_sensor(self):
        """校准传感器，确定基准磁场值"""
        logger.info(f"开始校准地磁传感器 {self.sensor_id}")
        
        samples = []
        for _ in range(self.calibration_samples):
            if self.serial_conn and self.serial_conn.in_waiting:
                raw_data = self.serial_conn.readline()
                value = self._parse_sensor_data(raw_data)
                if value is not None:
                    samples.append(value)
            time.sleep(0.1)
        
        if samples:
            self.baseline_value = np.mean(samples)
            logger.info(f"传感器校准完成，基准值: {self.baseline_value:.2f}")
        else:
            self.baseline_value = 1000  # 默认基准值
            logger.warning("传感器校准失败，使用默认基准值")
    
    def start_detection(self):
        if not self.initialize():
            return
            
        self.is_running = True
        logger.info(f"开始地磁检测 - 传感器 {self.sensor_id}")
        
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
                    raw_data = self.serial_conn.readline()
                    magnetic_field = self._parse_sensor_data(raw_data)
                    
                    if magnetic_field is not None:
                        detection_data = self._process_detection(magnetic_field)
                        
                        with self.data_lock:
                            self.last_detection = {
                                'timestamp': time.time(),
                                'magnetic_field': magnetic_field,
                                **detection_data
                            }
                
                time.sleep(0.1)
                
        except Exception as e:
            logger.error(f"读取地磁传感器数据失败: {e}")
    
    def _parse_sensor_data(self, raw_data: bytes) -> float:
        """解析传感器原始数据"""
        try:
            # 假设数据格式为简单的数值
            data_str = raw_data.decode('utf-8').strip()
            value = float(data_str)
            return value
            
        except Exception as e:
            logger.error(f"解析传感器数据失败: {e}")
            return None
    
    def _process_detection(self, magnetic_field: float) -> Dict:
        """处理检测逻辑"""
        # 计算磁场变化
        field_change = abs(magnetic_field - self.baseline_value)
        
        # 检测车辆存在
        current_vehicle_present = field_change > self.threshold
        
        # 检测车辆通过（上升沿）
        if current_vehicle_present and not self.vehicle_present:
            self.vehicle_count += 1
            self.last_vehicle_time = time.time()
        
        self.vehicle_present = current_vehicle_present
        
        # 更新占用率历史
        self.occupancy_history.append(1 if current_vehicle_present else 0)
        
        # 计算占用率（过去1小时的平均值）
        occupancy_rate = sum(self.occupancy_history) / len(self.occupancy_history) if self.occupancy_history else 0.0
        
        return {
            'vehicle_present': current_vehicle_present,
            'vehicle_count': self.vehicle_count,
            'occupancy_rate': occupancy_rate
        }
    
    def _generate_mock_data(self):
        try:
            while self.is_running:
                # 生成模拟磁场数据
                base_field = self.baseline_value
                
                # 模拟车辆通过时的磁场变化
                if np.random.random() < 0.1:  # 10%的概率有车辆
                    # 模拟车辆通过过程
                    field_change = np.random.normal(0, 20)  # 添加噪声
                    magnetic_field = base_field + 80 + field_change  # 明显的磁场变化
                else:
                    magnetic_field = base_field + np.random.normal(0, 10)  # 正常噪声
                
                detection_data = self._process_detection(magnetic_field)
                
                with self.data_lock:
                    self.last_detection = {
                        'timestamp': time.time(),
                        'magnetic_field': magnetic_field,
                        **detection_data
                    }
                
                time.sleep(0.5)  # 模拟数据更新频率
                
        except Exception as e:
            logger.error(f"生成模拟地磁数据失败: {e}")
    
    def get_detection_data(self) -> Dict:
        with self.data_lock:
            return self.last_detection.copy()
    
    def reset_vehicle_count(self):
        """重置车辆计数"""
        with self.data_lock:
            self.vehicle_count = 0
            logger.info(f"重置车辆计数 - 传感器 {self.sensor_id}")
    
    def stop_detection(self):
        self.is_running = False
        if self.serial_conn:
            self.serial_conn.close()
        logger.info(f"停止地磁检测 - 传感器 {self.sensor_id}")

# 模拟地磁传感器（用于测试）
class MockMagneticSensor(MagneticSensor):
    def __init__(self, sensor_id: str):
        super().__init__(sensor_id, port=None)
        self.baseline_value = 1000
    
    def initialize(self) -> bool:
        logger.info(f"模拟地磁传感器 {self.sensor_id} 初始化成功")
        return True
    
    def start_detection(self):
        self.is_running = True
        logger.info(f"开始模拟地磁检测 - 传感器 {self.sensor_id}")
        threading.Thread(target=self._generate_mock_data, daemon=True).start()
    
    def _generate_mock_data(self):
        try:
            vehicle_timer = 0
            vehicle_duration = 0
            
            while self.is_running:
                current_time = time.time()
                
                # 模拟车辆通过
                if vehicle_timer <= 0 and np.random.random() < 0.05:  # 5%的概率开始车辆通过
                    vehicle_duration = np.random.uniform(2, 5)  # 车辆通过持续2-5秒
                    vehicle_timer = vehicle_duration
                
                if vehicle_timer > 0:
                    # 车辆通过中
                    magnetic_field = self.baseline_value + 100 + np.random.normal(0, 15)
                    vehicle_timer -= 0.5
                else:
                    # 无车辆
                    magnetic_field = self.baseline_value + np.random.normal(0, 8)
                
                detection_data = self._process_detection(magnetic_field)
                
                with self.data_lock:
                    self.last_detection = {
                        'timestamp': current_time,
                        'magnetic_field': magnetic_field,
                        **detection_data
                    }
                
                time.sleep(0.5)
                
        except Exception as e:
            logger.error(f"生成模拟地磁数据失败: {e}")
