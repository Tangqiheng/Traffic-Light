from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from api_models import IntersectionStatus, TrafficLightStatus, ControlCommand, ControlLog
from services.traffic_service import TrafficService
import datetime

router = APIRouter(prefix="/api/traffic")

# 模拟数据库存储
intersection_data = {}
traffic_light_data = {}
control_logs = []

@router.get("/status", response_model=IntersectionStatus)
async def get_traffic_status(intersection_id: str = "intersection_001"):
    """获取交通状态信息"""
    try:
        return TrafficService.get_traffic_status(intersection_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取交通状态失败: {str(e)}")

@router.get("/light/{intersection_id}", response_model=TrafficLightStatus)
async def get_traffic_light_status(intersection_id: str):
    """获取信号灯状态"""
    try:
        return TrafficService.get_traffic_light_status(intersection_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取信号灯状态失败: {str(e)}")

@router.post("/control")
async def send_control_command(command: ControlCommand):
    """发送控制命令"""
    try:
        result = TrafficService.send_control_command(command)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"发送控制命令失败: {str(e)}")

@router.get("/logs", response_model=List[ControlLog])
async def get_control_logs(limit: int = 10):
    """获取控制日志"""
    # 返回最新的日志条目
    return control_logs[-limit:] if len(control_logs) > limit else control_logs

# 智能交通系统API端点

@router.get("/intelligent/status")
async def get_intelligent_status(intersection_id: str = "intersection_001"):
    """获取智能交通系统状态"""
    try:
        return TrafficService.get_intelligent_status(intersection_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取智能状态失败: {str(e)}")

@router.post("/intelligent/start")
async def start_intelligent_service(intersection_id: str = "intersection_001"):
    """启动智能交通服务"""
    try:
        result = TrafficService.start_intelligent_service(intersection_id)
        if result['status'] == 'error':
            raise HTTPException(status_code=500, detail=result['message'])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"启动智能服务失败: {str(e)}")

@router.post("/intelligent/stop")
async def stop_intelligent_service():
    """停止智能交通服务"""
    try:
        result = TrafficService.stop_intelligent_service()
        if result['status'] == 'error':
            raise HTTPException(status_code=500, detail=result['message'])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"停止智能服务失败: {str(e)}")

@router.post("/intelligent/control")
async def manual_intelligent_control(command: Dict[str, Any]):
    """手动智能控制"""
    try:
        result = TrafficService.manual_intelligent_control(command)
        if result['status'] == 'error':
            raise HTTPException(status_code=400, detail=result['message'])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"手动控制失败: {str(e)}")

@router.get("/intelligent/fused-data")
async def get_fused_sensor_data():
    """获取传感器融合数据"""
    try:
        service = TrafficService.get_intelligent_status("intersection_001")
        if not service.get('is_running', False):
            return {"message": "智能服务未运行", "data": None}
        
        return {
            "fused_data": service.get('latest_fused_data', {}),
            "classification": service.get('latest_classification', {}),
            "control_status": service.get('control_status', {})
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取融合数据失败: {str(e)}")

@router.get("/intelligent/sensors")
async def get_sensor_status():
    """获取传感器状态"""
    try:
        service = TrafficService.get_intelligent_status("intersection_001")
        return {
            "sensors": service.get('sensors', {}),
            "mqtt_connected": service.get('mqtt_connected', False)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取传感器状态失败: {str(e)}")

@router.post("/intelligent/timing/calculate")
async def calculate_optimal_timing(traffic_status: IntersectionStatus):
    """计算最优信号灯配时"""
    try:
        timing_plan = TrafficService.calculate_optimal_timing(traffic_status)
        return {
            "timing_plan": timing_plan,
            "total_vehicles": sum(lane.vehicle_count for lane in traffic_status.lanes)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"计算最优配时失败: {str(e)}")
