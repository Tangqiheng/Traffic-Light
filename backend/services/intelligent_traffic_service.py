import threading
import time
import logging
from typing import Dict, List
from sensors.camera_sensor import MockCameraSensor
from sensors.radar_sensor import MockRadarSensor
from sensors.magnetic_sensor import MockMagneticSensor
from sensors.sensor_fusion import SensorFusion
from algorithms.traffic_classification import TrafficStateClassifier
from controllers.adaptive_control import AdaptiveTrafficController
from mqtt_client.mqtt_handler import TrafficLightMQTTClient

logger = logging.getLogger(__name__)

class IntelligentTrafficService:
    def __init__(self, intersection_id: str = "intersection_001"):
        self.intersection_id = intersection_id
        self.is_running = False
        
        # 初始化传感器
        self.camera_sensors = {}
        self.radar_sensors = {}
        self.magnetic_sensors = {}
        
        # 初始化融合和控制模块
        self.sensor_fusion = SensorFusion(intersection_id)
        self.traffic_classifier = TrafficStateClassifier()
        self.adaptive_controller = AdaptiveTrafficController(intersection_id)
        
        # 初始化MQTT客户端
        self.mqtt_client = TrafficLightMQTTClient(intersection_id)
        
        # 控制线程
        self.control_thread = None
        self.monitoring_thread = None
        
        # 数据缓存
        self.latest_fused_data = {}
        self.latest_classification = {}
        self.control_status = {}
    
    def initialize_sensors(self) -> bool:
        """初始化所有传感器"""
        try:
            # 初始化摄像头传感器
            camera_ids = ['cam_north', 'cam_south', 'cam_east', 'cam_west']
            for cam_id in camera_ids:
                sensor = MockCameraSensor(cam_id)
                if sensor.initialize():
                    self.camera_sensors[cam_id] = sensor
                    logger.info(f"摄像头传感器 {cam_id} 初始化成功")
                else:
                    logger.error(f"摄像头传感器 {cam_id} 初始化失败")
            
            # 初始化雷达传感器
            radar_ids = ['radar_north', 'radar_south', 'radar_east', 'radar_west']
            for radar_id in radar_ids:
                sensor = MockRadarSensor(radar_id)
                if sensor.initialize():
                    self.radar_sensors[radar_id] = sensor
                    logger.info(f"雷达传感器 {radar_id} 初始化成功")
                else:
                    logger.error(f"雷达传感器 {radar_id} 初始化失败")
            
            # 初始化地磁传感器
            magnetic_ids = ['mag_north', 'mag_south', 'mag_east', 'mag_west']
            for mag_id in magnetic_ids:
                sensor = MockMagneticSensor(mag_id)
                if sensor.initialize():
                    self.magnetic_sensors[mag_id] = sensor
                    logger.info(f"地磁传感器 {mag_id} 初始化成功")
                else:
                    logger.error(f"地磁传感器 {mag_id} 初始化失败")
            
            logger.info("所有传感器初始化完成")
            return True
            
        except Exception as e:
            logger.error(f"传感器初始化失败: {e}")
            return False
    
    def start_sensors(self):
        """启动所有传感器"""
        try:
            # 启动摄像头传感器
            for sensor in self.camera_sensors.values():
                threading.Thread(target=sensor.start_detection, daemon=True).start()
            
            # 启动雷达传感器
            for sensor in self.radar_sensors.values():
                threading.Thread(target=sensor.start_detection, daemon=True).start()
            
            # 启动地磁传感器
            for sensor in self.magnetic_sensors.values():
                threading.Thread(target=sensor.start_detection, daemon=True).start()
            
            logger.info("所有传感器已启动")
            
        except Exception as e:
            logger.error(f"启动传感器失败: {e}")
    
    def initialize_mqtt(self) -> bool:
        """初始化MQTT通信"""
        try:
            if self.mqtt_client.connect():
                # 添加传感器数据回调
                self.mqtt_client.add_sensor_callback(self._on_sensor_data_received)
                
                # 添加控制命令回调
                self.mqtt_client.add_control_callback(self._on_control_command_received)
                
                logger.info("MQTT通信初始化成功")
                return True
            else:
                logger.error("MQTT通信初始化失败")
                return False
                
        except Exception as e:
            logger.error(f"MQTT初始化异常: {e}")
            return False
    
    def _on_sensor_data_received(self, sensor_type: str, data: Dict):
        """传感器数据接收回调"""
        try:
            # 更新传感器融合数据
            sensor_id = data.get('sensor_id', f"{sensor_type}_unknown")
            self.sensor_fusion.update_sensor_data(sensor_type, sensor_id, data)
            
            logger.debug(f"收到传感器数据: {sensor_type} - {sensor_id}")
            
        except Exception as e:
            logger.error(f"处理传感器数据失败: {e}")
    
    def _on_control_command_received(self, command: Dict):
        """控制命令接收回调"""
        try:
            command_type = command.get('type', 'unknown')
            logger.info(f"收到控制命令: {command_type}")
            
            # 这里可以实现远程控制逻辑
            
        except Exception as e:
            logger.error(f"处理控制命令失败: {e}")
    
    def start_monitoring(self):
        """启动监控线程"""
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        logger.info("监控线程已启动")
    
    def _monitoring_loop(self):
        """监控循环"""
        while self.is_running:
            try:
                # 收集传感器数据
                sensor_data = self._collect_sensor_data()
                
                # 更新传感器融合
                for sensor_type, sensors in sensor_data.items():
                    for sensor_id, data in sensors.items():
                        self.sensor_fusion.update_sensor_data(sensor_type, sensor_id, data)
                
                # 获取融合数据
                fused_data = self.sensor_fusion.get_fused_data()
                self.latest_fused_data = fused_data
                
                # 交通状态分类
                if fused_data.get('overall_status'):
                    overall_status = fused_data['overall_status']
                    # 构造分类特征
                    features = {
                        'queue_length': overall_status.get('total_vehicles', 0),
                        'average_speed': overall_status.get('average_speed', 30),
                        'occupancy_rate': overall_status.get('average_occupancy', 0),
                        'traffic_density': 0.5,  # 简化为固定值
                        'flow_rate': 0,  # 暂时未实现
                        'speed_variance': 5,  # 简化为固定值
                        'direction_balance': 0.8  # 简化为固定值
                    }
                    
                    classification = self.traffic_classifier.classify_traffic_state(features)
                    self.latest_classification = classification
                
                # 发布状态到MQTT
                if self.mqtt_client.get_connection_status():
                    status_data = {
                        'intersection_id': self.intersection_id,
                        'timestamp': time.time(),
                        'fused_data': fused_data,
                        'classification': self.latest_classification,
                        'control_status': self.control_status
                    }
                    self.mqtt_client.publish_status(status_data)
                
                time.sleep(1)  # 监控间隔
                
            except Exception as e:
                logger.error(f"监控循环异常: {e}")
                time.sleep(5)  # 错误后等待更长时间
    
    def _collect_sensor_data(self) -> Dict:
        """收集所有传感器数据"""
        sensor_data = {
            'camera': {},
            'radar': {},
            'magnetic': {}
        }
        
        # 收集摄像头数据
        for sensor_id, sensor in self.camera_sensors.items():
            data = sensor.get_detection_data()
            if data:
                sensor_data['camera'][sensor_id] = data
        
        # 收集雷达数据
        for sensor_id, sensor in self.radar_sensors.items():
            data = sensor.get_detection_data()
            if data:
                sensor_data['radar'][sensor_id] = data
        
        # 收集地磁数据
        for sensor_id, sensor in self.magnetic_sensors.items():
            data = sensor.get_detection_data()
            if data:
                sensor_data['magnetic'][sensor_id] = data
        
        return sensor_data
    
    def start_adaptive_control(self):
        """启动自适应控制"""
        self.control_thread = threading.Thread(target=self._control_loop, daemon=True)
        self.control_thread.start()
        logger.info("自适应控制线程已启动")
    
    def _control_loop(self):
        """控制循环"""
        while self.is_running:
            try:
                # 执行控制步骤
                if self.latest_fused_data:
                    control_result = self.adaptive_controller.control_step(self.latest_fused_data)
                    self.control_status = self.adaptive_controller.get_control_status()
                    
                    logger.debug(f"控制步骤完成: {control_result.get('action', 'unknown')}")
                
                time.sleep(5)  # 控制间隔（5秒）
                
            except Exception as e:
                logger.error(f"控制循环异常: {e}")
                time.sleep(10)  # 错误后等待更长时间
    
    def start_service(self) -> bool:
        """启动智能交通服务"""
        try:
            logger.info(f"启动智能交通服务 - 路口: {self.intersection_id}")
            
            # 初始化传感器
            if not self.initialize_sensors():
                logger.error("传感器初始化失败")
                return False
            
            # 初始化MQTT
            if not self.initialize_mqtt():
                logger.warning("MQTT初始化失败，继续运行（仅本地模式）")
            
            # 启动传感器
            self.start_sensors()
            
            # 启动监控
            self.start_monitoring()
            
            # 启动自适应控制
            self.start_adaptive_control()
            
            self.is_running = True
            logger.info("智能交通服务启动成功")
            return True
            
        except Exception as e:
            logger.error(f"启动智能交通服务失败: {e}")
            return False
    
    def stop_service(self):
        """停止智能交通服务"""
        logger.info("停止智能交通服务")
        self.is_running = False
        
        # 停止传感器
        for sensor in self.camera_sensors.values():
            sensor.stop_detection()
        for sensor in self.radar_sensors.values():
            sensor.stop_detection()
        for sensor in self.magnetic_sensors.values():
            sensor.stop_detection()
        
        # 断开MQTT连接
        if self.mqtt_client:
            self.mqtt_client.disconnect()
        
        logger.info("智能交通服务已停止")
    
    def get_service_status(self) -> Dict:
        """获取服务状态"""
        return {
            'intersection_id': self.intersection_id,
            'is_running': self.is_running,
            'sensors': {
                'camera': len(self.camera_sensors),
                'radar': len(self.radar_sensors),
                'magnetic': len(self.magnetic_sensors)
            },
            'mqtt_connected': self.mqtt_client.get_connection_status() if self.mqtt_client else False,
            'latest_fused_data': self.latest_fused_data,
            'latest_classification': self.latest_classification,
            'control_status': self.control_status
        }
    
    def manual_control(self, command: Dict) -> Dict:
        """手动控制"""
        try:
            # 这里可以实现手动控制逻辑
            logger.info(f"收到手动控制命令: {command}")
            
            # 发布到MQTT
            if self.mqtt_client.get_connection_status():
                self.mqtt_client.publish_alert({
                    'type': 'manual_control',
                    'command': command,
                    'timestamp': time.time()
                })
            
            return {'status': 'success', 'message': '手动控制命令已接收'}
            
        except Exception as e:
            logger.error(f"手动控制失败: {e}")
            return {'status': 'error', 'message': str(e)}

# 全局服务实例
intelligent_traffic_service = None

def get_intelligent_traffic_service() -> IntelligentTrafficService:
    """获取智能交通服务实例"""
    global intelligent_traffic_service
    if intelligent_traffic_service is None:
        intelligent_traffic_service = IntelligentTrafficService()
    return intelligent_traffic_service
