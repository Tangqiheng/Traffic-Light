#!/usr/bin/env python3
"""
依赖安装脚本
自动安装项目所需的所有Python依赖包
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
    except subprocess.CalledProcessError:
        print(f"✗ 安装 {package} 失败")
        return False

def main():
    print("开始安装 Traffic Light 项目依赖...")
    print("=" * 50)
    
    # 需要安装的包列表
    packages = [
        "tensorflow>=2.13.0",
        "numpy>=1.21.0", 
        "flask>=2.3.0",
        "flask-cors>=4.0.0",
        "python-dotenv>=1.0.0",
        "requests>=2.31.0"
    ]
    
    failed_packages = []
    
    for package in packages:
        print(f"正在安装 {package}...")
        if not install_package(package):
            failed_packages.append(package)
    
    print("=" * 50)
    if failed_packages:
        print(f"以下包安装失败:")
        for pkg in failed_packages:
            print(f"  - {pkg}")
        print("\n请手动运行以下命令:")
        print("pip install " + " ".join(failed_packages))
    else:
        print("所有依赖包安装成功！")
        print("\n现在可以运行项目了。")

if __name__ == "__main__":
    main()