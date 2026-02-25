#!/usr/bin/env python3
"""
智能交通灯系统状态检查脚本
用于验证前后端服务是否正常运行
"""

import requests
import json
import sys
from datetime import datetime

def check_service(url, service_name):
    """检查服务是否可达"""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"✅ {service_name} 服务正常运行")
            return True
        else:
            print(f"❌ {service_name} 服务返回状态码: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ {service_name} 服务无法连接")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ {service_name} 服务响应超时")
        return False
    except Exception as e:
        print(f"❌ {service_name} 服务出错: {str(e)}")
        return False

def test_api_endpoints():
    """测试API端点功能"""
    base_url = "http://localhost:8001"
    
    # 测试根端点
    print("\n=== 测试API端点 ===")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 根端点正常: {data['message']}")
        else:
            print(f"❌ 根端点异常: {response.status_code}")
    except Exception as e:
        print(f"❌ 根端点测试失败: {str(e)}")
    
    # 测试登录
    try:
        login_data = {"username": "admin", "password": "admin123"}
        response = requests.post(f"{base_url}/api/auth/login", json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            token = token_data['access_token']
            print(f"✅ 登录成功，获得token")
            
            # 测试需要认证的端点
            headers = {"Authorization": f"Bearer {token}"}
            
            # 测试系统状态
            response = requests.get(f"{base_url}/api/system/status", headers=headers)
            if response.status_code == 200:
                print("✅ 系统状态API正常")
            
            # 测试交通数据
            response = requests.get(f"{base_url}/api/traffic/data", headers=headers)
            if response.status_code == 200:
                traffic_data = response.json()
                print(f"✅ 交通数据API正常，获取到{len(traffic_data['data'])}个路口数据")
                
        else:
            print(f"❌ 登录失败: {response.status_code}")
    except Exception as e:
        print(f"❌ API测试失败: {str(e)}")

def main():
    print("=" * 50)
    print("智能交通灯系统状态检查")
    print("=" * 50)
    print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 检查后端服务
    backend_ok = check_service("http://localhost:8001", "后端(FastAPI)")
    
    # 检查前端服务 (更新为新端口)
    frontend_ok = check_service("http://localhost:5175", "前端(Vue/Vite)")
    
    # 如果服务都正常，测试API功能
    if backend_ok:
        test_api_endpoints()
    
    print("\n" + "=" * 50)
    if backend_ok and frontend_ok:
        print("🎉 所有服务运行正常！")
        print("前端访问地址: http://localhost:5175")
        print("后端API地址: http://localhost:8001")
        print("默认登录账号: admin / admin123")
    else:
        print("⚠️  部分服务存在问题，请检查上述错误信息")
    
    return backend_ok and frontend_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)