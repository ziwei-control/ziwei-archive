#!/usr/bin/env python3
"""
x402 API - 创建测试数据和管理员账户
"""

import hashlib
import sqlite3
import os
from datetime import datetime

DB_PATH = "/home/admin/Ziwei/projects/x402-api/api_keys.db"

def create_test_data():
    """创建测试用户数据"""
    print("=" * 60)
    print("创建测试用户数据")
    print("=" * 60)
    
    # 测试数据
    test_tx_hash = "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
    test_from_address = "0xUserTestAddress1234567890abcdef12"
    test_amount = 0.05
    test_timestamp = int(datetime.now().timestamp())
    
    # 生成 API Key
    salt = "x402_secret_salt_2026_production"
    hash_data = f"{test_tx_hash}{test_timestamp}{salt}"
    hash_hex = hashlib.sha256(hash_data.encode()).hexdigest()[:16]
    api_key = f"x402_{hash_hex}_{test_timestamp:x}"
    
    # 保存到数据库
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT OR REPLACE INTO api_keys
        (api_key, api_base_url, tx_hash, amount, from_address, timestamp, is_active)
        VALUES (?, ?, ?, ?, ?, ?, 1)
    """, (api_key, "8.213.149.224", test_tx_hash, test_amount, test_from_address, test_timestamp))
    
    conn.commit()
    conn.close()
    
    print("✅ 测试数据已创建")
    print(f"\n测试登录信息：")
    print(f"  发送地址：{test_from_address}")
    print(f"  交易 Hash: {test_tx_hash}")
    print(f"  API Key:   {api_key}")
    print(f"  金额：     {test_amount} USDC")
    print(f"\n使用以上信息登录 http://8.213.149.224:8091 测试")
    print("=" * 60)

def create_admin_account():
    """创建管理员账户（加密密码）"""
    print("\n" + "=" * 60)
    print("创建管理员账户")
    print("=" * 60)
    
    admin_address = "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
    admin_password = "0909opop!"
    
    # 加密密码（SHA256 + Salt）
    salt = "x402_admin_salt_2026_production"
    password_hash = hashlib.sha256(f"{admin_password}{salt}".encode()).hexdigest()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 创建管理员表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            address TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            is_active INTEGER DEFAULT 1
        )
    """)
    
    # 插入管理员
    cursor.execute("""
        INSERT OR REPLACE INTO admins
        (address, password_hash, salt)
        VALUES (?, ?, ?)
    """, (admin_address, password_hash, salt))
    
    conn.commit()
    conn.close()
    
    print("✅ 管理员账户已创建")
    print(f"\n管理员登录信息：")
    print(f"  地址：{admin_address}")
    print(f"  密码：0909opop!（已加密保存）")
    print(f"\n访问 http://8.213.149.224:8091/admin 登录")
    print("=" * 60)

if __name__ == "__main__":
    create_test_data()
    create_admin_account()
    print("\n✅ 所有数据创建完成！")
