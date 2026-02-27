#!/usr/bin/env python3
"""
紫微智控 - 自动巡查同步脚本
功能：
  1. 每 30 分钟巡查一次
  2. 发现更新自动同步到 GitHub 和 Gitee
  3. 每日 23:40 强制同步
"""

import os
import sys
import time
import subprocess
import hashlib
from datetime import datetime
from pathlib import Path

# 路径配置
Ziwei_DIR = Path("/home/admin/Ziwei")
DATA_DIR = Ziwei_DIR / "data"
LOGS_DIR = DATA_DIR / "logs"
STATE_FILE = DATA_DIR / "sync_state.json"

# 巡查间隔（秒）
WATCH_INTERVAL = 30 * 60  # 30 分钟

# 每日强制同步时间
DAILY_SYNC_HOUR = 23
DAILY_SYNC_MINUTE = 40


def log(message, level="INFO"):
    """记录日志"""
    timestamp = datetime.now().isoformat()
    log_line = f"[{timestamp}] [{level}] {message}"
    print(log_line)
    
    # 写入日志文件
    log_file = LOGS_DIR / f"auto_sync_{datetime.now().strftime('%Y%m%d')}.log"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(log_line + "\n")


def get_git_status():
    """获取 Git 状态"""
    try:
        # 检查是否有未提交的更改
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=Ziwei_DIR,
            capture_output=True,
            text=True
        )
        return result.stdout.strip()
    except Exception as e:
        log(f"获取 Git 状态失败：{e}", "ERROR")
        return None


def get_file_hash(filepath):
    """获取文件 MD5 哈希"""
    try:
        with open(filepath, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()
    except:
        return None


def load_state():
    """加载状态"""
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return eval(f.read())
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
            f.write(str(state))
        return True
    except Exception as e:
        log(f"保存状态失败：{e}", "ERROR")
        return False


def check_changes(state):
    """检查是否有更改"""
    log("检查文件更改...")
    
    # 获取 Git 状态
    git_status = get_git_status()
    if git_status:
        log(f"发现 Git 更改:\n{git_status}", "WARN")
        return True
    
    # 检查关键文件哈希
    key_files = [
        Ziwei_DIR / "config" / "agents.yaml",
        Ziwei_DIR / "README.md",
    ]
    
    current_hashes = {}
    for filepath in key_files:
        if filepath.exists():
            file_hash = get_file_hash(filepath)
            current_hashes[str(filepath)] = file_hash
            
            if str(filepath) in state["file_hashes"]:
                if state["file_hashes"][str(filepath)] != file_hash:
                    log(f"文件更改：{filepath.name}", "WARN")
                    return True
            else:
                # 新文件
                state["file_hashes"][str(filepath)] = file_hash
    
    # 检查 SOP 和 docs 目录
    for dir_path in [Ziwei_DIR / "SOP", Ziwei_DIR / "docs"]:
        if dir_path.exists():
            for md_file in dir_path.glob("*.md"):
                file_hash = get_file_hash(md_file)
                current_hashes[str(md_file)] = file_hash
                
                if str(md_file) in state["file_hashes"]:
                    if state["file_hashes"][str(md_file)] != file_hash:
                        log(f"文档更改：{md_file.name}", "WARN")
                        return True
                else:
                    state["file_hashes"][str(md_file)] = file_hash
    
    # 更新文件哈希
    state["file_hashes"].update(current_hashes)
    save_state(state)
    
    log("未发现更改")
    return False


def run_sync(reason="定时巡查"):
    """运行同步脚本"""
    log(f"开始同步（原因：{reason}）...")
    
    sync_script = Ziwei_DIR / "scripts" / "sync-to-both.sh"
    
    if not sync_script.exists():
        log("同步脚本不存在", "ERROR")
        return False
    
    try:
        result = subprocess.run(
            ["bash", str(sync_script)],
            cwd=Ziwei_DIR,
            capture_output=True,
            text=True,
            timeout=300  # 5 分钟超时
        )
        
        # 输出日志
        if result.stdout:
            log(f"同步输出:\n{result.stdout}")
        
        if result.stderr:
            log(f"同步错误:\n{result.stderr}", "ERROR")
        
        if result.returncode == 0:
            log("同步成功", "SUCCESS")
            return True
        else:
            log(f"同步失败（退出码：{result.returncode}）", "ERROR")
            return False
    
    except subprocess.TimeoutExpired:
        log("同步超时（>5 分钟）", "ERROR")
        return False
    except Exception as e:
        log(f"同步异常：{e}", "ERROR")
        return False


def should_daily_sync():
    """检查是否应该执行每日同步"""
    now = datetime.now()
    
    # 检查时间是否在 23:40-23:45 之间
    if now.hour == DAILY_SYNC_HOUR and DAILY_SYNC_MINUTE <= now.minute <= DAILY_SYNC_MINUTE + 5:
        return True
    
    return False


def main():
    """主循环"""
    log("=" * 60)
    log("紫微智控 - 自动巡查同步启动")
    log(f"巡查间隔：{WATCH_INTERVAL // 60} 分钟")
    log(f"每日同步：{DAILY_SYNC_HOUR}:{DAILY_SYNC_MINUTE:02d}")
    log("=" * 60)
    
    # 加载状态
    state = load_state()
    log(f"上次巡查：{state.get('last_check', '无')}")
    log(f"上次同步：{state.get('last_sync', '无')}")
    log(f"上次每日同步：{state.get('last_daily_sync', '无')}")
    
    # 确保日志目录存在
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    
    # 主循环
    while True:
        try:
            now = datetime.now()
            current_time = now.isoformat()
            
            # 更新巡查时间
            state["last_check"] = current_time
            save_state(state)
            
            log(f"第 {state.get('check_count', 0) + 1} 次巡查")
            
            # 检查是否需要每日同步
            if should_daily_sync():
                today = now.strftime("%Y-%m-%d")
                if state.get("last_daily_sync") != today:
                    log("触发每日定时同步（23:40）", "INFO")
                    run_sync("每日定时同步")
                    state["last_daily_sync"] = today
                    state["last_sync"] = current_time
                    save_state(state)
                else:
                    log("今日已执行每日同步", "INFO")
            
            # 检查是否有更改
            has_changes = check_changes(state)
            
            if has_changes:
                log("发现更改，触发自动同步", "WARN")
                success = run_sync("自动检测更改")
                
                if success:
                    state["last_sync"] = current_time
                    save_state(state)
            else:
                log("无更改，跳过同步")
            
            # 更新巡查计数
            state["check_count"] = state.get("check_count", 0) + 1
            save_state(state)
            
            # 等待下次巡查
            log(f"下次巡查：{WATCH_INTERVAL // 60} 分钟后")
            time.sleep(WATCH_INTERVAL)
            
        except KeyboardInterrupt:
            log("收到停止信号，正常退出", "WARN")
            break
        except Exception as e:
            log(f"巡查异常：{e}", "ERROR")
            time.sleep(60)  # 异常后等待 1 分钟重试
    
    log("自动巡查同步已停止")


if __name__ == "__main__":
    main()
