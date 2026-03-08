#!/usr/bin/env python3
# =============================================================================
# x402 交易机器人 - 正式版
# 功能：真实交易所API连接 + 真实资金操作
# ⚠️ 警告：高风险！仅使用能承受损失的资金！
# =============================================================================

import os
import sys
import json
import time
import datetime
from typing import Dict, Optional, List, Tuple

# 检查依赖
try:
    import ccxt
    from web3 import Web3
except ImportError as e:
    print(f"❌ 缺少依赖库: {e}")
    print("请安装: pip3 install ccxt web3 python-dotenv")
    sys.exit(1)

# 导入实时价格获取器
try:
    from get_realtime_prices import BinancePriceFetcher
    price_fetcher = BinancePriceFetcher()
except ImportError:
    price_fetcher = None
    print("⚠️  警告：无法导入 BinancePriceFetcher，将使用 CCXT 获取价格")

# 加载环境变量
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# 配置
CONFIG = {
    # 交易所配置
    "exchange": os.getenv("EXCHANGE", "binance"),
    "api_key": os.getenv("API_KEY", ""),
    "api_secret": os.getenv("API_SECRET", ""),
    
    # 钱包配置
    "wallet_private_key": os.getenv("WALLET_PRIVATE_KEY", ""),
    "wallet_network": os.getenv("WALLET_NETWORK", "mainnet"),
    
    # 风险控制
    "max_position_size": float(os.getenv("MAX_POSITION_SIZE", "0.2")),  # 最大仓位 20%
    "stop_loss": float(os.getenv("STOP_LOSS", "-0.10")),  # 止损 -10%
    "take_profit": float(os.getenv("TAKE_PROFIT", "0.05")),  # 止盈 +5%
    "max_drawdown": float(os.getenv("MAX_DOWNDOWN", "-0.15")),  # 最大回撤 -15%
    
    # 测试模式
    "test_mode": os.getenv("TEST_MODE", "true").lower() == "true",  # 测试订单模式
    "dry_run": os.getenv("DRY_RUN", "true").lower() == "true",  # 模拟下单（不真实交易）
    
    # 监控配置
    "update_interval": 5,  # 价格更新间隔（秒）
    "check_interval": 60,  # 风险检查间隔（秒）
    "log_file": "trades.log",
    
    # 模拟账户配置
    "initial_balance": float(os.getenv("INITIAL_BALANCE", "10000")),  # 初始模拟余额 $10,000
    "min_balance": 10.0  # 最小交易余额 $10
}


class RealExchangeConnector:
    """真实交易所连接器"""
    
    def __init__(self, exchange: str, api_key: str, api_secret: str):
        try:
            self.exchange_class = getattr(ccxt, exchange)
            self.exchange = self.exchange_class({
                'apiKey': api_key,
                'secret': api_secret,
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'future'  # 优先使用合约
                }
            })
            self.exchange_name = exchange
            print(f"✅ 已连接到 {exchange}")
        except Exception as e:
            raise Exception(f"连接交易所失败: {e}")
    
    def get_balance(self) -> Dict:
        """获取账户余额"""
        try:
            return self.exchange.fetch_balance()
        except Exception as e:
            print(f"❌ 获取余额失败: {e}")
            return {}
    
    def get_ticker(self, symbol: str) -> Dict:
        """获取当前价格（优先使用币安实时 API）"""
        try:
            # 优先使用币安实时 API
            if price_fetcher:
                binance_symbol = symbol.replace('/', '')
                price = price_fetcher.get_price(binance_symbol)
                if price > 0:
                    return {
                        'symbol': symbol,
                        'last': price,
                        'bid': price * 0.999,
                        'ask': price * 1.001,
                        'timestamp': datetime.datetime.now().timestamp() * 1000,
                        'datetime': datetime.datetime.now().isoformat(),
                        'source': 'Binance'
                    }
            
            # 回退到 CCXT
            return self.exchange.fetch_ticker(symbol)
        except Exception as e:
            print(f"❌ 获取价格失败 {symbol}: {e}")
            return {}
    
    
    def place_order(self, symbol: str, side: str, amount: float, price: float = None) -> Optional[Dict]:
        """下订单"""
        try:
            if self.exchange.options.get('createMarketOrder'):
                return self.exchange.create_market_order(symbol, side, amount)
            else:
                return self.exchange.create_limit_order(symbol, side, amount, price)
        except Exception as e:
            print(f"❌ 下单失败: {e}")
            return None
    
    def cancel_order(self, order_id: str) -> bool:
        """取消订单"""
        try:
            return self.exchange.cancel_order(order_id)
        except Exception as e:
            print(f"❌ 取消订单失败: {order_id}: {e}")
            return False
    
    def get_order(self, order_id: str) -> Optional[Dict]:
        """查询订单"""
        try:
            return self.exchange.fetch_order(order_id)
        except Exception as e:
            print(f"❌ 查询订单失败: {order_id}: {e}")
            return None
    
    def get_open_orders(self, symbol: str = None) -> List[Dict]:
        """获取挂单"""
        try:
            return self.exchange.fetch_open_orders(symbol)
        except Exception as e:
            print(f"❌ 获取挂单失败: {e}")
            return []
    
    def get_my_trades(self, symbol: str, limit: int = 100) -> List[Dict]:
        """获取历史交易"""
        try:
            return self.exchange.fetch_my_trades(symbol, limit=limit)
        except Exception as e:
            print(f"❌ 获取历史交易失败 {symbol}: {e}")
            return []


class RiskController:
    """风险控制器"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.max_position_size = config["max_position_size"]
        self.stop_loss = config["stop_loss"]
        self.take_profit = config["take_profit"]
        self.max_drawdown = config["max_drawdown"]
        self.entry_values = {}  # 记录入场价值
        self.highest_value = {}  # 最高价值（用于回撤计算）
    
    def check_position_size(self, available_balance: float, position_value: float) -> Tuple[bool, str]:
        """检查仓位大小"""
        max_allowed = available_balance * self.max_position_size
        if position_value > max_allowed:
            return False, f"仓位过大，最大允许 {max_allowed:.2f}"
        return True, "仓位正常"
    
    def check_stop_loss(self, symbol: str, current_price: float, entry_price: float) -> Tuple[bool, str]:
        """检查止损"""
        if entry_price == 0:
            return False, ""
        
        pnl = (current_price - entry_price) / entry_price
        
        if pnl <= self.stop_loss:
            return True, f"⚠️  {symbol} 触发止损: {pnl:.2%}"
        return False, ""
    
    def check_take_profit(self, symbol: str, current_price: float, entry_price: float) -> Tuple[bool, str]:
        """检查止盈"""
        if entry_price == 0:
            return False, ""
        
        pnc = (current_price - entry_price) / entry_price
        
        if pnc >= self.take_profit:
            return True, f"🎯 {symbol} 触发止盈: {pnc:.2%}"
        return False, ""
    
    def check_max_drawdown(self, symbol: str, current_value: float) -> Tuple[bool, str]:
        """检查最大回撤"""
        if symbol not in self.entry_values:
            self.entry_values[symbol] = current_value
            self.highest_value[symbol] = current_value
            return False, ""
        
        if current_value > self.highest_value[symbol]:
            self.highest_value[symbol] = current_value
        
        if symbol in self.highest_value:
            drawdown = (current_value - self.highest_value[symbol]) / self.highest_value[symbol]
            
            if drawdown <= self.max_drawdown:
                return True, f"⚠️  {symbol} 触发最大回撤: {drawdown:.2%}"
            return False, ""
        return False, ""
    
    def record_entry(self, symbol: str, value: float):
        """记录入场价值"""
        self.entry_values[symbol] = value
        self.highest_value[symbol] = value


class TradingBot:
    """交易机器人主类"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.connector = None
        self.risk_controller = RiskController(config)
        self.positions = {}
        self.trades = []
        self.running = False
    
    def connect(self):
        """连接交易所"""
        if not self.config['api_key'] or not self.config['api_secret']:
            print("❌ 未配置 API 密钥")
            return False
        
        try:
            self.connector = RealExchangeConnector(
                self.config['exchange'],
                self.config['api_key'],
                self.config['api_secret']
            )
            return True
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            return False
    
    def start(self):
        """启动机器人"""
        if not self.connect():
            return False
        
        self.running = True
        print(f"\n🤖 交易机器人启动中...")
        print(f"   交易所: {self.config['exchange']}")
        print(f"   测试模式: {'开启' if self.config['test_mode'] else '关闭'}")
        print(f"   模拟模式: {'开启' if self.config['dry_run'] else '关闭'}")
        print(f"   最大仓位: {self.config['max_position_size']*100:.1f}%")
        print(f"   止损: {self.config['stop_loss']*100:.1f}%")
        print(f"   止盈: {self.config['take_profit']*100:.1f}%")
        print()
        
        return True
    
    def stop(self):
        """停止机器人"""
        self.running = False
        print("🛑 交易机器人已停止")
    
    def run(self):
        """主运行循环"""
        if not self.running:
            return
        
        print("🔄 开始交易循环...")
        
        while self.running:
            try:
                # 获取余额
                balance = self.connector.get_balance()
                available = balance.get('USDT', {}).get('free', 0)
                
                if available < 10:
                    print("⚠️  可用余额不足 ($10)，跳过本轮")
                    time.sleep(60)
                    continue
                
                # 监控持仓
                self.monitor_positions()
                
                # 等待
                time.sleep(self.config['check_interval'])
                
            except KeyboardInterrupt:
                self.stop()
            except Exception as e:
                print(f"❌ 运行错误: {e}")
                time.sleep(60)
    
    def monitor_positions(self):
        """监控持仓和风险"""
        for symbol, position in self.positions.items():
            try:
                # 获取当前价格
                ticker = self.connector.get_ticker(symbol)
                if not ticker or 'last' not in ticker:
                    continue
                
                current_price = ticker['last']
                entry_price = position['entry_price']
                
                # 检查止损
                should_sl, sl_reason = self.risk_controller.check_stop_loss(symbol, current_price, entry_price)
                if should_sl:
                    print(f"\n{sl_reason}")
                    self.execute_close(symbol, "止损平仓")
                    continue
                
                # 检查止盈
                should_tp, tp_reason = self.risk_controller.check_take_profit(symbol, current_price, entry_price)
                if should_tp:
                    print(f"\n{tp_reason}")
                    self.execute_close(symbol, "止盈平仓")
                    continue
                
                # 检查最大回撤
                position_value = position['amount'] * current_price
                should_dd, dd_reason = self.risk_controller.check_max_drawdown(symbol, position_value)
                if should_dd:
                    print(f"\n{dd_reason}")
                    self.execute_close(symbol, "回撤平仓")
                    continue
                
            except Exception as e:
                print(f"❌ 监控 {symbol} 失败: {e}")
    
    def execute_open(self, symbol: str, side: str, amount: float, reason: str = ""):
        """开仓"""
        ticker = self.connector.get_ticker(symbol)
        if not ticker or 'last' not in ticker:
            print(f"❌ 无法获取 {symbol} 价格")
            return False
        
        current_price = ticker['last']
        order_value = amount * current_price
        
        # 风险检查
        balance = self.connector.get_balance()
        available = balance.get('USDT', {}).get('free', 0)
        
        can_trade, reason = self.risk_controller.check_position_size(available, order_value)
        if not can_trade:
            print(f"❌ {symbol} {reason}")
            return False
        
        # 下单
        print(f"\n📊 {symbol} {reason}")
        print(f"   价格: ${current_price}")
        print(f"   数量: {amount}")
        print(f"   价值: ${order_value:.2f}")
        print(f"   模式: {'测试' if self.config['test_mode'] else '真实'}")
        
        if not self.config['test_mode'] and not self.config['dry_run']:
            order = self.connector.place_order(symbol, side, amount, current_price)
            if order:
                print(f"   ✅ 订单已提交: {order.get('id', 'unknown')}")
                self.risk_controller.record_entry(symbol, order_value)
                self.positions[symbol] = {
                    'entry_price': current_price,
                    'amount': amount,
                    'side': side,
                    'entry_time': datetime.now().isoformat(),
                    'order_id': order.get('id', ''),
                    'test_mode': False
                }
        else:
            print(f"   ✅ 模拟下单成功")
            self.risk_controller.record_entry(symbol, order_value)
            self.positions[symbol] = {
                'entry_price': current_price,
                'amount': amount,
                'side': side,
                'entry_time': datetime.now().isoformat(),
                'test_mode': True
            }
        
        return True
    
    def execute_close(self, symbol: str, reason: str = ""):
        """平仓"""
        if symbol not in self.positions:
            return
        
        position = self.positions[symbol]
        current_ticker = self.connector.get_ticker(symbol)
        if not current_ticker or 'last' not in current_ticker:
            print(f"❌ 无法获取 {symbol} 价格")
            return False
        
        current_price = current_ticker['last']
        entry_price = position['entry_price']
        pnl = (current_price - entry_price) / entry_price
        pnl_usdt = pnl * entry_price * position['amount']
        
        side = 'sell' if position['side'] == 'buy' else 'buy'
        
        print(f"\n📊 {symbol} {reason}")
        print(f"   入场: ${entry_price:.4f}")
        print(f"   出场: ${current_price:.4f}")
        print(f"   收益: {pnl:.2%} (${pnl_usdt:+.2f} USDT)")
        
        if not self.config['test_mode'] and not self.config['dry_run']:
            # 取消挂单
            open_orders = self.connector.get_open_orders(symbol)
            for order in open_orders:
                self.connector.cancel_order(order['id'])
            
            # 反向平仓
            self.connector.place_order(symbol, side, position['amount'], current_price)
        
        # 记录交易
        self.trades.append({
            'symbol': symbol,
            'entry_price': entry_price,
            'exit_price': current_price,
            'pnl': pnl,
            'pnl_usdt': pnl_usdt,
            'amount': position['amount'],
            'side': side,
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        })
        
        # 清除持仓
        del self.positions[symbol]
        self.risk_controller.entry_values.pop(symbol, None)
        self.risk_controller.highest_value.pop(symbol, None)
        
        return True
    
    def get_status(self) -> Dict:
        """获取状态"""
        balance = self.connector.get_balance() if self.connector else {}
        
        total_pnl = sum(t['pnl_usdt'] for t in self.trades)
        
        return {
            "running": self.running,
            "exchange": self.config['exchange'],
            "test_mode": self.config['test_mode'],
            "dry_run": self.config['dry_run'],
            "available_balance": balance.get('USDT', {}).get('free', 0),
            "positions": len(self.positions),
            "trades_count": len(self.trades),
            "total_pnl": total_pnl
        }


def main():
    """主函数"""
    print("=" * 70)
    print("🤖 x402 交易机器人 - 正式版")
    print("=" * 70)
    print()
    print("⚠️  警告：高风险！仅使用能承受损失的资金！")
    print()
    
    # 创建机器人
    bot = TradingBot(CONFIG)
    
    # 连接
    if not bot.connect():
        print("❌ 连接失败，请检查配置")
        return
    
    # 显示状态
    status = bot.get_status()
    print(f"📊 状态:")
    print(f"   交易所: {status['exchange']}")
    print(f"   可用余额: ${status['available_balance']:.2f} USDT")
    print(f"   测试模式: {status['test_mode']}")
    print(f"   模拟下单: {status['dry_run']}")
    print()
    
    # 询问是否启动
    response = input("是否启动交易机器人？(yes/no): ").strip().lower()
    
    if response in ['yes', 'y']:
        bot.start()
        bot.run()
    else:
        print("❌ 已取消")


if __name__ == "__main__":
    main()