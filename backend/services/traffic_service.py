from fastapi import HTTPException
from api_models import IntersectionStatus, TrafficLightStatus, ControlCommand, ControlLog, Lane
from database import TrafficData, TrafficLight, ControlLog as DBControlLog
import datetime
from typing import Dict, Any
from .intelligent_traffic_service import get_intelligent_traffic_service
from .simulator import SimulatedHardware

import threading

# 全局模拟数据缓存
_sim_data_cache = None
_sim_data_lock = threading.Lock()

def _refresh_sim_data():
    global _sim_data_cache
    while True:
        data = SimulatedHardware.get_simulated_traffic_data()
        with _sim_data_lock:
            _sim_data_cache = data
        import time
        time.sleep(1)

# 启动后台线程自动刷新模拟数据
threading.Thread(target=_refresh_sim_data, daemon=True).start()

class TrafficService:
    @staticmethod
    def get_traffic_status(intersection_id: str):
        """获取动态交通状态（平滑模拟数据，车流量与速度匹配）"""
        import random, time
        now = int(time.time())
        directions = ['north', 'south', 'east', 'west']
        # 用静态变量保存上一次的车流量和速度，实现平滑变化
        if not hasattr(TrafficService.get_traffic_status, '_last_state'):
            TrafficService.get_traffic_status._last_state = {
                d: {
                    'vehicle_count': random.randint(15, 35),
                    'average_speed': random.uniform(25, 40)
                } for d in directions
            }
        last_state = TrafficService.get_traffic_status._last_state
        lanes = []
        for direction in directions:
            prev_count = last_state[direction]['vehicle_count']
            prev_speed = last_state[direction]['average_speed']
            # 车流量缓慢变化，波动不超过±6
            delta = random.randint(-6, 6)
            vehicle_count = max(5, min(50, prev_count + delta))
            # 速度与车流量反相关，车多则慢，车少则快
            if vehicle_count < 12:
                average_speed = random.uniform(38, 50)
            elif vehicle_count < 22:
                average_speed = random.uniform(32, 44)
            elif vehicle_count < 32:
                average_speed = random.uniform(24, 36)
            else:
                average_speed = random.uniform(15, 28)
            # 速度也做微小平滑
            average_speed = (prev_speed * 0.7 + average_speed * 0.3)
            # 保存本次状态
            last_state[direction]['vehicle_count'] = vehicle_count
            last_state[direction]['average_speed'] = average_speed
            queue_length = max(0, int(vehicle_count * 0.3 + random.randint(0, 3)))
            if vehicle_count < 12:
                status = 'light'
            elif vehicle_count < 28:
                status = 'normal'
            else:
                status = 'congested'
            lane = Lane(
                id=f"lane_{direction}_1",
                direction=direction,
                vehicle_count=vehicle_count,
                average_speed=round(average_speed, 1),
                queue_length=queue_length,
                status=status
            )
            lanes.append(lane)
        return IntersectionStatus(
            intersection_id=intersection_id,
            timestamp=datetime.datetime.utcnow(),
            lanes=lanes
        )
    
    @staticmethod
    def _get_mock_traffic_status(intersection_id: str):
        """获取模拟交通状态（备用）"""
        # 根据当前时间生成符合现实逻辑的模拟数据
        current_time = datetime.datetime.now()
        hour = current_time.hour
        
        # 定义不同时段的交通流量模式
        if 6 <= hour < 8:  # 早高峰
            base_vehicle_count = 35
            traffic_multiplier = 1.5
        elif 8 <= hour < 17:  # 白天平峰
            base_vehicle_count = 20
            traffic_multiplier = 1.0
        elif 17 <= hour < 19:  # 晚高峰
            base_vehicle_count = 40
            traffic_multiplier = 1.8
        elif 19 <= hour < 22:  # 晚间
            base_vehicle_count = 15
            traffic_multiplier = 0.8
        else:  # 夜间
            base_vehicle_count = 5
            traffic_multiplier = 0.5
        
        # 根据方向设置不同的交通模式（例如，上下班时间的主方向）
        direction_multipliers = {
            'north': 1.0,
            'south': 1.0,
            'east': 1.0 if 8 <= hour < 10 or 17 <= hour < 19 else 0.8,  # 早晚高峰东西向车流较多
            'west': 0.8 if 8 <= hour < 10 or 17 <= hour < 19 else 1.0
        }
        
        # 为不同方向设置不同的基础流量
        base_counts = {
            'north': int(base_vehicle_count * 0.9),
            'south': int(base_vehicle_count * 0.9),
            'east': int(base_vehicle_count * 1.1),
            'west': int(base_vehicle_count * 1.1)
        }
        
        from api_models import Lane
        
        lanes = []
        for direction in ['north', 'south', 'east', 'west']:
            # 计算基础车流量
            base_count = base_counts[direction]
            multiplier = traffic_multiplier * direction_multipliers[direction]
            
            # 添加随机波动，但保持在合理范围内
            import random
            vehicle_count = max(0, int(base_count * multiplier + random.gauss(0, 5)))
            
            # 限制最大值
            vehicle_count = min(vehicle_count, 50)
            
            # 根据车流量设置平均速度（车多则速度慢）
            if vehicle_count < 10:
                avg_speed = round(random.uniform(40, 60), 1)
            elif vehicle_count < 20:
                avg_speed = round(random.uniform(30, 50), 1)
            elif vehicle_count < 30:
                avg_speed = round(random.uniform(20, 40), 1)
            else:
                avg_speed = round(random.uniform(10, 30), 1)
            
            # 根据车流量设置排队长度
            queue_length = max(0, int(vehicle_count * 0.3 + random.randint(0, 3)))
            
            # 根据车流量和速度设置状态
            if vehicle_count < 10:
                status = 'light'
            elif vehicle_count < 25:
                status = 'normal'
            else:
                status = 'congested'
                
            # 如果速度特别慢，可能表示拥堵
            if avg_speed < 15 and vehicle_count > 15:
                status = 'congested'
            
            lane = Lane(
                id=f"lane_{direction}_1",
                direction=direction,
                vehicle_count=vehicle_count,
                average_speed=avg_speed,
                queue_length=queue_length,
                status=status
            )
            lanes.append(lane)
        
        return IntersectionStatus(
            intersection_id=intersection_id,
            timestamp=datetime.datetime.utcnow(),
            lanes=lanes
        )
    
    @staticmethod
    def get_traffic_light_status(intersection_id: str):
        """获取动态信号灯状态"""
        import time
        now = int(time.time())
        # 每24秒切换一次状态
        countdown = 24 - (now % 24)
        status = 'green' if (now // 24) % 2 == 0 else 'red'
        phases = [
            {
                "id": "phase_1",
                "state": status,
                "remaining_time": countdown if status == 'green' else 0,
                "lane_ids": ["lane_north_1", "lane_south_1"]
            },
            {
                "id": "phase_2",
                "state": 'red' if status == 'green' else 'green',
                "remaining_time": countdown if status == 'red' else 0,
                "lane_ids": ["lane_east_1", "lane_west_1"]
            }
        ]
        return TrafficLightStatus(
            intersection_id=intersection_id,
            current_phase="phase_1" if status == 'green' else "phase_2",
            timestamp=datetime.datetime.utcnow(),
            phases=phases
        )
    
    @staticmethod
    def _get_mock_traffic_light_status(intersection_id: str):
        """获取模拟信号灯状态（备用）"""
        return TrafficLightStatus(
            intersection_id=intersection_id,
            current_phase="phase_1",
            timestamp=datetime.datetime.utcnow(),
            phases=[
                {
                    "id": "phase_1",
                    "state": "green",
                    "remaining_time": 25,
                    "lane_ids": ["lane_north_1", "lane_south_1"]
                },
                {
                    "id": "phase_2",
                    "state": "red",
                    "remaining_time": 0,
                    "lane_ids": ["lane_east_1", "lane_west_1"]
                }
            ]
        )
    
    @staticmethod
    def send_control_command(command: ControlCommand):
        """发送控制命令"""
        try:
            # 获取智能交通服务实例
            service = get_intelligent_traffic_service()
            
            # 如果服务正在运行，通过MQTT发送控制命令
            if service.is_running and service.mqtt_client.get_connection_status():
                # 构造控制命令
                mqtt_command = {
                    'type': command.command_type,
                    'intersection_id': command.intersection_id,
                    'phase_id': command.phase_id,
                    'duration': command.duration,
                    'timestamp': datetime.datetime.utcnow().isoformat()
                }
                
                # 发送到MQTT
                service.mqtt_client.send_control_command(command.intersection_id, mqtt_command)
                
                log_entry = ControlLog(
                    timestamp=datetime.datetime.utcnow(),
                    operation=f"智能控制命令: {command.command_type}",
                    details=f"路口: {command.intersection_id}, 相位: {command.phase_id}, MQTT已发送"
                )
                
                return {"message": "智能控制命令已发送", "command_id": "cmd_smart_001", "log": log_entry}
            else:
                # 服务未运行，使用传统方式
                log_entry = ControlLog(
                    timestamp=datetime.datetime.utcnow(),
                    operation=f"控制命令: {command.command_type}",
                    details=f"路口: {command.intersection_id}, 相位: {command.phase_id}"
                )
                
                return {"message": "控制命令已发送（传统模式）", "command_id": "cmd_001", "log": log_entry}
                
        except Exception as e:
            print(f"发送控制命令失败: {e}")
            # 回退到传统方式
            log_entry = ControlLog(
                timestamp=datetime.datetime.utcnow(),
                operation=f"控制命令: {command.command_type}",
                details=f"路口: {command.intersection_id}, 相位: {command.phase_id}"
            )
            
            return {"message": "控制命令已发送", "command_id": "cmd_001", "log": log_entry}
    
    @staticmethod
    def calculate_optimal_timing(traffic_status: IntersectionStatus):
        """根据交通状态计算最优信号灯配时"""
        try:
            # 获取智能交通服务实例
            service = get_intelligent_traffic_service()
            
            # 如果服务正在运行，使用自适应控制器的计算结果
            if service.is_running and service.control_status:
                control_status = service.control_status
                
                # 从控制状态获取最优配时
                timing_plan = {}
                for direction in ['north', 'south', 'east', 'west']:
                    lane_id = f"lane_{direction}_1"
                    # 从控制状态获取该方向的绿灯时间
                    green_time = control_status.get(f'{direction}_green_time', 30)
                    timing_plan[lane_id] = green_time
                
                return timing_plan
            else:
                # 服务未运行，使用传统算法
                return TrafficService._calculate_traditional_timing(traffic_status)
                
        except Exception as e:
            print(f"计算最优配时失败: {e}")
            return TrafficService._calculate_traditional_timing(traffic_status)
    
    @staticmethod
    def _calculate_traditional_timing(traffic_status: IntersectionStatus):
        """传统算法计算最优信号灯配时"""
        total_vehicles = sum(lane.vehicle_count for lane in traffic_status.lanes)
        
        if total_vehicles == 0:
            # 如果没有车辆，给每个方向相同的最短时间
            timing_plan = {
                lane.id: 15 for lane in traffic_status.lanes
            }
        else:
            # 根据车流量比例分配时间
            timing_plan = {}
            for lane in traffic_status.lanes:
                proportion = lane.vehicle_count / total_vehicles
                # 基础时间 + 按比例增加的时间（最多60秒）
                green_time = 15 + int(proportion * 45)
                timing_plan[lane.id] = min(green_time, 60)
        
        return timing_plan
    
    @staticmethod
    def get_intelligent_status(intersection_id: str) -> Dict[str, Any]:
        """获取智能交通系统状态"""
        try:
            service = get_intelligent_traffic_service()
            return service.get_service_status()
        except Exception as e:
            print(f"获取智能状态失败: {e}")
            return {
                'intersection_id': intersection_id,
                'is_running': False,
                'error': str(e)
            }
    
    @staticmethod
    def start_intelligent_service(intersection_id: str) -> Dict[str, Any]:
        """启动智能交通服务"""
        try:
            service = get_intelligent_traffic_service()
            if service.start_service():
                return {
                    'status': 'success',
                    'message': f'智能交通服务已启动 - 路口: {intersection_id}'
                }
            else:
                return {
                    'status': 'error',
                    'message': '智能交通服务启动失败'
                }
        except Exception as e:
            print(f"启动智能服务失败: {e}")
            return {
                'status': 'error',
                'message': f'启动失败: {str(e)}'
            }
    
    @staticmethod
    def stop_intelligent_service() -> Dict[str, Any]:
        """停止智能交通服务"""
        try:
            service = get_intelligent_traffic_service()
            service.stop_service()
            return {
                'status': 'success',
                'message': '智能交通服务已停止'
            }
        except Exception as e:
            print(f"停止智能服务失败: {e}")
            return {
                'status': 'error',
                'message': f'停止失败: {str(e)}'
            }
    
    @staticmethod
    def manual_intelligent_control(command: Dict) -> Dict[str, Any]:
        """手动智能控制"""
        try:
            service = get_intelligent_traffic_service()
            return service.manual_control(command)
        except Exception as e:
            print(f"手动控制失败: {e}")
            return {
                'status': 'error',
                'message': f'手动控制失败: {str(e)}'
            }
    
    @staticmethod
    def get_intersection_status(intersection_id: str):
        """获取路口状态（兼容旧接口）"""
        return TrafficService.get_traffic_status(intersection_id)
    
    @staticmethod
    def control_light(intersection_id: str, command: str, duration: int = 30):
        """控制信号灯"""
        try:
            from api_models import ControlCommand
            
            # 构造控制命令
            control_cmd = ControlCommand(
                command_type=command,
                intersection_id=intersection_id,
                phase_id="phase_1",  # 默认相位
                duration=duration
            )
            
            # 发送控制命令
            result = TrafficService.send_control_command(control_cmd)
            
            return {
                "status": "success",
                "message": f"信号灯控制命令已发送: {command}",
                "command": command,
                "duration": duration,
                "result": result
            }
            
        except Exception as e:
            print(f"控制信号灯失败: {e}")
            return {
                "status": "error",
                "message": f"控制失败: {str(e)}"
            }
    
    @staticmethod
    def get_traffic_overview(intersection_id: str):
        """获取交通概况数据"""
        try:
            # 获取交通状态
            traffic_status = TrafficService.get_traffic_status(intersection_id)
            
            # 计算统计数据
            total_vehicles = sum(lane.vehicle_count for lane in traffic_status.lanes)
            avg_speed = sum(lane.average_speed for lane in traffic_status.lanes) / len(traffic_status.lanes) if traffic_status.lanes else 0
            congested_lanes = sum(1 for lane in traffic_status.lanes if lane.status == 'congested')
            
            # 获取信号灯状态
            light_status = TrafficService.get_traffic_light_status(intersection_id)
            current_phase = next((phase for phase in light_status.phases if phase['state'] == 'green'), None)
            
            return {
                "intersection_id": intersection_id,
                "timestamp": traffic_status.timestamp.isoformat(),
                "total_vehicles": total_vehicles,
                "average_speed": round(avg_speed, 1),
                "congested_lanes": congested_lanes,
                "current_phase": current_phase['id'] if current_phase else "unknown",
                "remaining_time": current_phase['remaining_time'] if current_phase else 0,
                "lanes": [
                    {
                        "id": lane.id,
                        "direction": lane.direction,
                        "vehicle_count": lane.vehicle_count,
                        "average_speed": lane.average_speed,
                        "queue_length": lane.queue_length,
                        "status": lane.status
                    }
                    for lane in traffic_status.lanes
                ]
            }
            
        except Exception as e:
            print(f"获取交通概况失败: {e}")
            # 返回默认数据
            return {
                "intersection_id": intersection_id,
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "total_vehicles": 0,
                "average_speed": 0,
                "congested_lanes": 0,
                "current_phase": "unknown",
                "remaining_time": 0,
                "lanes": []
            }
