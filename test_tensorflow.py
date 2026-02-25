#!/usr/bin/env python3
"""
测试 TensorFlow 导入修复
"""

print("Testing TensorFlow import...")

try:
    from backend.controllers.drl_traffic_controller import (
        DRLTrafficController, 
        check_tensorflow_availability,
        install_tensorflow_instructions
    )
    
    print("✓ Module imported successfully")
    
    # 测试依赖检查
    if check_tensorflow_availability():
        print("✓ TensorFlow is available and functional")
        # 尝试创建控制器实例
        try:
            controller = DRLTrafficController("test_intersection")
            print("✓ DRLTrafficController created successfully")
        except Exception as e:
            print(f"✗ Failed to create controller: {e}")
    else:
        print("✗ TensorFlow is not available")
        print(install_tensorflow_instructions())
        
except ImportError as e:
    print(f"✗ Import failed: {e}")
except Exception as e:
    print(f"✗ Unexpected error: {e}")

print("Test completed.")