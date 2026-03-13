#!/usr/bin/env python3
# =============================================================================
# 紧急修复 - 清理异常交易数据
# =============================================================================

import json
from pathlib import Path
from datetime import datetime

STRATEGY_DIR = Path("/home/admin/Ziwei/data/strategy")

def clean_trade_history():
    """清理异常交易记录"""
    jsonl_file = STRATEGY_DIR / "trade_history.jsonl"
    
    if not jsonl_file.exists():
        print("❌ 交易历史文件不存在")
        return
    
    # 读取所有交易
    trades = []
    with open(jsonl_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                trades.append(json.loads(line))
    
    print(f"原始交易数：{len(trades)}")
    
    # 过滤异常交易
    clean_trades = []
    removed_count = 0
    
    for trade in trades:
        amount = trade.get('amount', 0)
        value = trade.get('value', 0)
        
        # 保留正常交易（金额大于 0.001）
        if amount > 0.001 and value > 0.001:
            clean_trades.append(trade)
        else:
            removed_count += 1
    
    print(f"移除异常交易：{removed_count} 笔")
    print(f"清理后交易数：{len(clean_trades)}")
    
    # 保存清理后的数据
    with open(jsonl_file, 'w') as f:
        for trade in clean_trades:
            f.write(json.dumps(trade) + '\n')
    
    print("✅ 交易历史已清理")
    
    return clean_trades

def rebuild_account_status(trades):
    """从清理后的交易历史重建账户状态"""
    account_file = STRATEGY_DIR / "account_status.json"
    
    # 按币种分组
    by_symbol = {}
    for trade in trades:
        symbol = trade.get('symbol')
        if symbol not in by_symbol:
            by_symbol[symbol] = []
        by_symbol[symbol].append(trade)
    
    # 重建持仓
    portfolio = {}
    total_invested = 10000  # 初始资金
    
    for symbol, symbol_trades in by_symbol.items():
        # 找到首次建仓
        builds = [t for t in symbol_trades if t.get('type') == '建仓']
        adds = [t for t in symbol_trades if t.get('type') == '加仓']
        
        if not builds:
            continue
        
        # 使用首次建仓数据
        first_build = builds[0]
        
        # 计算总持仓和平均成本
        total_amount = first_build['amount']
        total_cost = first_build['value']
        
        for add in adds:
            total_amount += add['amount']
            total_cost += add['value']
        
        avg_price = total_cost / total_amount if total_amount > 0 else 0
        
        portfolio[symbol] = {
            'amount': total_amount,
            'entry_price': avg_price,
            'entry_time': first_build['time'],
            'stop_loss': first_build.get('stop_loss', avg_price * 0.95),
            'take_profit': first_build.get('take_profit', avg_price * 1.2)
        }
    
    # 计算剩余余额
    total_portfolio_value = sum(h['amount'] * h['entry_price'] for h in portfolio.values())
    remaining_balance = 10000 - total_portfolio_value
    
    # 重建账户状态
    account = {
        'balance': max(0, remaining_balance),
        'portfolio': portfolio,
        'daily_pnl': 0,
        'win_rate': 0,
        'total_trades': len([t for t in trades if t.get('type') in ['建仓', '加仓']]),
        'trade_history': trades[-100:],  # 保留最近 100 笔
        'timestamp': datetime.now().isoformat()
    }
    
    # 保存
    with open(account_file, 'w') as f:
        json.dump(account, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 账户状态已重建")
    print(f"   余额：${account['balance']:,.2f}")
    print(f"   持仓：{len(portfolio)} 个")
    
    return account

def main():
    print("=" * 80)
    print("🔧 紧急修复 - 清理异常交易数据")
    print("=" * 80)
    print()
    
    # 清理交易历史
    clean_trades = clean_trade_history()
    
    # 重建账户状态
    account = rebuild_account_status(clean_trades)
    
    print()
    print("=" * 80)
    print("✅ 修复完成")
    print("=" * 80)

if __name__ == "__main__":
    main()
