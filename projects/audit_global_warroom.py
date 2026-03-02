#!/usr/bin/env python3
# =============================================================================
# 全球战情室项目审计报告
# =============================================================================

import os
import re
from datetime import datetime

print("=" * 70)
print("🔍 全球战情室项目全面审计")
print("=" * 70)
print(f"📅 审计时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# 项目路径
PROJECTS = [
    "/home/admin/Ziwei/projects/global-warroom",
    "/home/admin/Ziwei/projects/global-warroom-upgraded",
    "/home/admin/Ziwei/scripts"
]

# 审计结果
audit_results = {
    "files": [],
    "security_issues": [],
    "config_issues": [],
    "code_quality": [],
    "recommendations": []
}

# 安全检查模式
SECURITY_PATTERNS = {
    "hardcoded_password": r'["\']UMayTeWFZsFqwv6M["\']',
    "hardcoded_api_key": r'api[_-]?key\s*[=:]\s*["\'][a-zA-Z0-9]{20,}["\']',
    "hardcoded_secret": r'secret\s*[=:]\s*["\'][a-zA-Z0-9]{20,}["\']',
    "sql_injection": r'execute\s*\(\s*["\'].*%s',
    "command_injection": r'os\.system\s*\(|subprocess\.call\s*\(',
    "eval_exec": r'\b(eval|exec)\s*\(',
}

print("=" * 70)
print("📁 文件结构审计")
print("=" * 70)
print()

for project_path in PROJECTS:
    if not os.path.exists(project_path):
        continue

    print(f"📂 {project_path}")
    print("-" * 70)

    # 列出文件
    for root, dirs, files in os.walk(project_path):
        # 跳过.git 目录
        if '.git' in root:
            continue

        level = root.replace(project_path, '').count(os.sep)
        indent = ' ' * 2 * level
        print(f"{indent}{os.path.basename(root)}/")

        subindent = ' ' * 2 * (level + 1)
        for file in files:
            filepath = os.path.join(root, file)
            size = os.path.getsize(filepath)
            audit_results["files"].append({
                "path": filepath,
                "size": size,
                "modified": datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat()
            })
            print(f"{subindent}{file} ({size} bytes)")

    print()

# 安全审计
print("=" * 70)
print("🔒 安全审计")
print("=" * 70)
print()

for file_info in audit_results["files"]:
    filepath = file_info["path"]

    # 跳过二进制文件
    if filepath.endswith(('.pyc', '.pyo', '.so', '.bin')):
        continue

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except:
        continue

    # 检查安全问题
    for issue_type, pattern in SECURITY_PATTERNS.items():
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            audit_results["security_issues"].append({
                "file": filepath,
                "type": issue_type,
                "count": len(matches)
            })
            print(f"⚠️  {filepath}")
            print(f"   问题：{issue_type}")
            print(f"   数量：{len(matches)}")
            print()

if not audit_results["security_issues"]:
    print("✅ 未发现严重安全问题")
    print()

# 配置审计
print("=" * 70)
print("⚙️ 配置审计")
print("=" * 70)
print()

# 检查.env 文件
env_files = [f["path"] for f in audit_results["files"] if f["path"].endswith('.env')]

if env_files:
    for env_file in env_files:
        print(f"📄 {env_file}")
        with open(env_file, 'r') as f:
            lines = f.readlines()

        has_smtp = any('SMTP' in line for line in lines)
        has_email = any('EMAIL' in line for line in lines)
        has_api = any('API' in line for line in lines)

        print(f"   SMTP 配置：{'✅' if has_smtp else '❌'}")
        print(f"   邮箱配置：{'✅' if has_email else '❌'}")
        print(f"   API 配置：{'✅' if has_api else '❌'}")
        print()
else:
    print("⚠️  未找到.env 配置文件")
    print()

# 代码质量审计
print("=" * 70)
print("📊 代码质量审计")
print("=" * 70)
print()

python_files = [f["path"] for f in audit_results["files"] if f["path"].endswith('.py')]

total_lines = 0
total_functions = 0
total_classes = 0

for py_file in python_files:
    try:
        with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            lines = content.split('\n')

        total_lines += len(lines)
        total_functions += len(re.findall(r'^\s*def\s+\w+', content, re.MULTILINE))
        total_classes += len(re.findall(r'^\s*class\s+\w+', content, re.MULTILINE))

    except:
        continue

print(f"Python 文件数量：{len(python_files)}")
print(f"总代码行数：{total_lines}")
print(f"函数数量：{total_functions}")
print(f"类数量：{total_classes}")
print()

# 功能审计
print("=" * 70)
print("🎯 功能审计")
print("=" * 70)
print()

features = {
    "加密货币监控": False,
    "股票监控": False,
    "邮件通知": False,
    "定时任务": False,
    "数据去重": False,
    "风险控制": False
}

for py_file in python_files:
    try:
        with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read().lower()

        if 'crypto' in content or 'bitcoin' in content or 'eth' in content:
            features["加密货币监控"] = True
        if 'stock' in content or '股票' in content:
            features["股票监控"] = True
        if 'email' in content or 'smtp' in content:
            features["邮件通知"] = True
        if 'cron' in content or 'schedule' in content or 'interval' in content:
            features["定时任务"] = True
        if 'duplicate' in content or '去重' in content:
            features["数据去重"] = True
        if 'risk' in content or '止损' in content or 'stop_loss' in content:
            features["风险控制"] = True

    except:
        continue

for feature, implemented in features.items():
    status = "✅" if implemented else "❌"
    print(f"{status} {feature}")

print()

# 运行状态审计
print("=" * 70)
print("🏃 运行状态审计")
print("=" * 70)
print()

import subprocess
result = subprocess.run(['pgrep', '-f', 'warroom'], capture_output=True, text=True)

if result.stdout.strip():
    print(f"✅ 进程运行中 (PID: {result.stdout.strip()})")
else:
    print("❌ 未运行")

print()

# 总结和建议
print("=" * 70)
print("📋 审计总结")
print("=" * 70)
print()

issues_count = len(audit_results["security_issues"])
files_count = len(audit_results["files"])

print(f"审计文件数：{files_count}")
print(f"安全问题数：{issues_count}")
print(f"代码行数：{total_lines}")
print(f"功能完整度：{sum(features.values())}/{len(features)}")
print()

if issues_count > 0:
    print("⚠️  发现安全问题，需要修复")
else:
    print("✅ 未发现严重安全问题")

running_features = [k for k, v in features.items() if v]
if running_features:
    print(f"\n✅ 已实现功能:")
    for f in running_features:
        print(f"  - {f}")

missing_features = [k for k, v in features.items() if not v]
if missing_features:
    print(f"\n⚠️  缺失功能:")
    for f in missing_features:
        print(f"  - {f}")

print()
print("=" * 70)
print("✅ 审计完成")
print("=" * 70)

# 保存审计报告
report_file = "/home/admin/Ziwei/projects/global-warroom-audit-report.md"
with open(report_file, 'w', encoding='utf-8') as f:
    f.write("# 全球战情室项目审计报告\n\n")
    f.write(f"**审计时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    f.write(f"## 审计结果\n\n")
    f.write(f"- 审计文件数：{files_count}\n")
    f.write(f"- 安全问题数：{issues_count}\n")
    f.write(f"- 代码行数：{total_lines}\n")
    f.write(f"- 功能完整度：{sum(features.values())}/{len(features)}\n\n")

print(f"\n💾 审计报告已保存：{report_file}")
