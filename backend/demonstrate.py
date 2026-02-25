import time
import logging
from services.intelligent_traffic_service import get_intelligent_traffic_service

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def demonstrate_system():
    """演示智能交通系统运行"""
    print("=" * 60)
    print("多模态智能交通灯控制系统演示")
    print("=" * 60)
    
    # 获取服务实例
    service = get_intelligent_traffic_service()
    print(f" 系统初始化完成 - 路口ID: {service.intersection_id}")
    
    # 启动智能交通服务
    print("\n 启动智能交通服务...")
    if service.start_service():
        print(" 智能交通服务启动成功")
        
        # 演示运行过程
        print("\n 系统运行状态监控:")
        print("-" * 40)
        
        for i in range(10):
            status = service.get_service_status()
            
            print(f"时间: {time.strftime('%H:%M:%S')}")
            print(f"  运行状态: {'运行中' if status['is_running'] else '已停止'}")
            print(f"  传感器数量: 摄像头{status['sensors']['camera']}个, 雷达{status['sensors']['radar']}个, 地磁{status['sensors']['magnetic']}个")
            print(f"  MQTT连接: {'已连接' if status['mqtt_connected'] else '未连接'}")
            
            if status.get('latest_fused_data'):
                fused_data = status['latest_fused_data']
                overall = fused_data.get('overall_status', {})
                print(f"  融合数据: 总车辆数{overall.get('total_vehicles', 0)}, 平均速度{overall.get('average_speed', 0):.1f}km/h")
            
            if status.get('latest_classification'):
                classification = status['latest_classification']
                print(f"  交通状态: {classification.get('state', '未知')} (置信度{classification.get('confidence', 0):.2f})")
            
            if status.get('control_status'):
                control = status['control_status']
                print(f"  控制状态: 当前相位{control.get('current_phase', '未知')}, 剩余时间{control.get('remaining_time', 0)}秒")
            
            print("-" * 40)
            time.sleep(3)
        
        # 演示手动控制
        print("\n 演示手动控制功能...")
        control_result = service.manual_control({
            'type': 'emergency_override',
            'phase': 'phase_1',
            'duration': 30
        })
        print(f" 手动控制结果: {control_result}")
        
        # 停止服务
        print("\n 停止智能交通服务...")
        service.stop_service()
        print(" 智能交通服务已停止")
        
        print("\n" + "=" * 60)
        print(" 演示完成！多模态智能交通系统运行正常")
        print("=" * 60)
        
    else:
        print(" 智能交通服务启动失败")

if __name__ == "__main__":
    demonstrate_system()
