#!/usr/bin/env python3
"""
简单后端测试脚本
直接测试后端API功能而不启动服务
"""

import requests
import json

def test_backend_apis():
    """测试后端API功能"""
    print("开始测试后端API...")
    print("=" * 40)
    
    # 测试1: 根路径
    print("1. 测试根路径...")
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            print("✅ 根路径访问成功")
            print(f"   响应: {response.json()}")
        else:
            print(f"❌ 根路径访问失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 根路径测试异常: {e}")
    
    # 测试2: 登录API
    print("\n2. 测试登录API...")
    try:
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        response = requests.post(
            "http://localhost:8000/api/auth/login",
            json=login_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 登录API测试成功!")
            print(f"   用户名: {result.get('user', {}).get('username')}")
            print(f"   访问令牌长度: {len(result.get('access_token', ''))} 字符")
        else:
            print(f"❌ 登录API测试失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            
    except Exception as e:
        print(f"❌ 登录API测试异常: {e}")
    
    # 测试3: 交通数据API
    print("\n3. 测试交通数据API...")
    try:
        response = requests.get(
            "http://localhost:8000/api/traffic/overview/intersection_001",
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 交通数据API测试成功!")
            if isinstance(result, dict):
                print(f"   数据字段: {list(result.keys())}")
                print(f"   数据示例: {str(result)[:100]}...")
            else:
                print(f"   数据: {result}")
        else:
            print(f"❌ 交通数据API测试失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            
    except Exception as e:
        print(f"❌ 交通数据API测试异常: {e}")

def check_service_status():
    """检查服务状态"""
    print("\n检查服务状态...")
    print("=" * 40)
    
    try:
        # 尝试连接到后端端口
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 8000))
        sock.close()
        
        if result == 0:
            print("✅ 后端端口 8000 可访问")
        else:
            print("❌ 后端端口 8000 不可访问")
            print("   请确保后端服务已启动")
            
    except Exception as e:
        print(f"❌ 端口检查异常: {e}")

if __name__ == "__main__":
    check_service_status()
    test_backend_apis()
    
    print("\n" + "=" * 40)
    print("测试完成!")