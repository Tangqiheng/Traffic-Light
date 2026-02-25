#!/usr/bin/env python3
"""
依赖检查脚本
验证项目所需的Python包是否已正确安装
"""

import sys

def check_import(module_name, package_name=None):
    """检查模块是否可以导入"""
    if package_name is None:
        package_name = module_name
    
    try:
        __import__(module_name)
        print(f"✓ {package_name} - 已安装")
        return True
    except ImportError:
        print(f"✗ {package_name} - 未安装")
        return False

def main():
    print("检查 Traffic Light 项目依赖...")
    print("=" * 40)
    
    # 必需的核心依赖
    core_deps = [
        ("flask", "Flask"),
        ("flask_cors", "Flask-CORS"),
        ("flask_sqlalchemy", "Flask-SQLAlchemy"),
        ("jwt", "PyJWT"),
        ("pymysql", "PyMySQL"),
        ("requests", "Requests"),
        ("dotenv", "python-dotenv")
    ]
    
    # 可选的AI依赖
    ai_deps = [
        ("tensorflow", "TensorFlow"),
        ("numpy", "NumPy")
    ]
    
    print("检查核心依赖:")
    core_missing = []
    for module, name in core_deps:
        if not check_import(module, name):
            core_missing.append(name)
    
    print("\n检查AI依赖:")
    ai_missing = []
    for module, name in ai_deps:
        if not check_import(module, name):
            ai_missing.append(name)
    
    print("\n" + "=" * 40)
    
    if core_missing:
        print("缺失的核心依赖:")
        for dep in core_missing:
            print(f"  - {dep}")
        print("\n请运行以下命令安装:")
        print("pip install flask flask-cors flask-sqlalchemy pyjwt pymysql requests python-dotenv")
    else:
        print("✓ 所有核心依赖已安装")
    
    if ai_missing:
        print("\n缺失的AI依赖:")
        for dep in ai_missing:
            print(f"  - {dep}")
        print("\nAI功能可能受限，但系统基础功能可正常运行")
    else:
        print("✓ 所有AI依赖已安装")
    
    if not core_missing:
        print("\n🎉 环境检查通过，可以启动项目!")

if __name__ == "__main__":
    main()