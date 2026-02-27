#!/usr/bin/env python3
"""测试DRLTrafficController导入"""
import sys
try:
    from controllers.drl_traffic_controller import DRLTrafficController
    print("成功导入 DRLTrafficController")
    
    # 测试实例化
    controller = DRLTrafficController("test_intersection")
    print("成功创建 DRLTrafficController 实例")
    
    # 测试基本方法
    dummy_data = {
        'north_straight': 10, 'south_straight': 5,
        'east_straight': 8, 'west_straight': 12,
        'north_left': 3, 'south_left': 2,
        'east_left': 4, 'west_left': 1,
        'north_straight_wait': 15, 'south_straight_wait': 10,
        'east_straight_wait': 20, 'west_straight_wait': 25,
        'north_left_wait': 5, 'south_left_wait': 3,
        'east_left_wait': 8, 'west_left_wait': 2
    }
    
    phase, duration = controller.get_next_phase(dummy_data)
    print(f"成功调用 get_next_phase: phase={phase}, duration={duration}")
    
    metrics = controller.get_performance_metrics()
    print(f"成功获取性能指标: {metrics}")
    
except ImportError as e:
    print(f"导入错误: {e}")
except Exception as e:
    print(f"运行时错误: {e}")
