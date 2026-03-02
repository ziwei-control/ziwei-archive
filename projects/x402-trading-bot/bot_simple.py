#!/usr/bin/env python3
# =============================================================================
# x402 生态交易机器人 - 简化版
# 功能：监控并模拟交易 x402 生态代币
# ⚠️ 警告：仅用于学习，不要使用真实资金！
# =============================================================================

import json
import time
from datetime import datetime
import random

# 目标代币配置
TOKENS = {
    "VIRTUAL": {"price": 1.40, "price_change": 0.80, "market_cap": 150000000},
    "PAYAI": {"price": 0.05191, "price_change": 12.81, "market_cap": 50000000},
    "PING": {"price": 0.02668, "price_change": -10.76, "market_cap": 10000000},
    "HEU": {"price": 0.036, "price_change": 1.72, "market_cap": 5000000}
}

# 交易配置
CONFIG = {
    "initial_balance": 100.0,  # 初始余额 USDT
    "max_position_size": 0.2,  # 最大仓位 20%
    "stop_loss": -0.10,         # 止损 -10%
    "take_profit": 0.05,       # 止盈 5%
    "update_interval": 5       # 价格更新间隔（秒）
}

# 交易记录
trades = []


class TradingBot:
    """x402 交易机器人"""

    def __init__(self):
        self.balance = CONFIG["initial_balance"]
        self.positions = {}
        self.start_time = datetime.now()

    def update_prices(self):
        """更新价格（模拟）"""
        for token, data in TOKENS.items():
            # 模拟价格波动 -2% 到 +2%
            change_percent = random.uniform(-0.02, 0.02)
            data["price"] *= (1 + change_percent)
            data["price_change"] = change_percent * 100

    def get_market_summary(self):
        """获取市场摘要"""
        summary = []
        total_market_cap = 0

        for token, data in TOKENS.items():
            total_market_cap += data["market_cap"]
            summary.append({
                "token": token,
                "price": data["price"],
                "change_24h": data["price_change"],
                "market_cap": data["market_cap"]
            })

        return {
            "total_market_cap": total_market_cap,
            "tokens": summary
        }

    def calculate_signals(self):
        """计算交易信号"""
        signals = {}

        for token, data in TOKENS.items():
            # 简单的买入/卖出信号
            if data["price_change"] > 3.0:
                signals[token] = "BUY"
            elif data["price_change"] < -3.0:
                signals[token] = "SELL"
            else:
                signals[token] = "HOLD"

        return signals

    def execute_trade(self, token, action):
        """执行交易（模拟）"""
        price = TOKENS[token]["price"]
        amount = CONFIG["max_position_size"] * self.balance

        if action == "BUY":
            if token not in self.positions:
                self.positions[token] = {
                    "amount": amount / price,
                    "entry_price": price,
                    "entry_time": datetime.now().isoformat()
                }
                self.balance -= amount

                trades.append({
                    "time": datetime.now().isoformat(),
                    "action": "BUY",
                    "token": token,
                    "price": price,
                    "amount_usdt": amount
                })

                return True

        elif action == "SELL":
            if token in self.positions:
                position = self.positions[token]
                amount_usdt = position["amount"] * price
                self.balance += amount_usdt

                # 计算收益
                pnl = (price - position["entry_price"]) / position["entry_price"]

                trades.append({
                    "time": datetime.now().isoformat(),
                    "action": "SELL",
                    "token": token,
                    "price": price,
                    "amount_usdt": amount_usdt,
                    "pnl": pnl * 100
                })

                del self.positions[token]
                return True

        return False

    def get_positions_value(self):
        """获取持仓价值"""
        value = 0.0
        for token, position in self.positions.items():
            price = TOKENS[token]["price"]
            value += position["amount"] * price
        return value

    def get_portfolio_summary(self):
        """获取投资组合摘要"""
        positions_value = self.get_positions_value()
        total_value = self.balance + positions_value
        pnl = (total_value - CONFIG["initial_balance"]) / CONFIG["initial_balance"] * 100

        return {
            "balance_usdt": self.balance,
            "positions_value": positions_value,
            "total_value": total_value,
            "pnl_percent": pnl,
            "positions_count": len(self.positions)
        }

    def run(self, iterations=10):
        """运行交易机器人"""
        print("=" * 70)
        print("🤖 x402 生态交易机器人 - 启动")
        print("=" * 70)
        print(f"⚠️ 警告：仅用于学习，不要使用真实资金！")
        print(f"💰 初始余额: ${CONFIG['initial_balance']}")
        print(f"🎯 最大仓位: {CONFIG['max_position_size'] * 100}%")
        print("=" * 70)
        print()

        for i in range(iterations):
            print(f"\n📊 第 {i+1}/{iterations} 轮 - {datetime.now().strftime('%H:%M:%S')}")

            # 更新价格
            self.update_prices()

            # 显示市场摘要
            market = self.get_market_summary()
            print(f"  市场总市值: ${market['total_market_cap']:,.0f}")
            for token_data in market["tokens"]:
                print(f"    {token_data['token']:8s}: ${token_data['price']:8.6f}  ({token_data['change_24h']:>+6.2f}%)")

            # 计算信号
            signals = self.calculate_signals()
            print(f"\n  🎯 交易信号:")
            for token, signal in signals.items():
                print(f"    {token}: {signal}")

                # 执行交易
                if signal in ["BUY", "SELL"]:
                    success = self.execute_trade(token, signal)
                    if success:
                        price = TOKENS[token]["price"]
                        print(f"      ✅ 执行 {signal} @ ${price:.6f}")

            # 显示投资组合
            portfolio = self.get_portfolio_summary()
            print(f"\n  💼 投资组合:")
            print(f"    可用余额: ${portfolio['balance_usdt']:,.2f}")
            print(f"    持仓价值: ${portfolio['positions_value']:,.2f}")
            print(f"    总价值:   ${portfolio['total_value']:,.2f}")
            print(f"    收益:     {portfolio['pnl_percent']:>+6.2f}%")

            # 显示持仓详情
            if portfolio['positions_count'] > 0:
                print(f"\n  📈 持仓详情:")
                for token, position in self.positions.items():
                    price = TOKENS[token]["price"]
                    entry_price = position["entry_price"]
                    pnl = (price - entry_price) / entry_price * 100
                    print(f"    {token}: {position['amount']:.2f} @ ${entry_price:.6f} (当前: ${price:.6f}, PnL: {pnl:+.2f}%)")

            print("-" * 70)

            # 等待
            time.sleep(1)

        # 最终总结
        print("\n" + "=" * 70)
        print("📊 交易总结")
        print("=" * 70)

        print(f"💰 初始余额: ${CONFIG['initial_balance']:.2f}")
        print(f"💼 最终价值: ${portfolio['total_value']:.2f}")
        print(f"📈 总收益: {portfolio['pnl_percent']:+.2f}%")

        print(f"\n📝 交易记录 ({len(trades)} 笔):")
        for i, trade in enumerate(trades, 1):
            print(f"  {i}. {trade['time']} {trade['action']:4s} {trade['token']:8s} @ ${trade['price']:.6f} (${trade['amount_usdt']:.2f})")

        print("=" * 70)
        print("⚠️ 再次提醒：仅用于学习，不要使用真实资金！")
        print("=" * 70)


def main():
    """主函数"""
    bot = TradingBot()

    # 运行 10 轮（模拟）
    bot.run(iterations=10)


if __name__ == "__main__":
    main()