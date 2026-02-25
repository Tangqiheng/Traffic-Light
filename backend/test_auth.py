#!/usr/bin/env python3
"""
认证系统测试脚本
测试登录、token验证和API访问功能
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_login():
    """测试登录功能"""
    print("🔐 测试登录功能...")
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"username": "admin", "password": "admin123"}
    )

    if response.status_code == 200:
        data = response.json()
        print("✅ 登录成功")
        print(f"   用户: {data['user']['username']}")
        print(f"   Token类型: {data['token_type']}")
        return data['access_token'], data['refresh_token']
    else:
        print(f"❌ 登录失败: {response.status_code}")
        print(f"   错误: {response.text}")
        return None, None

def test_get_current_user(access_token):
    """测试获取当前用户信息"""
    print("\n👤 测试获取用户信息...")
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)

    if response.status_code == 200:
        user = response.json()
        print("✅ 获取用户信息成功")
        print(f"   用户名: {user['username']}")
        print(f"   邮箱: {user['email']}")
        print(f"   全名: {user['full_name']}")
        print(f"   管理员: {user['is_admin']}")
        return True
    else:
        print(f"❌ 获取用户信息失败: {response.status_code}")
        print(f"   错误: {response.text}")
        return False

def test_traffic_api(access_token):
    """测试受保护的交通API"""
    print("\n🚦 测试交通API访问...")
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(f"{BASE_URL}/api/v1/traffic/status/1", headers=headers)

    if response.status_code == 200:
        data = response.json()
        print("✅ 交通API访问成功")
        print(f"   路口ID: {data.get('intersection_id', 'N/A')}")
        print(f"   车辆数: {data.get('vehicle_count', 'N/A')}")
        return True
    else:
        print(f"❌ 交通API访问失败: {response.status_code}")
        print(f"   错误: {response.text}")
        return False

def test_unauthorized_access():
    """测试未授权访问"""
    print("\n🚫 测试未授权访问...")
    response = requests.get(f"{BASE_URL}/api/v1/traffic/status/1")

    if response.status_code == 401:
        print("✅ 未授权访问正确被拒绝")
        return True
    else:
        print(f"❌ 未授权访问未被正确拒绝: {response.status_code}")
        return False

def main():
    print("🧪 开始认证系统测试\n")

    # 测试登录
    access_token, refresh_token = test_login()
    if not access_token:
        print("\n❌ 测试失败：无法登录")
        return

    # 测试获取用户信息
    if not test_get_current_user(access_token):
        print("\n❌ 测试失败：无法获取用户信息")
        return

    # 测试受保护API访问
    if not test_traffic_api(access_token):
        print("\n❌ 测试失败：无法访问受保护API")
        return

    # 测试未授权访问
    if not test_unauthorized_access():
        print("\n❌ 测试失败：未授权访问控制不正确")
        return

    print("\n🎉 所有测试通过！认证系统工作正常")
    print("\n📋 测试总结:")
    print("   ✅ 用户登录")
    print("   ✅ JWT Token验证")
    print("   ✅ 用户信息获取")
    print("   ✅ 受保护API访问")
    print("   ✅ 未授权访问控制")

if __name__ == "__main__":
    main()