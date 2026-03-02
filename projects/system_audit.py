#!/usr/bin/env python3
# 系统项目全面审计
import os
import json
import base64
import urllib.request
from datetime import datetime

# 项目列表
PROJECTS = [
    {
        "name": "x402-api",
        "path": "/home/admin/Ziwei/projects/x402-api",
        "description": "x402 支付 API 服务",
        "files": [
            "app_production.py",
            "x402_gateway.py",
            "secure_executor.py",
            ".env"
        ]
    },
    {
        "name": "x402-python-sdk",
        "path": "/home/admin/Ziwei/projects/x402-python-sdk",
        "description": "x402 Python SDK",
        "files": [
            "x402/client.py",
            "x402/payment.py",
            "examples/basic_usage.py"
        ]
    },
    {
        "name": "x402-trading-bot",
        "path": "/home/admin/Ziwei/projects/x402-trading-bot",
        "description": "x402 交易机器人",
        "files": [
            "bot_simple.py"
        ]
    },
    {
        "name": "global-warroom",
        "path": "/home/admin/Ziwei/projects/global-warroom",
        "description": "全球战情室 - 原版",
        "files": [
            "scripts/web3-wallet-assistant.py",
            "scripts/data-validator.py",
            "scripts/stock-analysis.py"
        ]
    },
    {
        "name": "global-warroom-upgraded",
        "path": "/home/admin/Ziwei/projects/global-warroom-upgraded",
        "description": "全球战情室 - 升级版",
        "files": [
            "scripts/global-warroom-upgraded.py",
            "scripts/global-warroom.py"
        ]
    },
    {
        "name": "log-trim",
        "path": "/home/admin/Ziwei/projects/log-trim",
        "description": "日志修剪工具",
        "files": [
            "log-trim.py"
        ]
    }
]


def read_file_content(filepath):
    """读取文件内容"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            # 限制内容长度
            if len(content) > 5000:
                content = content[:5000] + "\n...[内容已截断]..."
            return content
    except:
        return "无法读取文件"


def audit_project(project):
    """审计单个项目"""
    print(f"\n{'='*70}")
    print(f"🔍 审计项目: {project['name']}")
    print(f"📁 路径: {project['path']}")
    print(f"📝 描述: {project['description']}")
    print(f"{'='*70}")

    # 检查项目是否存在
    if not os.path.exists(project['path']):
        print(f"❌ 项目不存在")
        return None

    # 检查关键文件
    files_status = {}
    for filename in project['files']:
        filepath = os.path.join(project['path'], filename)
        exists = os.path.exists(filepath)
        files_status[filename] = {
            "exists": exists,
            "size": os.path.getsize(filepath) if exists else 0
        }

    print(f"\n📂 文件检查:")
    for filename, status in files_status.items():
        icon = "✅" if status['exists'] else "❌"
        size = f"{status['size']} bytes" if status['exists'] else "不存在"
        print(f"  {icon} {filename}: {size}")

    # 读取关键文件内容进行安全审计
    print(f"\n🔒 安全审计 (关键文件内容分析):")

    security_issues = []

    for filename in project['files']:
        if not files_status[filename]['exists']:
            continue

        filepath = os.path.join(project['path'], filename)

        # 跳过大文件和二进制文件
        if files_status[filename]['size'] > 50000:
            print(f"  ⏭️  {filename}: 文件过大，跳过")
            continue

        content = read_file_content(filepath)

        # 安全检查
        dangerous_patterns = [
            "exec(",
            "eval(",
            "__import__('os')",
            "subprocess.system",
            "os.system",
            "pickle.loads",
            "yaml.load",
        ]

        found_issues = []
        for pattern in dangerous_patterns:
            if pattern in content:
                found_issues.append(pattern)

        if found_issues:
            security_issues.append({
                "file": filename,
                "issues": found_issues
            })

        # 显示文件摘要
        lines = content.split('\n')[:5]
        print(f"\n  📄 {filename} ({files_status[filename]['size']} bytes):")
        print(f"     预览:")
        for line in lines:
            if line.strip():
                print(f"     {line.strip()[:70]}")

        # 显示安全问题
        if found_issues:
            print(f"     ⚠️  发现潜在安全问题: {', '.join(found_issues)}")

    return {
        "name": project['name'],
        "files": files_status,
        "security_issues": security_issues
    }


def main():
    """主审计流程"""
    print("=" * 70)
    print("🔍 系统项目全面审计报告")
    print("=" * 70)
    print(f"📅 审计时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📊 项目数量: {len(PROJECTS)}")
    print()

    audit_results = []

    for project in PROJECTS:
        result = audit_project(project)
        if result:
            audit_results.append(result)

    # 生成汇总报告
    print("\n" + "=" * 70)
    print("📊 审计汇总")
    print("=" * 70)

    total_files = sum(len(r['files']) for r in audit_results)
    existing_files = sum(sum(1 for f in r['files'].values() if f['exists']) for r in audit_results)
    total_security_issues = sum(len(r['security_issues']) for r in audit_results)

    print(f"✅ 检查项目: {len(audit_results)}")
    print(f"📄 检查文件: {total_files}")
    print(f"✅ 存在文件: {existing_files}")
    print(f"❌ 缺失文件: {total_files - existing_files}")
    print(f"⚠️  安全问题: {total_security_issues}")

    print("\n📋 详细问题列表:")
    for result in audit_results:
        if result['security_issues']:
            print(f"\n  {result['name']}:")
            for issue in result['security_issues']:
                print(f"    - {issue['file']}: {', '.join(issue['issues'])}")

    # 保存审计报告
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_projects": len(audit_results),
        "total_files": total_files,
        "existing_files": existing_files,
        "security_issues": total_security_issues,
        "details": audit_results
    }

    report_file = "/home/admin/Ziwei/projects/AUDIT_REPORT.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\n💾 审计报告已保存: {report_file}")

    print("\n" + "=" * 70)
    print("✅ 审计完成")
    print("=" * 70)


if __name__ == "__main__":
    main()