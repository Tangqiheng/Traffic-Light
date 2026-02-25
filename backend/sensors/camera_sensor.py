import cv2
import numpy as np
from ultralytics import YOLO
import time
from typing import List, Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class CameraSensor:
    def __init__(self, camera_id: str, video_source: Optional[str] = None):
        self.camera_id = camera_id
        self.video_source = video_source or 0  # 默认使用摄像头0
        self.cap = None
        self.model = None
        self.is_running = False
        
        # 车辆检测参数
        self.confidence_threshold = 0.5
        self.vehicle_classes = ['car', 'truck', 'bus', 'motorcycle']
        
        # 检测结果缓存
        self.last_detection = {
            'timestamp': 0,
            'vehicles': [],
            'queue_length': 0,
            'average_speed': 0.0
        }
        
    def initialize(self) -> bool:
        try:
            # 初始化摄像头
            self.cap = cv2.VideoCapture(self.video_source)
            if not self.cap.isOpened():
                logger.error(f"无法打开摄像头 {self.video_source}")
                return False
                
            # 加载YOLO模型
            self.model = YOLO('yolov8n.pt')  # 使用轻量级模型
            logger.info(f"摄像头传感器 {self.camera_id} 初始化成功")
            return True
            
        except Exception as e:
            logger.error(f"摄像头传感器初始化失败: {e}")
            return False
    
    def start_detection(self):
        if not self.initialize():
            return
            
        self.is_running = True
        logger.info(f"开始车辆检测 - 摄像头 {self.camera_id}")
        
        try:
            while self.is_running:
                if self.cap is None or not self.cap.isOpened():
                    logger.warning("摄像头未正确初始化或已关闭")
                    time.sleep(0.1)
                    continue
                ret, frame = self.cap.read()
                if not ret:
                    logger.warning("无法读取摄像头帧")
                    time.sleep(0.1)
                    continue
                
                # 进行车辆检测
                detection_result = self._detect_vehicles(frame)
                
                # 更新检测结果
                self.last_detection = {
                    'timestamp': time.time(),
                    'vehicles': detection_result['vehicles'],
                    'queue_length': detection_result['queue_length'],
                    'average_speed': detection_result['average_speed']
                }
                
                # 可视化检测结果（可选）
                if detection_result['vehicles']:
                    self._visualize_detection(frame, detection_result['vehicles'])
                
                time.sleep(0.1)  # 控制检测频率
                
        except Exception as e:
            logger.error(f"车辆检测过程中出错: {e}")
        finally:
            self.stop_detection()
    
    def _detect_vehicles(self, frame: np.ndarray) -> Dict:
        try:
            # 检查模型是否已加载
            if self.model is None:
                logger.error("YOLO模型未加载，无法进行车辆检测")
                return {'vehicles': [], 'queue_length': 0, 'average_speed': 0.0}
            # 使用YOLO进行检测
            results = self.model(frame, conf=self.confidence_threshold)
            
            vehicles = []
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    cls = int(box.cls[0])
                    class_name = self.model.names[cls]
                    
                    if class_name in self.vehicle_classes:
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        confidence = float(box.conf[0])
                        
                        vehicle = {
                            'class': class_name,
                            'bbox': [x1, y1, x2, y2],
                            'confidence': confidence,
                            'speed': self._estimate_speed(box)  # 简化的速度估算
                        }
                        vehicles.append(vehicle)
            
            # 计算队列长度和平均速度
            queue_length = len(vehicles)
            average_speed = np.mean([v['speed'] for v in vehicles]) if vehicles else 0.0
            
            return {
                'vehicles': vehicles,
                'queue_length': queue_length,
                'average_speed': average_speed
            }
            
        except Exception as e:
            logger.error(f"车辆检测失败: {e}")
            return {'vehicles': [], 'queue_length': 0, 'average_speed': 0.0}
    
    def _estimate_speed(self, box) -> float:
        # 简化的速度估算（实际应使用跟踪算法）
        # 这里返回一个随机速度作为示例
        return np.random.uniform(20, 60)  # 20-60 km/h
    
    def _visualize_detection(self, frame: np.ndarray, vehicles: List[Dict]):
        for vehicle in vehicles:
            x1, y1, x2, y2 = vehicle['bbox']
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
            
            label = f"{vehicle['class']}: {vehicle['confidence']:.2f}"
            cv2.putText(frame, label, (int(x1), int(y1)-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # 显示队列长度
        cv2.putText(frame, f"Queue: {len(vehicles)}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        
        cv2.imshow(f'Camera {self.camera_id}', frame)
        cv2.waitKey(1)
    
    def get_detection_data(self) -> Dict:
        return self.last_detection
    
    def stop_detection(self):
        self.is_running = False
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        logger.info(f"停止车辆检测 - 摄像头 {self.camera_id}")

# 模拟摄像头传感器（用于测试）
class MockCameraSensor(CameraSensor):
    def __init__(self, camera_id: str):
        super().__init__(camera_id, video_source=None)
        self.mock_data = self._generate_mock_data()
    
    def _generate_mock_data(self):
        return {
            'vehicles': [
                {'class': 'car', 'bbox': [100, 200, 200, 250], 'confidence': 0.85, 'speed': 35.2},
                {'class': 'truck', 'bbox': [300, 180, 450, 280], 'confidence': 0.92, 'speed': 28.5}
            ],
            'queue_length': 2,
            'average_speed': 31.85
        }
    
    def initialize(self) -> bool:
        logger.info(f"模拟摄像头传感器 {self.camera_id} 初始化成功")
        return True
    
    def start_detection(self):
        self.is_running = True
        logger.info(f"开始模拟车辆检测 - 摄像头 {self.camera_id}")
        
        while self.is_running:
            self.last_detection = {
                'timestamp': time.time(),
                **self.mock_data
            }
            # 添加一些随机变化
            self.mock_data['queue_length'] = max(0, self.mock_data['queue_length'] + np.random.randint(-1, 2))
            time.sleep(1)
    
    def _detect_vehicles(self, frame=None):
        return self.mock_data
