import requests
import json

def test_login_api():
    """测试登录API"""
    url = "http://localhost:8000/api/auth/login"
    data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            print("✅ 登录API测试成功")
            result = response.json()
            print(f"访问令牌: {result.get('access_token', 'N/A')[:20]}...")
        else:
            print("❌ 登录API测试失败")
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")

def test_traffic_api():
    """测试交通数据API"""
    url = "http://localhost:8000/api/traffic/overview/intersection_001"
    
    try:
        response = requests.get(url)
        print(f"\n交通API状态码: {response.status_code}")
        print(f"交通API响应: {response.text[:200]}...")
        
    except Exception as e:
        print(f"❌ 交通API请求失败: {e}")

if __name__ == "__main__":
    print("开始测试后端API...")
    test_login_api()
    test_traffic_api()