import numpy as np
import time
from typing import List, Dict, Tuple
from collections import defaultdict
import logging
from scipy.optimize import linear_sum_assignment
from filterpy.kalman import KalmanFilter
from filterpy.common import Q_discrete_white_noise

logger = logging.getLogger(__name__)

class SensorFusion:
    def __init__(self, intersection_id: str):
        self.intersection_id = intersection_id
        
        # 传感器数据缓存
        self.camera_data = {}
        self.radar_data = {}
        self.magnetic_data = {}
        
        # 融合结果
        self.fused_data = {
            'timestamp': 0,
            'lanes': {},
            'overall_status': {}
        }
        
        # 卡尔曼滤波器用于跟踪
        self.trackers = {}  # lane_id -> {vehicle_id: kalman_filter}
        self.next_vehicle_id = 0
        
        # 融合参数
        self.max_association_distance = 10.0  # 最大关联距离（米）
        self.confidence_weights = {
            'camera': 0.4,
            'radar': 0.4,
            'magnetic': 0.2
        }
    
    def update_sensor_data(self, sensor_type: str, sensor_id: str, data: Dict):
        """更新传感器数据"""
        if sensor_type == 'camera':
            self.camera_data[sensor_id] = data
        elif sensor_type == 'radar':
            self.radar_data[sensor_id] = data
        elif sensor_type == 'magnetic':
            self.magnetic_data[sensor_id] = data
        
        # 触发数据融合
        self._fuse_sensor_data()
    
    def _fuse_sensor_data(self):
        """融合多传感器数据"""
        try:
            current_time = time.time()
            
            # 获取所有车道信息
            lanes = self._get_lane_configuration()
            
            fused_lanes = {}
            
            for lane_id, lane_info in lanes.items():
                lane_data = self._fuse_lane_data(lane_id, lane_info)
                fused_lanes[lane_id] = lane_data
            
            # 计算整体路口状态
            overall_status = self._calculate_overall_status(fused_lanes)
            
            self.fused_data = {
                'timestamp': current_time,
                'lanes': fused_lanes,
                'overall_status': overall_status
            }
            
        except Exception as e:
            logger.error(f"传感器数据融合失败: {e}")
    
    def _get_lane_configuration(self) -> Dict:
        """获取路口车道配置"""
        # 这里应该从配置文件或数据库获取实际的车道配置
        # 暂时使用固定的十字路口配置
        return {
            'north_straight': {'direction': 'north', 'type': 'straight', 'sensors': ['cam_north', 'radar_north', 'mag_north']},
            'north_left': {'direction': 'north', 'type': 'left', 'sensors': ['cam_north', 'radar_north', 'mag_north']},
            'south_straight': {'direction': 'south', 'type': 'straight', 'sensors': ['cam_south', 'radar_south', 'mag_south']},
            'south_left': {'direction': 'south', 'type': 'left', 'sensors': ['cam_south', 'radar_south', 'mag_south']},
            'east_straight': {'direction': 'east', 'type': 'straight', 'sensors': ['cam_east', 'radar_east', 'mag_east']},
            'east_left': {'direction': 'east', 'type': 'left', 'sensors': ['cam_east', 'radar_east', 'mag_east']},
            'west_straight': {'direction': 'west', 'type': 'straight', 'sensors': ['cam_west', 'radar_west', 'mag_west']},
            'west_left': {'direction': 'west', 'type': 'left', 'sensors': ['cam_west', 'radar_west', 'mag_west']}
        }
    
    def _fuse_lane_data(self, lane_id: str, lane_info: Dict) -> Dict:
        """融合单个车道的数据"""
        # 收集该车道的所有传感器数据
        camera_vehicles = []
        radar_targets = []
        magnetic_status = None
        
        sensors = lane_info['sensors']
        
        # 从摄像头数据中提取该车道的车辆
        for cam_id, cam_data in self.camera_data.items():
            if cam_id in sensors and cam_data.get('vehicles'):
                # 过滤属于该车道的车辆（简化处理）
                camera_vehicles.extend(cam_data['vehicles'])
        
        # 从雷达数据中提取该车道的目标
        for radar_id, radar_data in self.radar_data.items():
            if radar_id in sensors and radar_data.get('targets'):
                # 根据角度过滤属于该车道的目标
                lane_angle_range = self._get_lane_angle_range(lane_info['direction'])
                filtered_targets = [
                    target for target in radar_data['targets']
                    if lane_angle_range[0] <= target['angle'] <= lane_angle_range[1]
                ]
                radar_targets.extend(filtered_targets)
        
        # 获取地磁传感器数据
        for mag_id, mag_data in self.magnetic_data.items():
            if mag_id in sensors:
                magnetic_status = mag_data
                break
        
        # 执行数据关联和融合
        fused_vehicles = self._associate_and_fuse(
            camera_vehicles, radar_targets, magnetic_status, lane_id
        )
        
        # 计算车道统计信息
        queue_length = len(fused_vehicles)
        average_speed = np.mean([v.get('speed', 0) for v in fused_vehicles]) if fused_vehicles else 0.0
        occupancy_rate = magnetic_status.get('occupancy_rate', 0.0) if magnetic_status else 0.0
        
        return {
            'lane_id': lane_id,
            'direction': lane_info['direction'],
            'type': lane_info['type'],
            'vehicles': fused_vehicles,
            'queue_length': queue_length,
            'average_speed': average_speed,
            'occupancy_rate': occupancy_rate,
            'traffic_density': len(radar_targets) / 100.0 if radar_targets else 0.0  # 简化的密度计算
        }
    
    def _get_lane_angle_range(self, direction: str) -> Tuple[float, float]:
        """获取车道对应的角度范围"""
        angle_ranges = {
            'north': (-45, 45),
            'south': (135, 225),
            'east': (45, 135),
            'west': (-135, -45)
        }
        return angle_ranges.get(direction, (-180, 180))
    
    def _associate_and_fuse(self, camera_vehicles: List, radar_targets: List, 
                           magnetic_status: Dict, lane_id: str) -> List[Dict]:
        """关联和融合多传感器数据"""
        if not camera_vehicles and not radar_targets:
            return []
        
        # 初始化或获取该车道的跟踪器
        if lane_id not in self.trackers:
            self.trackers[lane_id] = {}
        
        trackers = self.trackers[lane_id]
        
        # 简化的数据关联（实际应使用更复杂的算法）
        fused_vehicles = []
        
        # 处理摄像头检测到的车辆
        for cam_vehicle in camera_vehicles:
            # 查找匹配的雷达目标
            matched_radar = self._find_matching_radar_target(cam_vehicle, radar_targets)
            
            fused_vehicle = {
                'id': self._get_or_create_vehicle_id(lane_id, cam_vehicle),
                'class': cam_vehicle.get('class', 'unknown'),
                'position': cam_vehicle.get('bbox', [0, 0, 0, 0]),
                'confidence': cam_vehicle.get('confidence', 0.0),
                'speed': cam_vehicle.get('speed', 0.0),
                'source': 'camera'
            }
            
            if matched_radar:
                # 融合雷达数据
                fused_vehicle['speed'] = (
                    self.confidence_weights['camera'] * cam_vehicle.get('speed', 0) +
                    self.confidence_weights['radar'] * matched_radar.get('speed', 0)
                )
                fused_vehicle['source'] = 'camera+radar'
                # 移除已匹配的雷达目标
                if matched_radar in radar_targets:
                    radar_targets.remove(matched_radar)
            
            fused_vehicles.append(fused_vehicle)
        
        # 处理剩余的雷达目标（没有匹配摄像头检测的）
        for radar_target in radar_targets:
            fused_vehicle = {
                'id': self._get_or_create_vehicle_id(lane_id, radar_target),
                'class': 'unknown',  # 雷达无法识别车辆类型
                'position': None,  # 雷达没有位置信息
                'confidence': 0.8,  # 雷达检测的置信度
                'speed': radar_target.get('speed', 0.0),
                'distance': radar_target.get('distance', 0.0),
                'angle': radar_target.get('angle', 0.0),
                'source': 'radar'
            }
            fused_vehicles.append(fused_vehicle)
        
        # 更新卡尔曼滤波器进行跟踪
        self._update_trackers(lane_id, fused_vehicles)
        
        return fused_vehicles
    
    def _find_matching_radar_target(self, camera_vehicle: Dict, radar_targets: List) -> Dict:
        """查找与摄像头车辆匹配的雷达目标"""
        if not radar_targets:
            return None
        
        # 简化的匹配逻辑：基于速度相似性
        cam_speed = camera_vehicle.get('speed', 0)
        
        best_match = None
        min_speed_diff = float('inf')
        
        for radar_target in radar_targets:
            radar_speed = radar_target.get('speed', 0)
            speed_diff = abs(cam_speed - radar_speed)
            
            if speed_diff < min_speed_diff and speed_diff < 10:  # 速度差异小于10km/h
                min_speed_diff = speed_diff
                best_match = radar_target
        
        return best_match
    
    def _get_or_create_vehicle_id(self, lane_id: str, detection: Dict) -> int:
        """获取或创建车辆ID"""
        # 简化的ID分配逻辑
        vehicle_id = self.next_vehicle_id
        self.next_vehicle_id += 1
        return vehicle_id
    
    def _update_trackers(self, lane_id: str, vehicles: List[Dict]):
        """更新卡尔曼滤波器跟踪器"""
        # 这里应该实现卡尔曼滤波跟踪逻辑
        # 暂时简化处理
        pass
    
    def _calculate_overall_status(self, lanes: Dict) -> Dict:
        """计算路口整体状态"""
        total_vehicles = sum(lane['queue_length'] for lane in lanes.values())
        total_occupancy = np.mean([lane['occupancy_rate'] for lane in lanes.values()])
        avg_speed = np.mean([lane['average_speed'] for lane in lanes.values() if lane['average_speed'] > 0])
        
        # 确定交通状态
        if total_vehicles < 5:
            traffic_status = 'free'
        elif total_vehicles < 15:
            traffic_status = 'normal'
        elif total_vehicles < 25:
            traffic_status = 'congested'
        else:
            traffic_status = 'heavy_congested'
        
        return {
            'total_vehicles': total_vehicles,
            'average_occupancy': total_occupancy,
            'average_speed': avg_speed,
            'traffic_status': traffic_status,
            'congestion_level': self._calculate_congestion_level(traffic_status)
        }
    
    def _calculate_congestion_level(self, traffic_status: str) -> float:
        """计算拥堵等级（0-1）"""
        levels = {
            'free': 0.0,
            'normal': 0.2,
            'congested': 0.6,
            'heavy_congested': 1.0
        }
        return levels.get(traffic_status, 0.0)
    
    def get_fused_data(self) -> Dict:
        """获取融合后的数据"""
        return self.fused_data.copy()
    
    def reset_trackers(self):
        """重置所有跟踪器"""
        self.trackers.clear()
        self.next_vehicle_id = 0
        logger.info("重置传感器融合跟踪器")
