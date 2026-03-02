#!/usr/bin/env python3
# 设置每日 8 点自动发送测试报告

import os
import subprocess

# Cron 任务内容 - 每日 8 点执行
CRON_JOB = "0 8 * * * cd /home/admin/Ziwei/projects/x402-trading-bot && /usr/bin/python3 /home/admin/Ziwei/projects/x402-trading-bot/send_daily_report.py >> /home/admin/Ziwei/projects/x402-trading-bot/cron.log 2>&1"

print("=" * 70)
print("⏰ 设置每日 8 点自动发送测试报告")
print("=" * 70)
print()

# 检查 crontab
try:
    # 获取当前 crontab
    result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
    current_crontab = result.stdout if result.returncode == 0 else ""

    # 检查是否已存在
    if 'send_daily_report.py' in current_crontab:
        print("⚠️  定时任务已存在")
    else:
        # 添加新任务
        new_crontab = current_crontab.strip() + "\n" + CRON_JOB if current_crontab.strip() else CRON_JOB

        # 写入 crontab
        process = subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate(input=new_crontab)

        if process.returncode == 0:
            print("✅ 定时任务设置成功")
            print()
            print("📋 任务详情:")
            print(f"  时间: 每日 08:00")
            print(f"  命令: send_daily_report.py")
            print(f"  收件人: 19922307306@189.cn")
            print()
        else:
            print(f"❌ 设置失败：{stderr}")

    # 显示当前 crontab
    print("📋 当前 crontab 任务:")
    print("-" * 70)
    result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
    if result.returncode == 0:
        for line in result.stdout.split('\n'):
            if line.strip():
                print(f"  {line}")
    else:
        print("  无定时任务")

    print()
    print("=" * 70)

except Exception as e:
    print(f"❌ 错误：{e}")
    print()
    print("手动设置方法:")
    print("  crontab -e")
    print("  添加:")
    print(f"  {CRON_JOB}")
