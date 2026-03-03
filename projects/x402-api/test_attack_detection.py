#!/usr/bin/env python3
# 直接测试攻击检测

import sys
sys.path.insert(0, '/home/admin/Ziwei/projects/x402-api')

from security import security_manager

test_cases = [
    ("SQL 注入", "SELECT * FROM users; DROP TABLE users;--"),
    ("XSS", "<script>alert(1)</script>"),
    ("路径遍历", "../../../etc/passwd"),
    ("命令注入", "system(rm -rf /)"),
]

print("=" * 70)
print("🧪 直接测试攻击检测")
print("=" * 70)
print()

for test_name, test_data in test_cases:
    print(f"测试：{test_name}")
    print(f"数据：{test_data}")
    
    is_attack, attack_types = security_manager.detect_attack("127.0.0.1", test_data)
    
    if is_attack:
        print(f"✅ 检测到攻击：{attack_types}")
    else:
        print(f"❌ 未检测到攻击")
    print()

print("=" * 70)
print("查看攻击日志:")
print("=" * 70)
for log in security_manager.get_attack_log(10):
    print(f"  {log['timestamp'][:19]} | {log['ip']:15s} | {log['attack_type']}")
