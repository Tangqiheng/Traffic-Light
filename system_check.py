#!/usr/bin/env python3
"""
完整的系统状态检查脚本
验证前后端服务和API连接
"""

import requests
import json
import time

def check_backend_health():
    """检查后端健康状态"""
    print("🔍 检查后端服务...")
    try:
        response = requests.get('http://localhost:8000/', timeout=5)
        if response.status_code == 200:
            print("✅ 后端服务运行正常")
            data = response.json()
            print(f"   版本: {data.get('version', '未知')}")
            print(f"   状态: {data.get('status', '未知')}")
            return True
        else:
            print(f"❌ 后端服务异常 (状态码: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ 无法连接到后端服务: {e}")
        return False

def test_login_api():
    """测试登录API"""
    print("\n🔐 测试登录API...")
    url = "http://localhost:8000/api/auth/login"
    data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print("✅ 登录API测试成功")
            print(f"   访问令牌: {result.get('access_token', 'N/A')[:20]}...")
            print(f"   用户名: {result.get('user', {}).get('username', 'N/A')}")
            return True
        else:
            print(f"❌ 登录API测试失败 (状态码: {response.status_code})")
            print(f"   错误信息: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 登录API请求失败: {e}")
        return False

def test_traffic_api():
    """测试交通数据API"""
    print("\n🚦 测试交通数据API...")
    url = "http://localhost:8000/api/traffic/overview/intersection_001"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print("✅ 交通API测试成功")
            print(f"   数据字段: {list(result.keys()) if isinstance(result, dict) else 'N/A'}")
            return True
        else:
            print(f"❌ 交通API测试失败 (状态码: {response.status_code})")
            print(f"   错误信息: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 交通API请求失败: {e}")
        return False

def check_frontend_access():
    """检查前端访问"""
    print("\n🌐 检查前端服务...")
    try:
        # 尝试访问前端的常见端口
        ports_to_check = [5173, 5174, 5175]
        for port in ports_to_check:
            try:
                response = requests.get(f'http://localhost:{port}', timeout=3)
                if response.status_code < 500:  # 接受2xx和4xx状态码
                    print(f"✅ 前端服务在端口 {port} 运行")
                    return True
            except:
                continue
        
        print("⚠️  前端服务未检测到运行")
        print("   请确保已运行: cd frontend && npm run dev")
        return False
    except Exception as e:
        print(f"❌ 前端服务检查失败: {e}")
        return False

def main():
    print("=" * 50)
    print("智能交通灯控制系统 - 状态检查")
    print("=" * 50)
    
    # 检查各组件
    backend_ok = check_backend_health()
    login_ok = test_login_api() if backend_ok else False
    traffic_ok = test_traffic_api() if backend_ok else False
    frontend_ok = check_frontend_access()
    
    print("\n" + "=" * 50)
    print("📊 检查结果汇总:")
    print(f"   后端服务: {'✅ 正常' if backend_ok else '❌ 异常'}")
    print(f"   登录API:  {'✅ 正常' if login_ok else '❌ 异常'}")
    print(f"   交通API:  {'✅ 正常' if traffic_ok else '❌ 异常'}")
    print(f"   前端服务: {'✅ 正常' if frontend_ok else '❌ 异常'}")
    
    if all([backend_ok, login_ok, traffic_ok]):
        print("\n🎉 系统核心功能正常!")
        print("💡 提示: 如需完整功能，请启动前端服务")
    else:
        print("\n⚠️  系统存在问题，请检查上述错误信息")
        print("\n🔧 常见解决方案:")
        if not backend_ok:
            print("   - 重启后端: cd backend && python app.py")
        if not frontend_ok:
            print("   - 启动前端: cd frontend && npm run dev")
        print("   - 检查端口占用情况")

if __name__ == "__main__":
    main()