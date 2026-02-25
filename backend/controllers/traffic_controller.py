from flask import Blueprint, jsonify, request
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.traffic_service import TrafficService

# 创建路由蓝图
traffic_bp = Blueprint('traffic', __name__)


@traffic_bp.route('/status/<intersection_id>', methods=['GET'])
def get_traffic_status(intersection_id):
    """获取交通状态"""
    try:
        from services.traffic_service import TrafficService
        service = TrafficService()
        status = service.get_intersection_status(intersection_id)
        return jsonify(status.dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@traffic_bp.route('/light-status/<intersection_id>', methods=['GET'])
def get_light_status(intersection_id):
    """获取信号灯状态"""
    try:
        from services.traffic_service import TrafficService
        service = TrafficService()
        status = service.get_traffic_light_status(intersection_id)
        return jsonify(status.dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@traffic_bp.route('/control/<intersection_id>', methods=['POST'])
def control_traffic_light(intersection_id):
    """控制信号灯"""
    try:
        data = request.get_json()
        command = data.get('command')
        duration = data.get('duration', 30)
        
        from services.traffic_service import TrafficService
        service = TrafficService()
        result = service.control_light(intersection_id, command, duration)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@traffic_bp.route('/overview/<intersection_id>', methods=['GET'])
def get_traffic_overview(intersection_id):
    """获取交通概况数据"""
    try:
        from services.traffic_service import TrafficService
        service = TrafficService()
        overview = service.get_traffic_overview(intersection_id)
        return jsonify(overview)
    except Exception as e:
        return jsonify({'error': str(e)}), 500