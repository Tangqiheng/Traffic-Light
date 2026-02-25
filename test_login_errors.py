#!/usr/bin/env python3
"""
登录功能错误测试脚本
验证各种登录错误场景的处理
"""

import requests
import json

def test_login_scenarios():
    """测试各种登录场景"""
    base_url = "http://localhost:8000"
    
    test_cases = [
        {
            "name": "正常登录",
            "data": {"username": "admin", "password": "admin123"},
            "expected_status": 200,
            "description": "使用正确的凭据登录"
        },
        {
            "name": "用户名为空",
            "data": {"username": "", "password": "admin123"},
            "expected_status": 400,
            "description": "测试用户名为空的情况"
        },
        {
            "name": "密码为空",
            "data": {"username": "admin", "password": ""},
            "expected_status": 400,
            "description": "测试密码为空的情况"
        },
        {
            "name": "用户名不存在",
            "data": {"username": "nonexistent", "password": "password"},
            "expected_status": 401,
            "description": "测试不存在的用户名"
        },
        {
            "name": "密码错误",
            "data": {"username": "admin", "password": "wrongpassword"},
            "expected_status": 401,
            "description": "测试错误的密码"
        },
        {
            "name": "请求数据格式错误",
            "data": "invalid json format",
            "expected_status": 400,
            "description": "测试无效的JSON数据"
        }
    ]
    
    print("=" * 60)
    print("登录功能错误测试")
    print("=" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. 测试场景: {test_case['name']}")
        print(f"   描述: {test_case['description']}")
        print(f"   请求数据: {test_case['data']}")
        
        try:
            if isinstance(test_case['data'], str):
                # 发送无效JSON数据
                response = requests.post(
                    f"{base_url}/api/auth/login",
                    data=test_case['data'],
                    headers={'Content-Type': 'application/json'},
                    timeout=10
                )
            else:
                response = requests.post(
                    f"{base_url}/api/auth/login",
                    json=test_case['data'],
                    timeout=10
                )
            
            status_code = response.status_code
            response_data = response.json() if response.content else {}
            
            print(f"   实际状态码: {status_code}")
            print(f"   预期状态码: {test_case['expected_status']}")
            print(f"   响应数据: {json.dumps(response_data, ensure_ascii=False, indent=2)}")
            
            # 验证结果
            if status_code == test_case['expected_status']:
                print("   ✅ 测试通过")
                
                # 验证错误信息
                if 'error' in response_data:
                    print(f"   错误信息: {response_data['error']}")
                if 'code' in response_data:
                    print(f"   错误代码: {response_data['code']}")
                if 'details' in response_data:
                    print(f"   详细说明: {response_data['details']}")
            else:
                print("   ❌ 测试失败")
                print(f"   期望: {test_case['expected_status']}, 实际: {status_code}")
                
        except Exception as e:
            print(f"   ❌ 请求异常: {e}")
    
    print("\n" + "=" * 60)
    print("测试完成!")

def test_security_features():
    """测试安全相关功能"""
    print("\n" + "=" * 60)
    print("安全功能测试")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # 测试默认密码警告
    print("\n1. 测试默认密码安全警告...")
    try:
        response = requests.post(
            f"{base_url}/api/auth/login",
            json={"username": "admin", "password": "admin123"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 'DEFAULT_PASSWORD_WARNING':
                print("✅ 默认密码警告功能正常")
                print(f"   警告信息: {data.get('error')}")
                print(f"   详细说明: {data.get('details')}")
            elif data.get('access_token'):
                print("✅ 登录成功（无警告）")
            else:
                print("❌ 响应格式异常")
        else:
            print(f"❌ 登录失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")

if __name__ == "__main__":
    # 先检查服务是否运行
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            print("✅ 后端服务运行正常")
            test_login_scenarios()
            test_security_features()
        else:
            print("❌ 后端服务异常")
    except Exception as e:
        print(f"❌ 无法连接到后端服务: {e}")
        print("请确保后端服务已在 http://localhost:8000 运行")