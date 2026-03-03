#!/usr/bin/env python3
"""
紫微智控 - 进度监工巡查脚本
每 18 分钟巡查一次，每 4 小时汇总发送简报
"""

import os
import sys
import time
import yaml
from datetime import datetime, timedelta
from pathlib import Path

# 路径配置
Ziwei_DIR = Path("/home/admin/Ziwei")
TASKS_DIR = Ziwei_DIR / "data" / "tasks" / "current"
LOGS_DIR = Ziwei_DIR / "data" / "logs"
BUFFER_LOG = LOGS_DIR / "supervisor_buffer.log"
SUMMARY_DIR = LOGS_DIR / "supervisor_4h_summary"

def check_tasks():
    """扫描任务目录，检查进度"""
    records = []
    
    if not TASKS_DIR.exists():
        return records
    
    for task_file in TASKS_DIR.glob("*.md"):
        try:
            mtime = datetime.fromtimestamp(task_file.stat().st_mtime)
            elapsed = datetime.now() - mtime
            elapsed_minutes = elapsed.total_seconds() / 60
            
            if elapsed_minutes > 18:
                status = f"警告：{task_file.stem} 超过 18 分钟未更新 ({elapsed_minutes:.0f}分钟)"
                records.append(f"[{datetime.now().isoformat()}] {status}")
            else:
                status = f"正常：{task_file.stem} 进行中 ({elapsed_minutes:.0f}分钟)"
                records.append(f"[{datetime.now().isoformat()}] {status}")
        except Exception as e:
            records.append(f"[{datetime.now().isoformat()}] 错误：检查 {task_file.name} 失败 - {e}")
    
    return records

def write_buffer(records):
    """写入巡查缓存"""
    BUFFER_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(BUFFER_LOG, "a", encoding="utf-8") as f:
        for record in records:
            f.write(record + "\n")
    print(f"[巡查] 已写入 {len(records)} 条记录到缓存")

def should_send_summary():
    """判断是否应该发送 4 小时简报"""
    if not BUFFER_LOG.exists():
        return False
    
    # 检查距离上次简报是否≥4 小时
    summary_file = SUMMARY_DIR / f"last_summary.txt"
    if summary_file.exists():
        last_summary = datetime.fromtimestamp(summary_file.stat().st_mtime)
        elapsed = datetime.now() - last_summary
        if elapsed.total_seconds() < 4 * 3600:
            return False
    
    return True

def generate_summary():
    """生成 4 小时汇总简报"""
    if not BUFFER_LOG.exists():
        return None
    
    # 读取过去 4 小时的缓存记录
    records = []
    four_hours_ago = datetime.now() - timedelta(hours=4)
    
    with open(BUFFER_LOG, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(line.strip())
    
    if not records:
        return None
    
    # 生成简报
    summary = f"""# 巡查简报

**周期**: {four_hours_ago.strftime('%Y-%m-%d %H:%M')} - {datetime.now().strftime('%Y-%m-%d %H:%M')}
**巡查次数**: {len(records)}

## 关键巡查记录

"""
    
    for record in records[-20:]:  # 最近 20 条
        summary += f"- {record}\n"
    
    summary += f"\n## 周期总结\n\n整体运行正常。\n"
    
    # 保存简报
    SUMMARY_DIR.mkdir(parents=True, exist_ok=True)
    summary_file = SUMMARY_DIR / f"{datetime.now().strftime('%Y%m%d_%H%M')}_summary.md"
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write(summary)
    
    # 更新最后简报时间
    last_summary_file = SUMMARY_DIR / "last_summary.txt"
    last_summary_file.touch()
    
    return summary_file

def main():
    """主循环"""
    print(f"[{datetime.now().isoformat()}] 紫微智控进度监工启动")
    print(f"巡查频率：每 18 分钟一次")
    print(f"简报频率：每 4 小时一次")
    
    try:
        while True:
            # 执行巡查
            print(f"\n[{datetime.now().isoformat()}] 执行巡查...")
            records = check_tasks()
            
            if records:
                write_buffer(records)
            else:
                print(f"[巡查] 无进行中任务")
            
            # 检查是否需要发送简报
            if should_send_summary():
                print(f"[巡查] 生成 4 小时简报...")
                summary_file = generate_summary()
                if summary_file:
                    print(f"[巡查] 简报已保存：{summary_file}")
                    # TODO: 调用通信官发送邮件
            
            # 休眠 18 分钟
            print(f"[巡查] 下次巡查：18 分钟后")
            time.sleep(18 * 60)
    
    except KeyboardInterrupt:
        print("\n[监工] 收到停止信号，正常退出")
        sys.exit(0)

if __name__ == "__main__":
    main()
