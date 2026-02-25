from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import datetime

class Lane(BaseModel):
    """车道信息模型"""
    id: str
    direction: str
    vehicle_count: int
    average_speed: float
    queue_length: float
    status: str  # light, normal, congested

class IntersectionStatus(BaseModel):
    """路口交通状态模型"""
    intersection_id: str
    timestamp: datetime.datetime
    lanes: List[Lane]

class Phase(BaseModel):
    """信号灯相位模型"""
    id: str
    name: str
    state: str  # green, yellow, red
    lane_ids: List[str]
    remaining_time: int

class TrafficLightStatus(BaseModel):
    """交通灯状态模型"""
    intersection_id: str
    current_phase: str
    phases: List[Dict[str, Any]]
    timestamp: datetime.datetime

class ControlCommand(BaseModel):
    """控制命令模型"""
    intersection_id: str
    command_type: str
    phase_id: Optional[str] = None
    duration: Optional[int] = None

class ControlLog(BaseModel):
    """控制日志模型"""
    timestamp: datetime.datetime
    operation: str
    details: str

class TrafficHistory(BaseModel):
    """交通历史数据模型"""
    id: int
    intersection_id: str
    lane_id: str
    vehicle_count: int
    average_speed: float
    queue_length: int
    status: str
    timestamp: datetime.datetime