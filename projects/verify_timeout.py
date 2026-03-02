#!/usr/bin/env python3
# 外部 API 超时机制最终验证
import os
import re

print("=" * 70)
print("🔍 外部 API 超时机制最终验证")
print("=" * 70)
print()

# 搜索超时设置
timeout_patterns = [
    r'timeout\s*=\s*\d+',
    r'urlopen\s*\([^,)]*,\s*timeout\s*=\s*\d+',
]

# 需要检查的文件
critical_files = [
    "/home/admin/Ziwei/projects/x402-api/app_production.py",
    "/home/admin/Ziwei/projects/x402-api/app_full.py",
    "/home/admin/Ziwei/projects/global-warroom-upgraded/scripts/global-warroom.py",
    "/home/admin/Ziwei/projects/global-warroom-upgraded/scripts/global-warroom-upgraded.py",
]

total_checks = 0
with_timeout = 0

for filepath in critical_files:
    if not os.path.exists(filepath):
        continue
    
    filename = os.path.basename(filepath)
    print(f"📄 {filename}")
    print("-" * 70)
    
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # 查找所有 urllib.urlopen 调用
    urlopen_pattern = r'urllib\.request\.urlopen\s*\([^)]+\)'
    matches = re.findall(urlopen_pattern, content)
    
    if matches:
        print(f"   找到 {len(matches)} 个 urllib.urlopen 调用:")
        
        for match in matches:
            if 'timeout=' in match:
                print(f"   ✅ {match[:80]}...")
                with_timeout += 1
            else:
                print(f"   ⚠️  {match[:80]}...")
            total_checks += 1
    
    # 查找 requests 调用
    requests_pattern = r'requests\.(get|post|put|delete)\s*\([^)]+\)'
    matches = re.findall(requests_pattern, content)
    
    if matches:
        print(f"   找到 {len(matches)} 个 requests 调用:")
        
        for match in matches:
            if 'timeout=' in match:
                print(f"   ✅ {match[:80]}...")
                with_timeout += 1
            else:
                print(f"   ⚠️  {match[:80]}...")
            total_checks += 1
    
    # 查找 SMTP 调用
    smtp_pattern = r'smtp\.SMTP\([^)]*\)'
    matches = re.findall(smtp_pattern, content)
    
    if matches:
        print(f"   找到 {len(matches)} 个 SMTP 调用:")
        
        for match in matches:
            if 'timeout' in content[content.find(match):content.find(match)+200]:
                print(f"   ✅ {match[:80]}...")
                with_timeout += 1
            else:
                print(f"   ⚠️  {match[:80]}...")
            total_checks += 1
    
    if total_checks == 0:
        print(f"   ✅ 未发现外部 API 调用")
    else:
        print(f"   超时设置: {with_timeout}/{total_checks}")
    
    print()

print("=" * 70)
print("📊 超时机制覆盖率")
print("=" * 70)
print(f"总检查: {total_checks} 个外部 API 调用")
print(f"已设置超时: {with_timeout} 个")
print(f"覆盖率: {(with_timeout/total_checks*100) if total_checks > 0 else 100:.1f}%")
print()

if total_checks > 0:
    if with_timeout == total_checks:
        print("✅ 所有外部 API 调用已设置超时机制")
    else:
        print(f"⚠️  {total_checks - with_timeout} 个调用需要添加超时机制")
else:
    print("✅ 未发现需要添加超时的外部 API 调用")

print()
print("=" * 70)
print("🎯 推荐配置")
print("=" * 70)
print("""
超时设置建议：

1. urllib.urlopen:
   urllib.request.urlopen(req, timeout=30)

2. requests:
   requests.get(url, timeout=30)
   requests.post(url, json=data, timeout=30)

3. SMTP:
   smtp.SMTP(..., timeout=30)

推荐超时时间：
- 快速 API: 5-10 秒
- 标准 API: 30 秒
- 文件上传: 60-120 秒
""")
print("=" * 70)