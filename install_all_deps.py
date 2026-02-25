#!/usr/bin/env python3
"""
完整的依赖安装脚本
确保所有必要的Python包都被正确安装
"""

import subprocess
import sys
import os

def install_package(package):
    """安装单个包"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✓ 成功安装 {package}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ 安装 {package} 失败: {e}")
        return False

def main():
    print("开始安装 Traffic Light 项目所有依赖...")
    print("=" * 50)
    
    # 核心依赖列表
    core_packages = [
        "flask>=2.3.0",
        "flask-cors>=4.0.0", 
        "flask-sqlalchemy>=3.0.0",
        "pymysql>=1.0.0",
        "pyjwt>=2.8.0",
        "werkzeug>=2.3.0",
        "python-dotenv>=1.0.0",
        "requests>=2.31.0"
    ]
    
    # 可选的AI/ML依赖
    ml_packages = [
        "tensorflow>=2.13.0",
        "numpy>=1.21.0"
    ]
    
    print("安装核心依赖...")
    failed_core = []
    for package in core_packages:
        if not install_package(package):
            failed_core.append(package)
    
    print("\n安装AI/ML依赖（可选）...")
    failed_ml = []
    for package in ml_packages:
        if not install_package(package):
            failed_ml.append(package)
    
    print("=" * 50)
    
    if failed_core:
        print("以下核心依赖安装失败:")
        for pkg in failed_core:
            print(f"  - {pkg}")
        print("\n核心依赖缺失可能导致系统无法正常运行!")
    
    if failed_ml:
        print("以下AI/ML依赖安装失败:")
        for pkg in failed_ml:
            print(f"  - {pkg}")
        print("\nAI功能可能受限，但基础系统仍可运行。")
    
    if not failed_core and not failed_ml:
        print("所有依赖安装成功！")
        print("\n现在可以运行项目了:")
        print("cd backend && python app.py")
    elif not failed_core:
        print("核心依赖安装完成，AI功能可能受限。")
        print("\n可以尝试运行项目:")
        print("cd backend && python app.py")

if __name__ == "__main__":
    main()