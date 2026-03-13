#!/usr/bin/env python3
# =============================================================================
# 紫微智控 - 智能交易机器人 v2.0 (Soul Edition)
# 24 小时监控 | 情报驱动 | AI 决策 | 本金安全第一
# 
# ⚠️ 修改：不再启动子进程，由 Supervisor 直接管理
# =============================================================================

import os
import sys
import json
import time
import subprocess
from datetime import datetime
from pathlib import Path

# 路径配置
BOT_DIR = Path("/home/admin/Ziwei/projects/x402-trading-bot")
DATA_DIR = Path("/home/admin/Ziwei/data")
LOG_DIR = DATA_DIR / "logs" / "soul-trader"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# 进程管理（只监控，不启动）
PROCESSES = {
    'intel_collector': None,
    'strategy_engine': None,
}


def log(message: str):
    """日志输出"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_msg = f"[{timestamp}] {message}"
    print(log_msg)
    
    # 写入日志文件
    log_file = LOG_DIR / f"soul_trader_{datetime.now().strftime('%Y%m%d')}.log"
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(log_msg + '\n')


# =============================================================================
# ⚠️ 已禁用：子进程启动功能
# 现在由 Supervisor 直接管理 intel_collector 和 strategy_engine
# =============================================================================

def check_signals():
    """检查交易信号并执行"""
    log("📊 检查交易信号...")
    
    strategy_dir = Path("/home/admin/Ziwei/data/strategy")
    
    if not strategy_dir.exists():
        return
    
    # 获取最新信号文件
    signal_files = sorted(strategy_dir.glob("signals_*.json"), reverse=True)
    
    if not signal_files:
        log("⚠️ 暂无交易信号")
        return
    
    # 加载信号
    with open(signal_files[0], 'r') as f:
        signals = json.load(f)
    
    # 过滤强买入信号
    buy_signals = [s for s in signals if s['signal'] in ['STRONG_BUY', 'BUY']]
    
    if buy_signals:
        log(f"🎯 发现 {len(buy_signals)} 个买入信号:")
        for signal in buy_signals[:3]:  # 只显示前 3 个
            log(f"   {signal['symbol']}: {signal['signal']} (评分:{signal['score']})")
            log(f"      价格：${signal['price']:.6f} | 仓位：{signal['suggested_position']*100:.1f}%")
    else:
        log("✅ 暂无买入信号，继续监控")


def monitor_processes():
    """监控进程状态（只检查，不重启）"""
    log("🔍 监控进程状态...")
    
    # 检查 intel_collector
    result = subprocess.run("pgrep -f 'intel_collector.py'", shell=True, capture_output=True, text=True)
    if result.stdout.strip():
        pids = result.stdout.strip().split('\n')
        log(f"✅ intel_collector 运行中 (PID: {pids[0]})")
    else:
        log("❌ intel_collector 未运行（Supervisor 将自动重启）")
    
    # 检查 strategy_engine
    result = subprocess.run("pgrep -f 'strategy_engine_v3.py'", shell=True, capture_output=True, text=True)
    if result.stdout.strip():
        pids = result.stdout.strip().split('\n')
        log(f"✅ strategy_engine 运行中 (PID: {pids[0]})")
    else:
        log("❌ strategy_engine 未运行（Supervisor 将自动重启）")


def print_status():
    """打印系统状态"""
    print("\n" + "=" * 70)
    print("🤖 紫微智控 - 智能交易机器人 v2.0 (Soul Edition)")
    print("=" * 70)
    print(f"📅 时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📂 数据目录：{DATA_DIR}")
    print(f"📝 日志目录：{LOG_DIR}")
    print()
    
    # 进程状态
    print("📊 进程状态:")
    result = subprocess.run("pgrep -f 'intel_collector.py'", shell=True, capture_output=True, text=True)
    intel_pid = result.stdout.strip().split('\n')[0] if result.stdout.strip() else "未运行"
    print(f"   intel_collector: {intel_pid}")
    
    result = subprocess.run("pgrep -f 'strategy_engine_v3.py'", shell=True, capture_output=True, text=True)
    strategy_pid = result.stdout.strip().split('\n')[0] if result.stdout.strip() else "未运行"
    print(f"   strategy_engine: {strategy_pid}")
    
    print(f"   soul_trader: {os.getpid()}")
    print()


def main():
    """主函数 - 只做交易决策，不启动子进程"""
    log("=" * 70)
    log("🚀 紫微智控 - 智能交易机器人 v2.0 启动")
    log("=" * 70)
    log("📋 配置：Supervisor 管理所有进程，soul_trader 只做交易决策")
    log("=" * 70)
    
    # 等待 Supervisor 启动其他进程
    log("⏳ 等待 Supervisor 启动其他进程...")
    time.sleep(10)
    
    # 主循环
    check_interval = 60  # 60 秒检查一次信号
    
    while True:
        try:
            # 打印状态
            print_status()
            
            # 检查信号
            check_signals()
            
            # 监控进程（只检查，不重启）
            monitor_processes()
            
            # 等待
            log(f"⏳ 等待 {check_interval}秒后下次检查...")
            time.sleep(check_interval)
            
        except KeyboardInterrupt:
            log("\n🛑 收到停止信号")
            log("👋 智能交易机器人已停止")
            break
        
        except Exception as e:
            log(f"❌ 错误：{e}")
            time.sleep(60)


if __name__ == "__main__":
    main()
