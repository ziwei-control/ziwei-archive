#!/usr/bin/env python3
# =============================================================================
# 双库同步脚本 - GitHub + Gitee (全项目版)
# =============================================================================

import os
import subprocess
from datetime import datetime

# 项目列表（10 个项目）
PROJECTS = [
    # x402 系列 (ziwei 组织)
    {
        "name": "x402-api",
        "path": "/home/admin/Ziwei/projects/x402-api",
        "description": "x402 支付 API 服务 - 让 AI 智能体自主付费",
        "github_org": "ziwei",
        "gitee_user": "ziwei"
    },
    {
        "name": "x402-python-sdk",
        "path": "/home/admin/Ziwei/projects/x402-python-sdk",
        "description": "x402 Python SDK - 让 Python 开发者轻松集成 x402 协议",
        "github_org": "ziwei",
        "gitee_user": "ziwei"
    },
    {
        "name": "x402-trading-bot",
        "path": "/home/admin/Ziwei/projects/x402-trading-bot",
        "description": "x402 交易机器人 - 自动交易 x402 生态代币",
        "github_org": "ziwei",
        "gitee_user": "ziwei"
    },
    # ziwei-control 系列
    {
        "name": "runtask",
        "path": "/home/admin/Ziwei/projects/runtask",
        "description": "任务运行管理工具",
        "github_org": "ziwei-control",
        "gitee_user": "pandac0"
    },
    {
        "name": "look",
        "path": "/home/admin/Ziwei/projects/look",
        "description": "视觉识别工具",
        "github_org": "ziwei-control",
        "gitee_user": "pandac0"
    },
    {
        "name": "log-trim",
        "path": "/home/admin/Ziwei/projects/log-trim",
        "description": "日志清理工具",
        "github_org": "ziwei-control",
        "gitee_user": "pandac0"
    },
    {
        "name": "ai_no1_ruyi",
        "path": "/home/admin/Ziwei/projects/ai_no1_ruyi",
        "description": "AI 如意助手",
        "github_org": "ziwei-control",
        "gitee_user": "pandac0"
    },
    {
        "name": "global-warroom",
        "path": "/home/admin/Ziwei/projects/global-warroom",
        "description": "全球战情室监控面板",
        "github_org": "ziwei-control",
        "gitee_user": "pandac0"
    },
    {
        "name": "learn-system",
        "path": "/home/admin/Ziwei/projects/learn-system",
        "description": "学习系统",
        "github_org": "ziwei-control",
        "gitee_user": "pandac0"
    },
    {
        "name": "ziwei-audit-system",
        "path": "/home/admin/Ziwei/projects/ziwei-audit-system",
        "description": "紫微审计系统",
        "github_org": "ziwei-control",
        "gitee_user": "pandac0"
    },
]


def setup_remote(project):
    """配置双仓库远程"""
    project_path = project['path']
    project_name = project['name']
    github_org = project.get('github_org', 'ziwei')
    gitee_user = project.get('gitee_user', 'ziwei')
    
    os.chdir(project_path)

    # 检查是否已有 remote
    result = subprocess.run(['git', 'remote', '-v'], capture_output=True, text=True)

    has_github = 'github' in result.stdout.lower()
    has_gitee = 'gitee' in result.stdout.lower()

    print(f"\n📋 配置远程仓库:")

    if not has_github:
        github_url = f"git@github.com:{github_org}/{project_name}.git"
        subprocess.run(['git', 'remote', 'add', 'github', github_url])
        print(f"  ✅ 添加 GitHub: {github_url}")
    else:
        print(f"  ✅ GitHub 已配置")

    if not has_gitee:
        gitee_url = f"git@gitee.com:{gitee_user}/{project_name}.git"
        subprocess.run(['git', 'remote', 'add', 'gitee', gitee_url])
        print(f"  ✅ 添加 Gitee: {gitee_url}")
    else:
        print(f"  ✅ Gitee 已配置")


def add_and_commit(project_path, message):
    """添加文件并提交"""
    os.chdir(project_path)

    # 检查是否有更改
    status = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
    
    if not status.stdout.strip():
        print(f"  ⏭️  无更改，跳过提交")
        return False

    # 添加所有文件
    subprocess.run(['git', 'add', '.'])

    # 提交
    subprocess.run(['git', 'commit', '-m', message])

    print(f"  ✅ 提交：{message}")
    return True


def push_to_both(project_path, project_name):
    """推送到双库"""
    os.chdir(project_path)

    print(f"\n🚀 推送到双库:")

    # 获取当前分支
    branch_result = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], capture_output=True, text=True)
    branch = branch_result.stdout.strip()
    print(f"  📍 分支：{branch}")

    # 推送到 GitHub
    print("  📤 推送到 GitHub...")
    result = subprocess.run(['git', 'push', 'github', branch], capture_output=True, text=True)
    if result.returncode == 0:
        print("  ✅ GitHub 推送成功")
    else:
        print(f"  ⚠️  GitHub 推送失败：{result.stderr[:100]}")

    # 推送到 Gitee
    print("  📤 推送到 Gitee...")
    result = subprocess.run(['git', 'push', 'gitee', branch], capture_output=True, text=True)
    if result.returncode == 0:
        print("  ✅ Gitee 推送成功")
    else:
        print(f"  ⚠️  Gitee 推送失败：{result.stderr[:100]}")


def main():
    """主函数"""
    print("=" * 70)
    print(f"🔄 Ziwei 全项目双库同步 ({len(PROJECTS)} 个项目)")
    print("=" * 70)
    print(f"📅 时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    commit_message = f"🚀 全项目同步 - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n- x402 系列：API, SDK, Trading Bot\n- Control 系列：runtask, look, log-trim, ai_no1_ruyi, global-warroom, learn-system, audit\n\n✅ 完整文档和配置"

    success_count = 0
    skip_count = 0

    for project in PROJECTS:
        print(f"\n{'='*70}")
        print(f"📦 项目：{project['name']}")
        print(f"📝 描述：{project['description']}")
        print(f"{'='*70}")

        try:
            # 配置远程
            setup_remote(project)

            # 添加并提交
            has_changes = add_and_commit(project['path'], commit_message)
            
            if not has_changes:
                skip_count += 1
                print(f"  ℹ️  无更改，跳过推送")
            else:
                # 推送到双库
                push_to_both(project['path'], project['name'])
            
            success_count += 1
        except Exception as e:
            print(f"  ❌ 错误：{e}")

        print()

    print("=" * 70)
    print(f"✅ 同步完成：{success_count}/{len(PROJECTS)} 个项目")
    print(f"ℹ️  跳过：{skip_count} 个（无更改）")
    print("=" * 70)
    print()
    print("📍 仓库地址:")
    
    for project in PROJECTS:
        github_org = project.get('github_org', 'ziwei')
        gitee_user = project.get('gitee_user', 'ziwei')
        print(f"\n  {project['name']}:")
        print(f"    GitHub: https://github.com/{github_org}/{project['name']}")
        print(f"    Gitee:  https://gitee.com/{gitee_user}/{project['name']}")

    print()
    print("=" * 70)


if __name__ == "__main__":
    main()
