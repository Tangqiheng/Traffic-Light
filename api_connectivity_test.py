#!/usr/bin/env python3
"""
API连通性测试脚本
详细检查后端服务和API接口状态
"""

import requests
import socket
import time

def check_port_connectivity(host, port):
    """检查端口连通性"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception as e:
        print(f"端口检查异常: {e}")
        return False

def test_api_endpoints():
    """测试各个API端点"""
    base_url = "http://localhost:8000"
    
    # 测试端点列表
    endpoints = [
        {
            "name": "根路径",
            "url": "/",
            "method": "GET",
            "expected_status": 200
        },
        {
            "name": "登录接口",
            "url": "/api/auth/login",
            "method": "POST",
            "expected_status": 400,  # 空数据应该返回400
            "data": {}
        },
        {
            "name": "交通概况接口",
            "url": "/api/traffic/overview/intersection_001",
            "method": "GET",
            "expected_status": 200
        }
    ]
    
    print("=" * 50)
    print("API连通性测试")
    print("=" * 50)
    
    # 检查端口连通性
    print("1. 检查端口连通性...")
    if check_port_connectivity("localhost", 8000):
        print("✅ 端口 8000 可访问")
    else:
        print("❌ 端口 8000 不可访问")
        print("   请确保后端服务已启动")
        return False
    
    # 测试各个API端点
    all_passed = True
    for i, endpoint in enumerate(endpoints, 2):
        print(f"\n{i}. 测试 {endpoint['name']} ({endpoint['url']})...")
        
        try:
            if endpoint['method'] == 'GET':
                response = requests.get(
                    f"{base_url}{endpoint['url']}", 
                    timeout=5
                )
            else:  # POST
                response = requests.post(
                    f"{base_url}{endpoint['url']}",
                    json=endpoint.get('data', {}),
                    timeout=5
                )
            
            status_code = response.status_code
            expected = endpoint['expected_status']
            
            if status_code == expected:
                print(f"✅ 测试通过 (状态码: {status_code})")
                if response.content:
                    try:
                        data = response.json()
                        print(f"   响应数据: {str(data)[:100]}...")
                    except:
                        print(f"   响应内容: {response.text[:100]}...")
            else:
                print(f"❌ 测试失败")
                print(f"   期望状态码: {expected}")
                print(f"   实际状态码: {status_code}")
                if response.content:
                    try:
                        data = response.json()
                        print(f"   错误信息: {data}")
                    except:
                        print(f"   响应内容: {response.text}")
                all_passed = False
                
        except requests.exceptions.ConnectionError:
            print("❌ 连接失败 - 服务未启动或网络问题")
            all_passed = False
        except requests.exceptions.Timeout:
            print("❌ 请求超时")
            all_passed = False
        except Exception as e:
            print(f"❌ 请求异常: {e}")
            all_passed = False
    
    return all_passed

def check_backend_process():
    """检查后端进程状态"""
    print("\n" + "=" * 50)
    print("后端进程检查")
    print("=" * 50)
    
    try:
        # 尝试导入psutil来检查进程（如果安装了的话）
        import psutil
        
        python_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] == 'python.exe' and proc.info['cmdline']:
                    cmdline = ' '.join(proc.info['cmdline'])
                    if 'app.py' in cmdline or 'traffic' in cmdline.lower():
                        python_processes.append({
                            'pid': proc.info['pid'],
                            'cmdline': cmdline
                        })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        if python_processes:
            print("找到可能的后端进程:")
            for proc in python_processes:
                print(f"  PID: {proc['pid']}")
                print(f"  命令: {proc['cmdline']}")
        else:
            print("未找到运行中的后端进程")
            
    except ImportError:
        print("psutil未安装，跳过进程检查")
        print("请手动检查任务管理器中的Python进程")

def main():
    print("开始API连通性测试...")
    
    # 检查后端进程
    check_backend_process()
    
    # 测试API连通性
    success = test_api_endpoints()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 所有API测试通过!")
        print("系统状态正常，可以正常使用登录功能")
    else:
        print("❌ API测试失败!")
        print("请按照以下步骤排查:")
        print("1. 确认后端服务已启动 (python backend/app.py)")
        print("2. 检查端口8000是否被其他程序占用")
        print("3. 验证后端代码是否有语法错误")
        print("4. 查看后端控制台是否有错误信息")

if __name__ == "__main__":
    main()