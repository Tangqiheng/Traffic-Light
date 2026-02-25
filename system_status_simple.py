#!/usr/bin/env python3
"""
智能交通灯系统状态检查脚本
"""
import requests
import json
import sys
from datetime import datetime

def check_service(url, service_name):
    """检查服务状态"""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"✅ {service_name} 正常运行")
            return True
        else:
            print(f"❌ {service_name} 返回状态码: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ {service_name} 无法访问: {e}")
        return False

def test_login():
    """测试登录功能"""
    try:
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        response = requests.post(
            "http://localhost:8001/api/auth/login",
            json=login_data,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            print("✅ 登录功能正常")
            print(f"   获取到访问令牌: {token[:20]}...")
            return token
        else:
            print(f"❌ 登录失败，状态码: {response.status_code}")
            print(f"   响应: {response.text}")
            return None
    except Exception as e:
        print(f"❌ 登录测试失败: {e}")
        return None

def test_protected_api(token):
    """测试受保护的API"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            "http://localhost:8001/api/system/status",
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 受保护API访问正常")
            print(f"   系统状态: {data.get('status')}")
            print(f"   时间戳: {data.get('timestamp')}")
            return True
        else:
            print(f"❌ 受保护API访问失败，状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 受保护API测试失败: {e}")
        return False

def main():
    print("="*60)
    print("🚦 智能交通灯系统状态检查")
    print("="*60)
    print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 检查各项服务
    services = [
        ("http://localhost:8001/", "后端API服务"),
        ("http://localhost:5174/", "前端Web服务")
    ]
    
    all_services_ok = True
    for url, name in services:
        if not check_service(url, name):
            all_services_ok = False
    
    print()
    
    if all_services_ok:
        print("🎉 基础服务检查通过!")
        print()
        
        # 测试登录功能
        token = test_login()
        if token:
            print()
            # 测试受保护API
            test_protected_api(token)
            
        print()
        print("="*60)
        print("💡 系统访问信息:")
        print("   前端界面: http://localhost:5174")
        print("   API文档: http://localhost:8001/docs")
        print("   默认账号: admin/admin123")
        print("="*60)
    else:
        print("❌ 部分服务未正常运行，请检查!")
        sys.exit(1)

if __name__ == "__main__":
    main()