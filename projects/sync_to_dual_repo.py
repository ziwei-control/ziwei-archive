#!/usr/bin/env python3
# =============================================================================
# 双库同步脚本 - GitHub + Gitee
# =============================================================================

import os
import subprocess
from datetime import datetime

# 项目列表
PROJECTS = [
    {
        "name": "x402-api",
        "path": "/home/admin/Ziwei/projects/x402-api",
        "description": "x402 支付 API 服务 - 让 AI 智能体自主付费"
    },
    {
        "name": "x402-python-sdk",
        "path": "/home/admin/Ziwei/projects/x402-python-sdk",
        "description": "x402 Python SDK - 让 Python 开发者轻松集成 x402 协议"
    },
    {
        "name": "x402-trading-bot",
        "path": "/home/admin/Ziwei/projects/x402-trading-bot",
        "description": "x402 交易机器人 - 自动交易 x402 生态代币"
    }
]

# 仓库配置
GITHUB_BASE = "https://github.com/ziwei"
GITEE_BASE = "https://gitee.com/ziwei"


def setup_remote(project_path, project_name):
    """配置双仓库远程"""
    os.chdir(project_path)

    # 检查是否已有 remote
    result = subprocess.run(['git', 'remote', '-v'], capture_output=True, text=True)

    has_github = 'github' in result.stdout.lower()
    has_gitee = 'gitee' in result.stdout.lower()

    print(f"\n📋 配置远程仓库:")

    if not has_github:
        github_url = f"{GITHUB_BASE}/{project_name}.git"
        subprocess.run(['git', 'remote', 'add', 'github', github_url])
        print(f"  ✅ 添加 GitHub: {github_url}")
    else:
        print(f"  ✅ GitHub 已配置")

    if not has_gitee:
        gitee_url = f"{GITEE_BASE}/{project_name}.git"
        subprocess.run(['git', 'remote', 'add', 'gitee', gitee_url])
        print(f"  ✅ 添加 Gitee: {gitee_url}")
    else:
        print(f"  ✅ Gitee 已配置")


def add_and_commit(project_path, message):
    """添加文件并提交"""
    os.chdir(project_path)

    # 添加所有文件
    subprocess.run(['git', 'add', '.'])

    # 提交
    subprocess.run(['git', 'commit', '-m', message])

    print(f"  ✅ 提交：{message}")


def push_to_both(project_path):
    """推送到双库"""
    os.chdir(project_path)

    print(f"\n🚀 推送到双库:")

    # 推送到 GitHub
    print("  📤 推送到 GitHub...")
    result = subprocess.run(['git', 'push', 'github', 'main'], capture_output=True, text=True)
    if result.returncode == 0:
        print("  ✅ GitHub 推送成功")
    else:
        print(f"  ⚠️  GitHub 推送失败：{result.stderr[:100]}")

    # 推送到 Gitee
    print("  📤 推送到 Gitee...")
    result = subprocess.run(['git', 'push', 'gitee', 'main'], capture_output=True, text=True)
    if result.returncode == 0:
        print("  ✅ Gitee 推送成功")
    else:
        print(f"  ⚠️  Gitee 推送失败：{result.stderr[:100]}")


def main():
    """主函数"""
    print("=" * 70)
    print("🔄 三项目双库同步 - GitHub + Gitee")
    print("=" * 70)
    print(f"📅 时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    commit_message = f"🚀 三项目完整部署 - {datetime.now().strftime('%Y-%m-%d')}\n\n- 项目 1: x402 API (生产环境)\n- 项目 2: x402 Python SDK (CodeCanyon 准备)\n- 项目 3: x402 交易机器人 (测试模式)\n\n✅ 完整文档和配置"

    for project in PROJECTS:
        print(f"\n{'='*70}")
        print(f"📦 项目：{project['name']}")
        print(f"📝 描述：{project['description']}")
        print(f"{'='*70}")

        # 配置远程
        setup_remote(project['path'], project['name'])

        # 添加并提交
        add_and_commit(project['path'], commit_message)

        # 推送到双库
        push_to_both(project['path'])

        print()

    print("=" * 70)
    print("✅ 三项目双库同步完成")
    print("=" * 70)
    print()
    print("📍 仓库地址:")
    for project in PROJECTS:
        print(f"\n  {project['name']}:")
        print(f"    GitHub: {GITHUB_BASE}/{project['name']}")
        print(f"    Gitee:  {GITEE_BASE}/{project['name']}")

    print()
    print("=" * 70)


if __name__ == "__main__":
    main()
