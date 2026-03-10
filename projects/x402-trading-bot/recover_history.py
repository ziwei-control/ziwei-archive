#!/usr/bin/env python3
# =============================================================================
# 交易历史恢复工具
# 用途：从备份和日志中恢复丢失的交易历史
# =============================================================================

import json
from pathlib import Path
from datetime import datetime
import re

STRATEGY_DIR = Path("/home/admin/Ziwei/data/strategy")
BACKUP_DIR = STRATEGY_DIR / "backup"
LOG_FILE = Path("/home/admin/Ziwei/data/logs/soul-trader/strategy_engine.out")

def load_from_jsonl():
    """从独立历史文件加载"""
    jsonl_file = STRATEGY_DIR / "trade_history.jsonl"
    if not jsonl_file.exists():
        return []
    
    trades = []
    with open(jsonl_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                trades.append(json.loads(line))
    
    print(f"✅ 从 trade_history.jsonl 加载：{len(trades)} 笔")
    return trades

def load_from_account_status():
    """从账户状态加载"""
    account_file = STRATEGY_DIR / "account_status.json"
    if not account_file.exists():
        return []
    
    with open(account_file) as f:
        account = json.load(f)
    
    history = account.get('trade_history', [])
    print(f"✅ 从 account_status.json 加载：{len(history)} 笔")
    return history

def load_from_backup():
    """从最新备份加载"""
    latest_backup = BACKUP_DIR / "account_status_latest.json"
    if not latest_backup.exists():
        return []
    
    with open(latest_backup) as f:
        account = json.load(f)
    
    history = account.get('trade_history', [])
    print(f"✅ 从最新备份加载：{len(history)} 笔")
    return history

def recover_from_logs():
    """从日志文件恢复"""
    if not LOG_FILE.exists():
        return []
    
    recovered = []
    with open(LOG_FILE, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    
    for line in lines:
        # 查找买入记录
        if '[模拟买入]' in line or '[模拟建仓]' in line or '[模拟加仓]' in line:
            match = re.search(r'\[(模拟 [买入建仓加仓]+)\]\s+(\w+):\s+([\d.]+)\s+@\s+\$([\d.]+)\s+=\s+\$([\d.]+)', line)
            if match:
                action = match.group(1)
                symbol = match.group(2)
                amount = float(match.group(3))
                price = float(match.group(4))
                value = float(match.group(5))
                
                trade_type = '建仓' if '建仓' in action else '加仓'
                recovered.append({
                    'type': trade_type,
                    'symbol': symbol,
                    'time': 'recovered_from_log',
                    'price': price,
                    'amount': amount,
                    'value': value,
                    'recovered': True
                })
    
    print(f"✅ 从日志恢复：{len(recovered)} 笔")
    return recovered

def merge_and_deduplicate(all_trades):
    """合并并去重"""
    seen = set()
    unique = []
    
    for trade in all_trades:
        key = f"{trade.get('symbol')}-{trade.get('time')}-{trade.get('amount')}"
        if key not in seen:
            seen.add(key)
            unique.append(trade)
    
    # 按时间排序
    unique.sort(key=lambda x: x.get('time', ''))
    
    return unique

def main():
    print("=" * 70)
    print("📜 交易历史恢复工具")
    print("=" * 70)
    
    # 从多个源加载
    all_trades = []
    all_trades.extend(load_from_jsonl())
    all_trades.extend(load_from_account_status())
    all_trades.extend(load_from_backup())
    all_trades.extend(recover_from_logs())
    
    # 合并去重
    unique_trades = merge_and_deduplicate(all_trades)
    
    print(f"\n📊 统计结果:")
    print(f"  原始总数：{len(all_trades)} 笔")
    print(f"  去重后：{len(unique_trades)} 笔")
    
    # 按币种统计
    by_symbol = {}
    for trade in unique_trades:
        symbol = trade.get('symbol', 'UNKNOWN')
        if symbol not in by_symbol:
            by_symbol[symbol] = 0
        by_symbol[symbol] += 1
    
    print(f"\n📦 按币种统计:")
    for symbol, count in sorted(by_symbol.items()):
        print(f"  {symbol}: {count} 笔")
    
    # 显示最近 10 笔
    print(f"\n📜 最近 10 笔交易:")
    for trade in unique_trades[-10:]:
        print(f"  {trade.get('type')} {trade.get('symbol')} @ {trade.get('time', 'N/A')[:19]}")
    
    # 保存恢复结果
    output_file = STRATEGY_DIR / "recovered_history.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(unique_trades, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 恢复结果已保存：{output_file}")
    print("=" * 70)

if __name__ == "__main__":
    main()
