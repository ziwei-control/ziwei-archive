#!/usr/bin/env python3
# =============================================================================
# 紫微智控 - 智能交易机器人 v2.0 (Soul Edition)
# 24 小时监控 | 情报驱动 | AI 决策 | 本金安全第一
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

# 进程管理
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


def start_intel_collector():
    """启动情报搜集器"""
    log("🕵️ 启动情报搜集器...")
    
    proc = subprocess.Popen(
        ['python3', str(BOT_DIR / 'intel_collector.py')],
        stdout=open(LOG_DIR / 'intel_collector.out', 'a'),
        stderr=subprocess.STDOUT
    )
    
    PROCESSES['intel_collector'] = proc
    log(f"✅ 情报搜集器已启动 (PID: {proc.pid})")
    return proc


def start_strategy_engine():
    """启动策略引擎 v3.0"""
    log("🧠 启动策略引擎 v3.0 (AI 增强版)...")
    
    proc = subprocess.Popen(
        ['python3', str(BOT_DIR / 'strategy_engine_v3.py')],
        stdout=open(LOG_DIR / 'strategy_engine.out', 'a'),
        stderr=subprocess.STDOUT
    )
    
    PROCESSES['strategy_engine'] = proc
    log(f"✅ 策略引擎 v3.0 已启动 (PID: {proc.pid})")
    return proc


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
    """监控进程状态"""
    for name, proc in PROCESSES.items():
        if proc:
            if proc.poll() is not None:
                log(f"❌ {name} 进程已退出，重启中...")
                if name == 'intel_collector':
                    start_intel_collector()
                elif name == 'strategy_engine':
                    start_strategy_engine()
            else:
                log(f"✅ {name} 运行正常 (PID: {proc.pid})")


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
    for name, proc in PROCESSES.items():
        if proc:
            status = "✅ 运行中" if proc.poll() is None else "❌ 已退出"
            print(f"   {name}: {status}")
        else:
            print(f"   {name}: ⏸️ 未启动")
    
    # 最新信号摘要
    strategy_dir = Path("/home/admin/Ziwei/data/strategy")
    if strategy_dir.exists():
        signal_files = sorted(strategy_dir.glob("signals_*.json"), reverse=True)
        if signal_files:
            with open(signal_files[0], 'r') as f:
                signals = json.load(f)
            buy_count = len([s for s in signals if 'BUY' in s['signal']])
            print(f"\n📈 最新信号：{len(signals)}个代币分析，{buy_count}个买入信号")
    
    print("=" * 70 + "\n")


def main():
    """主函数"""
    log("=" * 70)
    log("🚀 紫微智控 - 智能交易机器人 v2.0 启动")
    log("=" * 70)
    
    # 启动子进程
    start_intel_collector()
    time.sleep(2)
    start_strategy_engine()
    
    # 等待情报搜集
    log("⏳ 等待情报数据...")
    time.sleep(30)
    
    # 主循环
    check_interval = 60  # 60 秒检查一次信号
    
    while True:
        try:
            # 打印状态
            print_status()
            
            # 检查信号
            check_signals()
            
            # 监控进程
            monitor_processes()
            
            # 等待
            log(f"⏳ 等待 {check_interval}秒后下次检查...")
            time.sleep(check_interval)
            
        except KeyboardInterrupt:
            log("\n🛑 收到停止信号，关闭所有进程...")
            
            for name, proc in PROCESSES.items():
                if proc:
                    proc.terminate()
                    log(f"✅ {name} 已停止")
            
            log("👋 智能交易机器人已停止")
            break
        
        except Exception as e:
            log(f"❌ 错误：{e}")
            time.sleep(60)


if __name__ == '__main__':
    main()
