#!/usr/bin/env python3
"""
自动同步监控 - 安全版本
修复: eval → ast.literal_eval
"""

import os
import sys
import json
import ast
import hashlib
from pathlib import Path
from datetime import datetime, timedelta

# 路径配置
Ziwei_DIR = Path("/home/admin/Ziwei")
STATE_FILE = Ziwei_DIR / "data" / "sync_state.json"

def load_state():
    """加载状态 - 使用 ast.literal_eval 替代 eval"""
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                # ✅ 安全：使用 ast.literal_eval 替代 eval
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

def main():
    """主函数"""
    print("✅ 自动同步监控 - 安全版本")
    state = load_state()
    print(f"📊 最后同步：{state.get('last_sync', '从未')}")

if __name__ == "__main__":
    main()
