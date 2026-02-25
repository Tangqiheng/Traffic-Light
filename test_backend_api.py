#!/usr/bin/env python3
"""
后端API测试脚本
验证Flask后端服务是否正常运行
"""

import requests
import json

def test_backend_health():
    """测试后端健康检查"""
    try:
        response = requests.get('http://localhost:8000/')
        print(f"健康检查状态: {response.status_code}")
        if response.status_code == 200:
            print("✅ 后端服务运行正常")
            print(f"响应内容: {response.text}")
        else:
            print("❌ 后端服务异常")
    except Exception as e:
        print(f"❌ 无法连接到后端服务: {e}")

def test_login_api():
    """测试登录API"""
    url = "http://localhost:8000/api/auth/login"
    data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"\n登录API状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 登录API测试成功")
            print(f"访问令牌: {result.get('access_token', 'N/A')[:30]}...")
            print(f"用户信息: {result.get('user', {})}")
        else:
            print("❌ 登录API测试失败")
            print(f"错误信息: {response.text}")
            
    except Exception as e:
        print(f"❌ 登录API请求失败: {e}")

def test_traffic_api():
    """测试交通数据API"""
    url = "http://localhost:8000/api/traffic/overview/intersection_001"
    
    try:
        response = requests.get(url)
        print(f"\n交通API状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 交通API测试成功")
            print(f"数据示例: {str(result)[:100]}...")
        else:
            print("❌ 交通API测试失败")
            print(f"错误信息: {response.text}")
            
    except Exception as e:
        print(f"❌ 交通API请求失败: {e}")

def main():
    print("开始测试后端API服务...")
    print("=" * 50)
    
    test_backend_health()
    test_login_api()
    test_traffic_api()
    
    print("\n" + "=" * 50)
    print("测试完成!")

if __name__ == "__main__":
    main()