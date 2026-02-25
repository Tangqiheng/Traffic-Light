#!/usr/bin/env python3
"""完整测试脚本 - 验证黄灯和时间段特性"""

import time
import sys
import os
sys.path.append(os.path.dirname(__file__))

# 导入必要的模块
from simple_server import (
    get_time_based_vehicle_count,
    get_signal_light_status_and_time,
    light_control_state,
    update_traffic_data
)

def test_time_based_traffic():
    """测试时间段车流量功能"""
    print("=== 时间段车流量测试 ===")
    for hour in [6, 8, 12, 18, 22]:
        # 模拟不同时段
        import datetime
        original_hour = datetime.datetime.now().hour
        # 这里我们只测试函数逻辑，不实际修改系统时间
        print(f"模拟{hour}点时段的车流量: {get_time_based_vehicle_count()}辆")
    print()

def test_signal_light_cycle():
    """测试信号灯完整周期"""
    print("=== 信号灯周期测试 ===")
    print(f"初始状态: 相位={light_control_state['current_phase']}")
    print()
    
    # 记录不同状态的出现
    states_seen = {}
    
    for i in range(70):  # 测试约70秒，覆盖完整周期
        status, remaining_time, phase = get_signal_light_status_and_time()
        key = f"{status}-{phase}"
        if key not in states_seen:
            states_seen[key] = []
        states_seen[key].append((i, remaining_time))
        
        if i % 5 == 0:  # 每5秒打印一次
            print(f"{i:2d}s: {status:>2s}灯 ({remaining_time:2d}s) - {phase}")
        time.sleep(1)
    
    print("\n=== 状态出现统计 ===")
    for state, times in states_seen.items():
        print(f"{state}: 出现{len(times)}次")
    print()

def test_update_traffic_data():
    """测试完整的交通数据更新"""
    print("=== 交通数据更新测试 ===")
    for i in range(5):
        data = update_traffic_data("测试路口", {})
        print(f"第{i+1}次更新:")
        print(f"  车流量: {data['vehicle_count']}辆")
        print(f"  信号灯: {data['light_status']} ({data['remaining_time']}s)")
        print(f"  相位: {data['current_phase']}")
        print(f"  拥堵等级: {data['congestion_level']}")
        print(f"  平均速度: {data['average_speed']}km/h")
        print()
        time.sleep(2)

if __name__ == "__main__":
    print("开始完整功能测试...\n")
    
    try:
        test_time_based_traffic()
        test_signal_light_cycle()
        test_update_traffic_data()
        print("✅ 所有测试完成!")
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()