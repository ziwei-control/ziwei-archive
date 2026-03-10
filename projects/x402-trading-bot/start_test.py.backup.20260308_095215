#!/usr/bin/env python3
# =============================================================================
# x402 交易机器人 - 测试启动脚本
# ⚠️ 测试模式：真实资金不动！
# =============================================================================

import os
import sys
from datetime import datetime

# 加载环境变量
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("❌ 缺少 python-dotenv，请安装：pip3 install python-dotenv")
    sys.exit(1)

print("=" * 70)
print("🤖 x402 交易机器人 - 测试模式启动")
print("=" * 70)
print()
print("⚠️  警告：这是测试模式，真实资金不会动用！")
print()

# 检查配置
test_mode = os.getenv("TEST_MODE", "true").lower() == "true"
dry_run = os.getenv("DRY_RUN", "true").lower() == "true"
api_key = os.getenv("API_KEY", "")
api_secret = os.getenv("API_SECRET", "")
initial_balance = float(os.getenv("INITIAL_BALANCE", "10"))
stop_loss = float(os.getenv("STOP_LOSS", "-0.10"))
take_profit = float(os.getenv("TAKE_PROFIT", "0.05"))
max_position = float(os.getenv("MAX_POSITION_SIZE", "0.2"))

print("📊 配置检查:")
print("-" * 70)
print(f"  测试模式: {'✅ 开启' if test_mode else '❌ 关闭'}")
print(f"  模拟下单: {'✅ 开启' if dry_run else '❌ 关闭'}")
print(f"  API Key: {'✅ 已配置' if api_key else '❌ 未配置'}")
print(f"  API Secret: {'✅ 已配置' if api_secret else '❌ 未配置'}")
print()
print("💰 资金配置:")
print(f"  初始资金: ${initial_balance} USDT (虚拟)")
print(f"  止损: {stop_loss*100:.1f}%")
print(f"  止盈: {take_profit*100:.1f}%")
print(f"  最大仓位: {max_position*100:.1f}%")
print()

if not api_key or not api_secret:
    print("❌ 错误：API 密钥未配置")
    sys.exit(1)

if not test_mode or not dry_run:
    print("⚠️  警告：测试模式或模拟模式未开启！")
    print("   建议设置 TEST_MODE=true 和 DRY_RUN=true")
    print()
    response = input("是否继续？(yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print("❌ 已取消")
        sys.exit(0)

print("=" * 70)
print("🚀 启动测试...")
print("=" * 70)
print()

# 导入并启动机器人
try:
    from bot_production import TradingBot, CONFIG

    # 创建机器人
    bot = TradingBot(CONFIG)

    # 连接交易所
    print("📡 连接 Binance...")
    if not bot.connect():
        print("❌ 连接失败")
        sys.exit(1)

    print("✅ 连接成功")
    print()

    # 显示余额
    balance = bot.connector.get_balance()
    usdt_balance = balance.get('USDT', {}).get('free', 0)
    print(f"💵 Binance 账户 USDT 余额: ${usdt_balance:.2f}")
    print(f"💵 测试虚拟资金: ${initial_balance:.2f}")
    print()

    # 启动
    print("🔄 开始监控市场...")
    print()
    print("📋 交易对:")
    print("  - VIRTUAL/USDT")
    print("  - PAYAI/USDT")
    print("  - PING/USDT")
    print()
    print("📊 监控中... (按 Ctrl+C 停止)")
    print()

    # 启动主循环
    bot.start()
    bot.run()

except KeyboardInterrupt:
    print()
    print("🛑 用户中断，正在停止...")
    bot.stop()
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 70)
print("✅ 测试完成")
print("=" * 70)