#!/usr/bin/env python3
# =============================================================================
# 修复重复建仓问题 - 清理异常持仓数据
# 用途：分析并修复因策略引擎重启导致的重复建仓问题
# =============================================================================

import json
from pathlib import Path
from datetime import datetime

STRATEGY_DIR = Path("/home/admin/Ziwei/data/strategy")

def analyze_account_status():
    """分析当前账户状态"""
    account_file = STRATEGY_DIR / "account_status.json"
    
    if not account_file.exists():
        print("❌ 账户状态文件不存在")
        return None
    
    with open(account_file) as f:
        account = json.load(f)
    
    print("=" * 70)
    print("📊 当前账户状态分析")
    print("=" * 70)
    print(f"余额：${account.get('balance', 0):,.2f}")
    print(f"持仓数：{len(account.get('portfolio', {}))}")
    print(f"总交易：{account.get('total_trades', 0)} 笔")
    
    # 分析持仓
    portfolio = account.get('portfolio', {})
    total_value = 0
    
    print("\n📦 持仓详情:")
    for coin, holding in portfolio.items():
        value = holding['amount'] * holding['entry_price']
        total_value += value
        print(f"  {coin}: {holding['amount']:,.2f} @ ${holding['entry_price']:,.6f} = ${value:,.2f}")
    
    print(f"\n持仓总价值：${total_value:,.2f}")
    print(f"总资产：${account.get('balance', 0) + total_value:,.2f}")
    
    return account

def analyze_trade_history():
    """分析交易历史"""
    jsonl_file = STRATEGY_DIR / "trade_history.jsonl"
    
    if not jsonl_file.exists():
        print("❌ 交易历史文件不存在")
        return
    
    trades = []
    with open(jsonl_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                trades.append(json.loads(line))
    
    print("\n" + "=" * 70)
    print("📜 交易历史分析")
    print("=" * 70)
    print(f"总交易数：{len(trades)} 笔")
    
    # 按币种分组
    by_symbol = {}
    for trade in trades:
        symbol = trade.get('symbol', 'UNKNOWN')
        if symbol not in by_symbol:
            by_symbol[symbol] = []
        by_symbol[symbol].append(trade)
    
    print("\n按币种统计:")
    for symbol, symbol_trades in sorted(by_symbol.items()):
        builds = [t for t in symbol_trades if t.get('type') == '建仓']
        adds = [t for t in symbol_trades if t.get('type') == '加仓']
        closes = [t for t in symbol_trades if t.get('type') == '清仓']
        
        print(f"\n  {symbol}:")
        print(f"    建仓：{len(builds)} 次")
        if builds:
            print(f"      首次：{builds[0].get('time', 'N/A')[:19]}")
            print(f"      最后：{builds[-1].get('time', 'N/A')[:19]}")
        print(f"    加仓：{len(adds)} 次")
        if adds:
            # 检查是否有异常小的加仓
            tiny_adds = [t for t in adds if t.get('amount', 0) < 0.001]
            if tiny_adds:
                print(f"    ⚠️  异常小加仓：{len(tiny_adds)} 次")
        print(f"    清仓：{len(closes)} 次")
    
    # 检查重复建仓
    print("\n" + "=" * 70)
    print("🔍 重复建仓检测")
    print("=" * 70)
    
    for symbol, symbol_trades in sorted(by_symbol.items()):
        builds = [t for t in symbol_trades if t.get('type') == '建仓']
        
        if len(builds) > 1:
            print(f"\n⚠️  {symbol}: 重复建仓 {len(builds)} 次！")
            for i, build in enumerate(builds, 1):
                print(f"  第{i}次：{build.get('time', 'N/A')[:19]} - {build.get('amount', 0):,.2f} @ ${build.get('price', 0):,.6f}")

def fix_account_status():
    """修复账户状态（可选）"""
    print("\n" + "=" * 70)
    print("🔧 修复建议")
    print("=" * 70)
    print("""
如果发现重复建仓问题，执行以下步骤：

1. 停止策略引擎
   pkill -f strategy_engine_v3.py

2. 备份当前状态
   cp /home/admin/Ziwei/data/strategy/account_status.json \\
      /home/admin/Ziwei/data/strategy/backup/account_status_before_fix.json

3. 重启策略引擎（已修复代码）
   cd /home/admin/Ziwei/projects/x402-trading-bot
   nohup python3 strategy_engine_v3.py > \\
      /home/admin/Ziwei/data/logs/soul-trader/strategy_engine_v3.log 2>&1 &

4. 验证修复
   tail -30 /home/admin/Ziwei/data/logs/soul-trader/strategy_engine_v3.log | grep "恢复"
""")

def main():
    print("\n🔍 开始分析账户状态和交易历史...\n")
    
    # 分析当前状态
    account = analyze_account_status()
    
    # 分析交易历史
    analyze_trade_history()
    
    # 修复建议
    fix_account_status()
    
    print("\n" + "=" * 70)
    print("✅ 分析完成")
    print("=" * 70)

if __name__ == "__main__":
    main()
