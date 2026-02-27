#!/usr/bin/env python3
"""
自动化运行全部后端测试脚本，并打印结果。
"""
import os
import subprocess

test_scripts = [
    'test_auth.py',
    'test_integration.py',
    'test_signals.py',
    'test_password_fix.py',
    'test_drl_import.py',
]

backend_dir = os.path.dirname(os.path.abspath(__file__))

print("\n========== 后端自动化测试开始 ==========")
for script in test_scripts:
    script_path = os.path.join(backend_dir, script)
    print(f"\n--- 运行 {script} ---")
    try:
        result = subprocess.run(['python', script_path], capture_output=True, text=True, timeout=120)
        print(result.stdout)
        if result.stderr:
            print("[stderr]", result.stderr)
        if result.returncode == 0:
            print(f"✅ {script} 运行成功")
        else:
            print(f"❌ {script} 运行失败，返回码: {result.returncode}")
    except Exception as e:
        print(f"❌ {script} 执行异常: {e}")
print("\n========== 后端自动化测试结束 ==========")
