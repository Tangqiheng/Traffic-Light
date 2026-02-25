#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
使用正确 Python 环境启动项目的脚本
解决 VS Code 中 TensorFlow 导入问题
"""

import subprocess
import sys
import os

def main():
    """主函数"""
    # 设置正确的 Python 路径
    python_path = "D:\\Anaconda\\python.exe"
    
    if not os.path.exists(python_path):
        print(f"错误: 找不到 Python 路径 {python_path}")
        print("请检查 Anaconda 是否正确安装")
        return
    
    print(f"使用 Python 环境: {python_path}")
    
    # 获取要运行的脚本参数
    if len(sys.argv) < 2:
        print("用法: python start_with_correct_env.py <script_name.py> [args...]")
        print("示例: python start_with_correct_env.py backend/controllers/drl_traffic_controller.py")
        return
    
    script_to_run = sys.argv[1]
    script_args = sys.argv[2:] if len(sys.argv) > 2 else []
    
    # 构建完整的命令
    cmd = [python_path, script_to_run] + script_args
    
    print(f"执行命令: {' '.join(cmd)}")
    
    try:
        # 运行脚本
        result = subprocess.run(cmd, capture_output=False, text=True)
        print(f"脚本执行完成，返回码: {result.returncode}")
    except Exception as e:
        print(f"执行脚本时出错: {e}")

if __name__ == "__main__":
    main()