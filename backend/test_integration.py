import sys
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import os
import time
import logging

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_intelligent_traffic_service():
    """测试智能交通服务"""
    print("=== 开始测试智能交通服务 ===")
    
    try:
        from services.intelligent_traffic_service import get_intelligent_traffic_service
        
        # 获取服务实例
        service = get_intelligent_traffic_service()
        print(f" 服务实例创建成功 - 路口ID: {service.intersection_id}")
        
        # 测试服务状态
        status = service.get_service_status()
        print(f" 初始服务状态: 运行中={status['is_running']}, 传感器数量={status['sensors']}")
        
        # 启动服务
        print("正在启动智能交通服务...")
        if service.start_service():
            print(" 智能交通服务启动成功")
            
            # 等待服务初始化
            time.sleep(3)
            
            # 检查服务状态
            status = service.get_service_status()
            print(f" 服务运行状态: {status}")
            
            # 测试手动控制
            print("测试手动控制...")
            control_result = service.manual_control({
                'type': 'emergency_override',
                'phase': 'phase_1',
                'duration': 60
            })
            print(f" 手动控制结果: {control_result}")
            
            # 运行一段时间
            print("服务运行中，等待数据收集...")
            for i in range(5):
                time.sleep(2)
                status = service.get_service_status()
                if status.get('latest_fused_data'):
                    print(f" 第{i+1}次数据更新 - 融合数据: {status['latest_fused_data'].get('overall_status', {})}")
                else:
                    print(f"第{i+1}次 - 等待数据...")
            
            # 停止服务
            print("正在停止智能交通服务...")
            service.stop_service()
            print(" 智能交通服务已停止")
            
            return True
            
        else:
            print(" 智能交通服务启动失败")
            return False
            
    except Exception as e:
        print(f" 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_traffic_service_integration():
    """测试交通服务集成"""
    print("\n=== 开始测试交通服务集成 ===")
    
    try:
        from services.traffic_service import TrafficService
        
        # 测试获取交通状态
        status = TrafficService.get_traffic_status("intersection_001")
        print(f" 获取交通状态成功: {len(status.lanes)} 个车道")
        
        # 测试获取信号灯状态
        light_status = TrafficService.get_traffic_light_status("intersection_001")
        print(f" 获取信号灯状态成功: {len(light_status.phases)} 个相位")
        
        # 测试智能状态
        intelligent_status = TrafficService.get_intelligent_status("intersection_001")
        print(f" 获取智能状态成功: 运行中={intelligent_status.get('is_running', False)}")
        
        return True
        
    except Exception as e:
        print(f" 交通服务集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_endpoints():
    """测试API端点"""
    print("\n=== 开始测试API端点 ===")
    
    try:
        from app import app
        # 使用 Flask 自带的测试客户端
        with app.test_client() as client:
            # 测试交通状态API
            response = client.get("/api/traffic/status")
            if response.status_code == 200:
                print(" 交通状态API测试成功")
            else:
                print(f" 交通状态API测试失败: {response.status_code}")
                return False

            # 测试信号灯状态API
            response = client.get("/api/traffic/light/intersection_001")
            if response.status_code == 200:
                print(" 信号灯状态API测试成功")
            else:
                print(f" 信号灯状态API测试失败: {response.status_code}")
                return False

            # 测试智能状态API
            response = client.get("/api/traffic/intelligent/status")
            if response.status_code == 200:
                print(" 智能状态API测试成功")
            else:
                print(f" 智能状态API测试失败: {response.status_code}")
                return False

            # 测试传感器状态API
            response = client.get("/api/traffic/intelligent/sensors")
            if response.status_code == 200:
                print(" 传感器状态API测试成功")
            else:
                print(f" 传感器状态API测试失败: {response.status_code}")
                return False

            return True
    except Exception as e:
        print(f" API端点测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("智能交通系统集成测试")
    print("=" * 50)
    
    results = []
    
    # 测试智能交通服务
    results.append(test_intelligent_traffic_service())
    
    # 测试交通服务集成
    results.append(test_traffic_service_integration())
    
    # 测试API端点
    results.append(test_api_endpoints())
    
    # 总结结果
    print("\n" + "=" * 50)
    print("测试结果总结:")
    print(f"智能交通服务测试: {'通过' if results[0] else '失败'}")
    print(f"交通服务集成测试: {'通过' if results[1] else '失败'}")
    print(f"API端点测试: {'通过' if results[2] else '失败'}")
    
    success_count = sum(results)
    total_count = len(results)
    print(f"\n总体结果: {success_count}/{total_count} 项测试通过")
    
    if success_count == total_count:
        print(" 所有测试通过！智能交通系统集成成功！")
        return 0
    else:
        print(" 部分测试失败，请检查系统配置")
        return 1

if __name__ == "__main__":
    exit(main())
