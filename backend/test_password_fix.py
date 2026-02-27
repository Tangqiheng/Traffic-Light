#!/usr/bin/env python3
"""测试密码长度修复"""

import sys
import os
import hashlib
from passlib.context import CryptContext

# 创建密码上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def test_password_length():
    """测试密码长度处理"""
    print("=== 密码长度修复测试 ===")
    
    # 测试正常长度密码
    normal_password = "admin123"
    print(f"正常密码 '{normal_password}' 长度: {len(normal_password.encode('utf-8'))} 字节")
    
    # 测试超长密码
    long_password = "a" * 100  # 100个字符
    print(f"超长密码 '{long_password[:20]}...' 长度: {len(long_password.encode('utf-8'))} 字节")
    
    # 测试截断逻辑
    if len(long_password.encode('utf-8')) > 72:
        truncated = long_password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
        print(f"截断后密码: '{truncated}' 长度: {len(truncated.encode('utf-8'))} 字节")
    
    # 测试哈希
    try:
        # 截断正常密码
        normal_bytes = normal_password.encode('utf-8')
        if len(normal_bytes) > 72:
            normal_bytes = normal_bytes[:72]
        safe_normal = normal_bytes.decode('utf-8', errors='ignore')
        hashed = pwd_context.hash(safe_normal)
        print(f"正常密码哈希成功")
    except Exception as e:
        print(f"正常密码哈希失败: {e}")
        import sys
        sys.exit(1)

    # 测试超长密码哈希（应截断）
    try:
        password_to_hash = long_password
        long_bytes = password_to_hash.encode('utf-8')
        if len(long_bytes) > 72:
            long_bytes = long_bytes[:72]
        safe_long = long_bytes.decode('utf-8', errors='ignore')
        hashed_long = pwd_context.hash(safe_long)
        print(f"超长密码截断后哈希成功")
    except Exception as e:
        print(f"超长密码哈希失败: {e}")
        import sys
        sys.exit(1)

    # 测试验证
    try:
        # 验证正常密码
        hashed = pwd_context.hash(safe_normal)
        verified = pwd_context.verify(safe_normal, hashed)
        print(f"密码验证成功: {verified}")
    except Exception as e:
        print(f"密码验证失败: {e}")
        import sys
        sys.exit(1)
    
    print("=== 测试完成 ===")

if __name__ == "__main__":
    test_password_length()