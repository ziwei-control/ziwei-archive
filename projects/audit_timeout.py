#!/usr/bin/env python3
# 外部 API 超时机制审计和修复
import os
import re
from datetime import datetime

# 需要检查的文件
FILES_TO_AUDIT = [
    "/home/admin/Ziwei/projects/x402-api/app_production.py",
    "/home/admin/Ziwei/projects/x402-api/app_full.py",
    "/home/admin/Ziwei/projects/global-warroom-upgraded/scripts/global-warroom.py",
    "/home/admin/Ziwei/projects/global-warroom-upgraded/scripts/global-warroom-upgraded.py",
    "/home/admin/Ziwei/projects/global-warroom/scripts/web3-wallet-assistant.py",
    "/home/admin/Ziwei/projects/global-warroom/scripts/stock-analysis.py",
]

print("=" * 70)
print("🔍 外部 API 超时机制审计")
print("=" * 70)
print(f"📅 审计时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"📊 检查文件: {len(FILES_TO_AUDIT)}")
print()

# API 调用模式
API_PATTERNS = [
    (r'urllib\.request\.urlopen\s*\([^,)]*\)', 'urlopen'),
    (r'requests\.(get|post|put|delete)\s*\([^)]+\)', 'requests'),
    (r'smtp\.SMTP\([^)]*\)', 'SMTP'),
    (r'urllib2\.urlopen\s*\([^,)]*\)', 'urllib2'),
]

findings = []

for filepath in FILES_TO_AUDIT:
    if not os.path.exists(filepath):
        continue
    
    filename = os.path.basename(filepath)
    print(f"\n📄 {filename}")
    print("-" * 70)
    
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        lines = content.split('\n')
    
    # 检查外部 API 调用
    api_calls = []
    
    for i, line in enumerate(lines, 1):
        for pattern, api_type in API_PATTERNS:
            if re.search(pattern, line):
                api_calls.append({
                    "line": i,
                    "code": line.strip(),
                    "type": api_type
                })
    
    if api_calls:
        print(f"   找到 {len(api_calls)} 个外部 API 调用:")
        
        has_timeout = 0
        for call in api_calls:
            print(f"   第 {call['line']} 行: {call['type']}")
            print(f"   代码: {call['code'][:70]}...")
            
            # 检查是否已有超时设置
            code = lines[call['line'] - 1]
            if 'timeout' in code.lower():
                print(f"   ✅ 已设置超时")
                has_timeout += 1
            else:
                print(f"   ⚠️  缺少超时设置")
                findings.append({
                    "file": filename,
                    "line": call['line'],
                    "type": call['type']
                })
        
        print()
        print(f"   超时覆盖率: {has_timeout}/{len(api_calls)}")
    else:
        print(f"   ✅ 未发现外部 API 调用")

if findings:
    print()
    print("=" * 70)
    print("📋 需要添加超时机制的调用")
    print("=" * 70)
    
    for i, finding in enumerate(findings, 1):
        print(f"{i}. {finding['file']}: 第 {finding['line']} 行 ({finding['type']})")
else:
    print()
    print("=" * 70)
    print("✅ 所有外部 API 调用已设置超时")
    print("=" * 70)

# 保存审计报告
report = {
    "timestamp": datetime.now().isoformat(),
    "total_files_checked": len(FILES_TO_AUDIT),
    "api_calls_needing_timeout": len(findings),
    "details": findings
}

with open("/home/admin/Ziwei/projects/TIMEOUT_AUDIT.json", 'w') as f:
    json.dump(report, f, indent=2)

print()
print(f"💾 审计报告已保存: /home/admin/Ziwei/projects/TIMEOUT_AUDIT.json")