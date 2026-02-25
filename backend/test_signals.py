#!/usr/bin/env python3
"""测试信号灯状态生成"""

import time
import sys
import os
sys.path.append(os.path.dirname(__file__))

from simple_server import get_signal_light_status_and_time, light_control_state

def test_signal_generation():
    """测试信号灯状态生成"""
    print("=== 信号灯状态测试 ===")
    print(f"初始相位: {light_control_state['current_phase']}")
    print(f"相位开始时间: {light_control_state['phase_start_time']}")
    print()
    
    # 测试多次状态生成
    for i in range(20):
        status, remaining_time, phase = get_signal_light_status_and_time()
        print(f"第{i+1:2d}秒: {status:>2s}灯 ({remaining_time:2d}s) - {phase}")
        time.sleep(1)
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_signal_generation()