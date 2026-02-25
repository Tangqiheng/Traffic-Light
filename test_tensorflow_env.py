#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TensorFlow 环境测试脚本
用于诊断 TensorFlow 导入和运行环境问题
"""

import sys
import os

def test_python_environment():
    """测试 Python 环境信息"""
    print("=== Python 环境信息 ===")
    print(f"Python 版本: {sys.version}")
    print(f"Python 可执行文件路径: {sys.executable}")
    print(f"当前工作目录: {os.getcwd()}")
    print()

def test_tensorflow_import():
    """测试 TensorFlow 导入"""
    print("=== TensorFlow 导入测试 ===")
    try:
        import tensorflow as tf
        print(f"✓ TensorFlow 版本: {tf.__version__}")
        
        # 测试基本操作
        hello = tf.constant('Hello, TensorFlow!')
        print(f"✓ TensorFlow 基本操作测试通过: {hello}")
        
        # 测试 Keras 导入
        try:
            from tensorflow import keras
            print("✓ 从 tensorflow 导入 keras 成功")
        except ImportError as e:
            print(f"✗ 从 tensorflow 导入 keras 失败: {e}")
            try:
                import keras
                print("✓ 直接导入 keras 成功")
            except ImportError as e2:
                print(f"✗ 直接导入 keras 也失败: {e2}")
                return False
                
        return True
    except ImportError as e:
        print(f"✗ TensorFlow 导入失败: {e}")
        return False

def test_drl_controller_import():
    """测试 DRL 控制器导入"""
    print("\n=== DRL 控制器导入测试 ===")
    try:
        # 添加项目路径到 Python 路径
        project_root = os.path.dirname(os.path.abspath(__file__))
        backend_path = os.path.join(project_root, 'backend')
        if backend_path not in sys.path:
            sys.path.insert(0, backend_path)
        
        from controllers.drl_traffic_controller import DRLTrafficController, check_tensorflow_availability
        print("✓ DRLTrafficController 导入成功")
        
        # 测试 TensorFlow 可用性检查
        is_available = check_tensorflow_availability()
        print(f"✓ TensorFlow 可用性检查: {is_available}")
        
        if is_available:
            # 尝试创建控制器实例
            try:
                controller = DRLTrafficController("test_intersection")
                print("✓ DRLTrafficController 实例创建成功")
            except Exception as e:
                print(f"✗ DRLTrafficController 实例创建失败: {e}")
        
        return True
    except Exception as e:
        print(f"✗ DRL 控制器导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("开始 TensorFlow 环境测试...\n")
    
    test_python_environment()
    
    tensorflow_ok = test_tensorflow_import()
    
    if tensorflow_ok:
        drl_ok = test_drl_controller_import()
        if drl_ok:
            print("\n🎉 所有测试通过！TensorFlow 环境配置正确。")
        else:
            print("\n⚠️  TensorFlow 可用但 DRL 控制器有问题。")
    else:
        print("\n❌ TensorFlow 不可用，请检查安装。")
        print("\n建议解决方案:")
        print("1. 运行: pip install tensorflow")
        print("2. 或运行项目根目录的安装脚本: python install_deps.py")
        print("3. 检查 VS Code 的 Python 解释器设置")

if __name__ == "__main__":
    main()