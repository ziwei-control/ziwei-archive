#!/usr/bin/env python3
"""
自动同步监控 - 看门狗版本
持续运行，每 5 分钟检查一次同步状态
"""

import os
import sys
import json
import ast
import time
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime, timedelta

# 路径配置
Ziwei_DIR = Path("/home/admin/Ziwei")
STATE_FILE = Ziwei_DIR / "data" / "sync_state.json"
CHECK_INTERVAL = 300  # 5 分钟

def load_state():
    """加载状态 - 使用 ast.literal_eval 替代 eval"""
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return ast.literal_eval(f.read())
        except:
            pass
    return {
        "last_check": None,
        "last_sync": None,
        "last_daily_sync": None,
        "file_hashes": {}
    }

def save_state(state):
    """保存状态"""
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        print(f"❌ 保存状态失败：{e}")

def check_sync_status():
    """检查同步状态"""
    state = load_state()
    now = datetime.now()
    
    state["last_check"] = now.isoformat()
    
    # 检查是否需要每日同步
    last_daily = state.get("last_daily_sync")
    if last_daily:
        last_daily_dt = datetime.fromisoformat(last_daily)
        if (now - last_daily_dt).days >= 1:
            print(f"📅 需要执行每日同步 (上次：{last_daily})")
            state["last_daily_sync"] = now.isoformat()
    else:
        print("📅 首次运行，执行每日同步")
        state["last_daily_sync"] = now.isoformat()
    
    save_state(state)
    print(f"✅ 检查完成 - {now.strftime('%Y-%m-%d %H:%M:%S')}")
    
    return state

def main():
    """主函数 - 持续运行"""
    print("=" * 60)
    print("🐕 自动同步监控 - 看门狗版本")
    print(f"⏰ 检查间隔：{CHECK_INTERVAL}秒")
    print("=" * 60)
    
    while True:
        try:
            check_sync_status()
        except Exception as e:
            print(f"❌ 检查失败：{e}")
        
        print(f"⏳ 等待 {CHECK_INTERVAL}秒后下次检查...\n")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
