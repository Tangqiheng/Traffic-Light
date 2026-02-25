#!/usr/bin/env python3
"""
智能交通灯系统最终验证脚本
验证所有修复是否成功
"""

import requests
import json
import sys
from datetime import datetime

def final_verification():
    print("=" * 60)
    print("智能交通灯系统最终验证")
    print("=" * 60)
    print(f"验证时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 验证后端服务
    print("\n1. 后端服务验证:")
    try:
        response = requests.get("http://localhost:8001/", timeout=5)
        if response.status_code == 200:
            print("   ✅ 后端服务正常运行")
        else:
            print(f"   ❌ 后端服务异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ 后端服务连接失败: {str(e)}")
        return False
    
    # 2. 验证前端服务
    print("\n2. 前端服务验证:")
    try:
        response = requests.get("http://localhost:5175/", timeout=5)
        if response.status_code == 200:
            print("   ✅ 前端服务正常运行")
        else:
            print(f"   ❌ 前端服务异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ 前端服务连接失败: {str(e)}")
        return False
    
    # 3. 验证API功能
    print("\n3. API功能验证:")
    try:
        # 登录获取token
        login_response = requests.post(
            "http://localhost:8001/api/auth/login",
            json={"username": "admin", "password": "admin123"},
            timeout=5
        )
        
        if login_response.status_code == 200:
            token = login_response.json()['access_token']
            headers = {"Authorization": f"Bearer {token}"}
            print("   ✅ 用户登录成功")
            
            # 测试系统状态API
            status_response = requests.get(
                "http://localhost:8001/api/system/status",
                headers=headers,
                timeout=5
            )
            if status_response.status_code == 200:
                print("   ✅ 系统状态API正常")
            else:
                print(f"   ❌ 系统状态API异常: {status_response.status_code}")
                return False
            
            # 测试交通数据API
            traffic_response = requests.get(
                "http://localhost:8001/api/traffic/data",
                headers=headers,
                timeout=5
            )
            if traffic_response.status_code == 200:
                data = traffic_response.json()
                print(f"   ✅ 交通数据API正常 ({len(data['data'])}个路口)")
            else:
                print(f"   ❌ 交通数据API异常: {traffic_response.status_code}")
                return False
                
        else:
            print(f"   ❌ 登录失败: {login_response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ API测试失败: {str(e)}")
        return False
    
    # 4. 验证文件结构
    print("\n4. 文件结构验证:")
    import os
    
    # 检查关键文件是否存在
    required_files = [
        r"frontend\src\services\api.js",
        r"frontend\src\views\Dashboard.vue",
        r"backend\simple_server.py"
    ]
    
    all_files_exist = True
    for file_path in required_files:
        full_path = os.path.join(r"c:\Users\T2101235618\Desktop\Traffic Light", file_path)
        if os.path.exists(full_path):
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} 不存在")
            all_files_exist = False
    
    if not all_files_exist:
        return False
    
    print("\n" + "=" * 60)
    print("🎉 所有验证通过！系统修复完成！")
    print("\n访问信息:")
    print("- 前端界面: http://localhost:5175")
    print("- 后端API: http://localhost:8001")
    print("- 登录账号: admin / admin123")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = final_verification()
    sys.exit(0 if success else 1)