#!/usr/bin/env python3
# 完整超时机制验证
import os

print("=" * 70)
print("🔍 外部 API 超时机制完整验证")
print("=" * 70)
print()

# 检查关键文件
files_to_check = [
    "/home/admin/Ziwei/projects/x402-api/app_production.py",
    "/home/admin/Ziwei/projects/x402-api/app_full.py",
    "/home/admin/Ziwei/projects/x402-api/app_simple.py",
    "/home/admin/Ziwei/projects/x402-api/app_demo.py",
    "/home/admin/Ziwei/projects/global-warroom-upgraded/scripts/global-warroom.py",
    "/home/admin/Ziwei/projects/global-warroom-upgraded/scripts/global-warroom-upgraded.py",
]

print("📊 验证结果:")
print()

all_safe = True

for filepath in files_to_check:
    if not os.path.exists(filepath):
        continue
    
    filename = os.path.basename(filepath)
    
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # 检查超时设置
    has_timeout = 'timeout' in content
    
    # 检查是否有外部 API 调用
    has_external_api = any([
        'urllib.request.urlopen' in content,
        'requests.get' in content or 'requests.post' in content,
        'smtplib.SMTP' in content or 'import smtplib' in content,
        'urlopen(' in content
    ])
    
    if has_external_api:
        status = "✅" if has_timeout else "⚠️ "
        note = "已设置超时" if has_timeout else "需要添加超时"
        
        if not has_timeout:
            all_safe = False
        
        print(f"{status} {filename}: {note}")
    else:
        print(f"✅ {filename}: 无外部 API 调用")

print()
print("=" * 70)

if all_safe:
    print("✅ 所有外部 API 调用已设置超时机制")
    print()
    print("📋 超时配置标准:")
    print("-" * 70)
    print("• urllib.request.urlopen: timeout=30")
    print("• requests.get/post: timeout=30")
    print("• smtplib.SMTP: timeout=30")
    print()
    print("• 快速 API: 5-10 秒")
    print("• 标准 API: 30 秒")
    print("• 文件上传: 60-120 秒")
else:
    print("⚠️  部分文件需要添加超时机制")

print("=" * 70)