#!/usr/bin/env python3
# 验证安全修复
import os
import json
from dotenv import load_dotenv

print("=" * 70)
print("🔍 global-warroom-upgraded 安全修复验证")
print("=" * 70)
print()

# 检查 .env 文件
env_file = "/home/admin/Ziwei/projects/global-warroom-upgraded/.env"
gitignore_file = "/home/admin/Ziwei/projects/global-warroom-upgraded/.gitignore"

print("📄 .env 文件检查:")
if os.path.exists(env_file):
    stat = os.stat(env_file)
    print(f"   ✅ 文件存在")
    print(f"   📊 大小: {stat.st_size} bytes")
    print(f"   🔒 权限: {oct(stat.st_mode)[-3:]}")
    
    if oct(stat.st_mode)[-3:] == "600":
        print(f"   ✅ 权限正确 (600 - 仅所有者可读写)")
    else:
        print(f"   ⚠️  权限不安全，建议: chmod 600 {env_file}")
else:
    print(f"   ❌ 文件不存在")
print()

print("📄 .gitignore 检查:")
if os.path.exists(gitignore_file):
    with open(gitignore_file, 'r') as f:
        content = f.read()
    if ".env" in content:
        print(f"   ✅ .env 已添加到 .gitignore")
    else:
        print(f"   ⚠️  .env 未添加到 .gitignore")
else:
    print(f"   ❌ .gitignore 不存在")
print()

print("🔍 环境变量加载测试:")
try:
    load_dotenv(env_file)
    
    required_vars = {
        "SMTP_SERVER": os.getenv("SMTP_SERVER"),
        "SMTP_PORT": os.getenv("SMTP_PORT"),
        "SENDER_EMAIL": os.getenv("SENDER_EMAIL"),
        "SENDER_PASSWORD": os.getenv("SENDER_PASSWORD"),
        "RECEIVER_EMAIL": os.getenv("RECEIVER_EMAIL")
    }
    
    all_loaded = True
    for var, value in required_vars.items():
        if value:
            if var == "SENDER_PASSWORD":
                print(f"   ✅ {var}: ***")
            else:
                print(f"   ✅ {var}: {value}")
        else:
            print(f"   ❌ {var}: 未加载")
            all_loaded = False
    
    if all_loaded:
        print()
        print("✅ 所有环境变量加载成功")
    else:
        print()
        print("⚠️  部分环境变量未加载")
        
except Exception as e:
    print(f"   ❌ 加载失败: {e}")
print()

print("🔍 代码中硬编码检查:")
files_to_check = [
    "/home/admin/Ziwei/projects/global-warroom-upgraded/scripts/global-warroom-upgraded.py",
    "/home/admin/Ziwei/projects/global-warroom-upgraded/scripts/global-warroom.py"
]

password_found = False
for filepath in files_to_check:
    if not os.path.exists(filepath):
        continue
    
    filename = os.path.basename(filepath)
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    if "UMayTeWFZsFqwv6M" in content or 'sender_password": "UMayTeWFZsFqwv6M"' in content:
        print(f"   ❌ {filename}: 仍包含硬编码密码")
        password_found = True
    else:
        print(f"   ✅ {filename}: 未发现硬编码密码")

if password_found:
    print()
    print("⚠️  警告: 代码中仍存在硬编码密码，需要手动修复")
else:
    print()
    print("✅ 代码中未发现硬编码密码")

print()
print("=" * 70)
print("✅ 验证完成")
print("=" * 70)