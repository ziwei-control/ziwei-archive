#!/usr/bin/env python3
# =============================================================================
# 紫微智控系统 - 全面审计报告
# =============================================================================

import os
import re
import json
import subprocess
from datetime import datetime
from pathlib import Path

# 配置
Ziwei_DIR = Path("/home/admin/Ziwei")
REPORT_DIR = Ziwei_DIR / "audits"
REPORT_DIR.mkdir(exist_ok=True)

print("=" * 70)
print("🔍 紫微智控系统 - 全面审计")
print("=" * 70)
print(f"📅 审计时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"📂 审计目录：{Ziwei_DIR}")
print()

# 审计结果
audit_results = {
    "timestamp": datetime.now().isoformat(),
    "projects": {},
    "security": {"critical": 0, "high": 0, "medium": 0, "low": 0},
    "code_quality": {},
    "running_services": [],
    "recommendations": []
}

# =============================================================================
# 1. 项目结构审计
# =============================================================================
print("=" * 70)
print("📁 项目结构审计")
print("=" * 70)
print()

projects = {
    "x402-api": "/home/admin/Ziwei/projects/x402-api",
    "x402-python-sdk": "/home/admin/Ziwei/projects/x402-python-sdk",
    "x402-trading-bot": "/home/admin/Ziwei/projects/x402-trading-bot",
    "global-warroom": "/home/admin/Ziwei/projects/global-warroom",
    "global-warroom-upgraded": "/home/admin/Ziwei/projects/global-warroom-upgraded",
    "scripts": "/home/admin/Ziwei/scripts"
}

for name, path in projects.items():
    if os.path.exists(path):
        # 统计文件
        total_files = 0
        total_size = 0
        py_files = 0
        
        for root, dirs, files in os.walk(path):
            if '.git' in root or '__pycache__' in root:
                continue
            for file in files:
                total_files += 1
                filepath = os.path.join(root, file)
                total_size += os.path.getsize(filepath)
                if file.endswith('.py'):
                    py_files += 1
        
        audit_results["projects"][name] = {
            "path": path,
            "total_files": total_files,
            "python_files": py_files,
            "total_size_kb": round(total_size / 1024, 2)
        }
        
        print(f"✅ {name:25s} | 文件：{total_files:4d} | Python: {py_files:3d} | 大小：{total_size/1024:8.1f} KB")
    else:
        print(f"❌ {name:25s} | 不存在")

print()

# =============================================================================
# 2. 运行服务审计
# =============================================================================
print("=" * 70)
print("🏃 运行服务审计")
print("=" * 70)
print()

services_to_check = [
    ("x402 API", "app_production.py"),
    ("全球战情室", "warroom"),
    ("交易机器人", "bot_production")
]

for service_name, keyword in services_to_check:
    result = subprocess.run(['pgrep', '-f', keyword], capture_output=True, text=True)
    if result.stdout.strip():
        pids = result.stdout.strip().split('\n')
        audit_results["running_services"].append({
            "name": service_name,
            "pids": pids,
            "status": "running"
        })
        print(f"✅ {service_name:20s} | 运行中 (PID: {', '.join(pids)})")
    else:
        print(f"❌ {service_name:20s} | 未运行")

print()

# =============================================================================
# 3. 安全审计
# =============================================================================
print("=" * 70)
print("🔒 安全审计")
print("=" * 70)
print()

SECURITY_PATTERNS = {
    "hardcoded_password": (r'["\']UMayTeWFZsFqwv6M["\']', "🔴 严重"),
    "hardcoded_api_key": (r'api[_-]?key\s*[=:]\s*["\'][a-zA-Z0-9]{20,}["\']', "🟠 高"),
    "eval_exec": (r'\b(eval|exec)\s*\(', "🟡 中"),
    "command_injection": (r'os\.system\s*\(|subprocess\.call\s*\(', "🟡 中"),
    "sql_injection": (r'execute\s*\(\s*["\'].*%s', "🟠 高"),
}

security_issues = []

for project_name, project_path in projects.items():
    if not os.path.exists(project_path):
        continue
    
    for root, dirs, files in os.walk(project_path):
        if '.git' in root or '__pycache__' in root:
            continue
        
        for file in files:
            if not file.endswith('.py'):
                continue
            
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            except:
                continue
            
            for issue_type, (pattern, severity) in SECURITY_PATTERNS.items():
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    security_issues.append({
                        "file": filepath,
                        "type": issue_type,
                        "severity": severity,
                        "count": len(matches)
                    })
                    
                    if "严重" in severity:
                        audit_results["security"]["critical"] += 1
                    elif "高" in severity:
                        audit_results["security"]["high"] += 1
                    elif "中" in severity:
                        audit_results["security"]["medium"] += 1
                    else:
                        audit_results["security"]["low"] += 1

if security_issues:
    print(f"⚠️  发现 {len(security_issues)} 个安全问题:\n")
    for issue in security_issues[:10]:  # 显示前 10 个
        print(f"  {issue['severity']} {issue['type']:20s} | {os.path.basename(issue['file']):40s} ({issue['count']}处)")
    if len(security_issues) > 10:
        print(f"  ... 还有 {len(security_issues) - 10} 个问题")
else:
    print("✅ 未发现严重安全问题")

print()

# =============================================================================
# 4. 代码质量审计
# =============================================================================
print("=" * 70)
print("📊 代码质量审计")
print("=" * 70)
print()

total_lines = 0
total_functions = 0
total_classes = 0
total_docstrings = 0
python_files_total = 0

for project_name, project_path in projects.items():
    if not os.path.exists(project_path):
        continue
    
    project_lines = 0
    project_functions = 0
    project_classes = 0
    
    for root, dirs, files in os.walk(project_path):
        if '.git' in root or '__pycache__' in root:
            continue
        
        for file in files:
            if not file.endswith('.py'):
                continue
            
            filepath = os.path.join(root, file)
            python_files_total += 1
            
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    lines = content.split('\n')
                
                project_lines += len(lines)
                project_functions += len(re.findall(r'^\s*def\s+\w+', content, re.MULTILINE))
                project_classes += len(re.findall(r'^\s*class\s+\w+', content, re.MULTILINE))
                project_docstrings += len(re.findall(r'"""[\s\S]*?"""', content))
            except:
                continue
    
    total_lines += project_lines
    total_functions += project_functions
    total_classes += project_classes

audit_results["code_quality"] = {
    "total_python_files": python_files_total,
    "total_lines": total_lines,
    "total_functions": total_functions,
    "total_classes": total_classes,
    "avg_lines_per_file": round(total_lines / python_files_total, 1) if python_files_total > 0 else 0
}

print(f"Python 文件总数：{python_files_total}")
print(f"总代码行数：{total_lines:,}")
print(f"函数数量：{total_functions}")
print(f"类数量：{total_classes}")
print(f"平均每文件行数：{audit_results['code_quality']['avg_lines_per_file']}")
print()

# =============================================================================
# 5. 配置文件审计
# =============================================================================
print("=" * 70)
print("⚙️  配置文件审计")
print("=" * 70)
print()

config_files = []
for root, dirs, files in os.walk(Ziwei_DIR):
    if '.git' in root:
        continue
    for file in files:
        if file in ['.env', 'config.yaml', 'config.json', '.gitignore']:
            filepath = os.path.join(root, file)
            config_files.append(filepath)

for config_file in config_files[:10]:
    size = os.path.getsize(config_file)
    perms = oct(os.stat(config_file).st_mode)[-3:]
    print(f"📄 {config_file.replace(str(Ziwei_DIR), ''):50s} | {size:6d} bytes | 权限：{perms}")

print()

# =============================================================================
# 6. Git 仓库审计
# =============================================================================
print("=" * 70)
print("📦 Git 仓库审计")
print("=" * 70)
print()

git_repos = []
for root, dirs, files in os.walk(Ziwei_DIR):
    if '.git' in dirs:
        git_repos.append(root)
        dirs.remove('.git')

for repo in git_repos:
    repo_name = repo.replace(str(Ziwei_DIR), '')
    print(f"✅ {repo_name}")

print()

# =============================================================================
# 7. 磁盘使用审计
# =============================================================================
print("=" * 70)
print("💾 磁盘使用审计")
print("=" * 70)
print()

total_size = 0
for root, dirs, files in os.walk(Ziwei_DIR):
    if '.git' in root:
        continue
    for file in files:
        filepath = os.path.join(root, file)
        try:
            total_size += os.path.getsize(filepath)
        except:
            pass

print(f"紫微智控总大小：{total_size / 1024 / 1024:.2f} MB")
print()

# =============================================================================
# 8. 审计总结和建议
# =============================================================================
print("=" * 70)
print("📋 审计总结")
print("=" * 70)
print()

print("📊 系统概览:")
print(f"  项目数量：{len(audit_results['projects'])}")
print(f"  Python 文件：{python_files_total}")
print(f"  代码行数：{total_lines:,}")
print(f"  运行服务：{len(audit_results['running_services'])}")
print()

print("🔒 安全状态:")
print(f"  严重问题：{audit_results['security']['critical']}")
print(f"  高危问题：{audit_results['security']['high']}")
print(f"  中危问题：{audit_results['security']['medium']}")
print(f"  低危问题：{audit_results['security']['low']}")
print()

if audit_results['security']['critical'] > 0:
    print("⚠️  需要立即修复严重安全问题！")
    audit_results["recommendations"].append("立即修复硬编码密码")

if len(audit_results['running_services']) < 3:
    print("⚠️  部分服务未运行")
    audit_results["recommendations"].append("启动未运行的服务")

print()
print("=" * 70)
print("✅ 审计完成")
print("=" * 70)

# 保存审计报告
report_file = REPORT_DIR / f"audit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(report_file, 'w', encoding='utf-8') as f:
    json.dump(audit_results, f, ensure_ascii=False, indent=2)

print(f"\n💾 审计报告已保存：{report_file}")

# 生成 Markdown 报告
md_report = f"""# 紫微智控系统审计报告

**审计时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 系统概览

| 项目 | 数量 |
|------|------|
| 项目数 | {len(audit_results['projects'])} |
| Python 文件 | {python_files_total} |
| 代码行数 | {total_lines:,} |
| 运行服务 | {len(audit_results['running_services'])} |

## 安全状态

| 级别 | 数量 |
|------|------|
| 严重 | {audit_results['security']['critical']} |
| 高危 | {audit_results['security']['high']} |
| 中危 | {audit_results['security']['medium']} |
| 低危 | {audit_results['security']['low']} |

## 项目列表

"""

for name, stats in audit_results['projects'].items():
    md_report += f"- **{name}**: {stats['total_files']} 文件，{stats['python_files']} Python, {stats['total_size_kb']} KB\n"

md_report += f"\n## 运行服务\n\n"
for service in audit_results['running_services']:
    md_report += f"- ✅ {service['name']} (PID: {', '.join(service['pids'])})\n"

md_report_file = REPORT_DIR / f"audit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
with open(md_report_file, 'w', encoding='utf-8') as f:
    f.write(md_report)

print(f"📄 Markdown 报告：{md_report_file}")
