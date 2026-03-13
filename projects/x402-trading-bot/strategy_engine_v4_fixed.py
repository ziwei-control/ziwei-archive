#!/usr/bin/env python3
# =============================================================================
# 交易策略引擎 v4.0 - 修复版
# 修复：浮点数精度、异常加仓、重复建仓问题
# =============================================================================

import json
import time
import math
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from decimal import Decimal, ROUND_HALF_UP  # 使用 Decimal 提高精度

# 配置
STRATEGY_DIR = Path("/home/admin/Ziwei/data/strategy")
STRATEGY_DIR.mkdir(parents=True, exist_ok=True)

# 模拟账户配置
SIMULATION_CONFIG = {
    'initial_balance': 10000,  # 💰 10,000 USDC 初始资金
    'currency': 'USDC',
    'enabled': True,
}

# 增强安全参数（v4.0 修复版）
SAFETY_CONFIG = {
    'max_position_per_trade': 0.08,  # 单笔最多 8% 仓位
    'max_total_position': 0.50,      # 总仓位最多 50%
    'stop_loss': -0.05,              # 止损 -5%
    'take_profit': 0.20,             # 止盈 +20%
    'min_add_amount_usd': 1.0,       # 🔒 最小加仓金额 $1（防止异常加仓）
    'min_trade_amount_usd': 10.0,    # 🔒 最小交易金额 $10
    'max_daily_trades': 50,          # 🔒 每日最大交易次数
    'max_risk_per_trade': 0.03,      # 单笔最大风险 3%
}

# 交易历史持久化配置
TRADE_HISTORY_FILE = STRATEGY_DIR / "trade_history.jsonl"
BACKUP_DIR = STRATEGY_DIR / "backup"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)
MAX_BACKUPS = 100


class AdvancedStrategyEngine:
    """高级策略引擎 v4.0（修复版）"""
    
    def __init__(self):
        self.positions = {}
        self.trade_history = []
        self.signal_cache = {}
        self.simulation_balance = Decimal(str(SIMULATION_CONFIG['initial_balance']))
        self.simulation_portfolio = {}
        self.daily_pnl = Decimal('0')
        self.win_rate = 0
        self.total_trades = 0
        self.daily_trade_count = 0
        self.last_trade_date = None
        
        # 🔒 先恢复账户状态（防止重复建仓）
        self.load_account_status()
        
        # 加载交易历史
        self.load_trade_history()
    
    def load_account_status(self):
        """🔒 加载账户状态（恢复持仓和余额，防止重复建仓）"""
        account_file = STRATEGY_DIR / "account_status.json"
        
        if not account_file.exists():
            print("ℹ️ 未找到账户状态文件，使用初始状态")
            return
        
        try:
            with open(account_file) as f:
                account = json.load(f)
            
            # 恢复余额（使用 Decimal 提高精度）
            if 'balance' in account:
                balance = account['balance']
                # 忽略极小的余额（浮点数误差）
                if balance > 0.001:
                    self.simulation_balance = Decimal(str(balance))
                    print(f"✅ 恢复余额：${float(self.simulation_balance):,.2f}")
                else:
                    print(f"⚠️ 忽略极小余额：${balance}（浮点数误差）")
                    self.simulation_balance = Decimal(str(SIMULATION_CONFIG['initial_balance']))
            
            # 恢复持仓
            if 'portfolio' in account and account['portfolio']:
                self.simulation_portfolio = account['portfolio']
                print(f"✅ 恢复持仓：{len(self.simulation_portfolio)} 个币种")
                for coin, holding in self.simulation_portfolio.items():
                    value = Decimal(str(holding['amount'])) * Decimal(str(holding['entry_price']))
                    print(f"   {coin}: {holding['amount']:,.2f} @ ${holding['entry_price']:,.6f} = ${float(value):,.2f}")
            
            # 恢复其他状态
            if 'daily_pnl' in account:
                self.daily_pnl = Decimal(str(account['daily_pnl']))
            if 'win_rate' in account:
                self.win_rate = account['win_rate']
            if 'total_trades' in account:
                self.total_trades = account['total_trades']
            
            print(f"✅ 账户状态恢复完成 | 总交易：{self.total_trades} 笔")
            
        except Exception as e:
            print(f"❌ 加载账户状态失败：{e}")
            print("⚠️ 将使用初始状态（可能导致重复建仓）")
    
    def load_trade_history(self):
        """加载之前的交易历史"""
        loaded_count = 0
        
        # 从独立历史文件加载
        if TRADE_HISTORY_FILE.exists():
            try:
                with open(TRADE_HISTORY_FILE, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            trade = json.loads(line)
                            # 过滤异常交易（金额过小）
                            if trade.get('value', 0) > 0.001:
                                if not any(t.get('time') == trade.get('time') and t.get('symbol') == trade.get('symbol') for t in self.trade_history):
                                    self.trade_history.append(trade)
                                    loaded_count += 1
                print(f"✅ 从独立文件加载交易历史：{loaded_count} 笔")
            except Exception as e:
                print(f"⚠️ 加载独立历史文件失败：{e}")
        
        print(f"📜 总交易历史：{len(self.trade_history)} 笔")
    
    def check_daily_trade_limit(self) -> bool:
        """🔒 检查每日交易限制"""
        today = datetime.now().date()
        
        # 如果是新的一天，重置计数器
        if self.last_trade_date != today:
            self.daily_trade_count = 0
            self.last_trade_date = today
            print(f"📅 新的一天，交易计数器已重置")
        
        # 检查是否超过每日限制
        if self.daily_trade_count >= SAFETY_CONFIG['max_daily_trades']:
            print(f"⚠️ 已达到每日最大交易次数限制：{SAFETY_CONFIG['max_daily_trades']}")
            return False
        
        return True
    
    def execute_simulation_trade(self, signal: Dict):
        """🔒 执行模拟交易（v4.0 修复版 - 防止异常加仓）"""
        if not SIMULATION_CONFIG['enabled']:
            return
        
        # 🔒 检查每日交易限制
        if not self.check_daily_trade_limit():
            return
        
        symbol = signal['symbol']
        position = signal['suggested_position']
        price = Decimal(str(signal['price']))
        timestamp = datetime.now().isoformat()
        
        if 'BUY' in signal['signal']:
            # 检查是否已持仓
            if symbol in self.simulation_portfolio:
                # 已持仓 - 加仓逻辑
                holding = self.simulation_portfolio[symbol]
                
                # 计算加仓金额
                amount_usd = self.simulation_balance * Decimal(str(position))
                
                # 🔒 检查最小加仓金额
                if float(amount_usd) < SAFETY_CONFIG['min_add_amount_usd']:
                    print(f"⏭️ [跳过加仓] {symbol}: 加仓金额 ${float(amount_usd):.2f} < 最小 ${SAFETY_CONFIG['min_add_amount_usd']}")
                    return
                
                # 🔒 检查余额是否足够
                if amount_usd > self.simulation_balance:
                    print(f"⏭️ [跳过加仓] {symbol}: 余额不足 ${float(self.simulation_balance):.2f} < ${float(amount_usd):.2f}")
                    return
                
                tokens = amount_usd / price
                
                # 🔒 检查最小交易量
                if float(tokens) < 0.001:
                    print(f"⏭️ [跳过加仓] {symbol}: 交易量过小 {float(tokens)}")
                    return
                
                # 使用 Decimal 计算平均成本（提高精度）
                old_amount = Decimal(str(holding['amount']))
                old_price = Decimal(str(holding['entry_price']))
                old_cost = old_amount * old_price
                new_cost = amount_usd
                
                total_amount = old_amount + tokens
                avg_price = (old_cost + new_cost) / total_amount if total_amount > 0 else price
                
                # 更新持仓
                holding['amount'] = float(total_amount)
                holding['entry_price'] = float(avg_price)
                holding['entry_time'] = timestamp
                holding['stop_loss'] = float(signal['stop_loss'])
                holding['take_profit'] = float(signal['take_profit'])
                
                self.simulation_balance -= amount_usd
                self.total_trades += 1
                self.daily_trade_count += 1
                
                # 记录加仓历史
                trade_record = {
                    'type': '加仓',
                    'symbol': symbol,
                    'time': timestamp,
                    'price': float(price),
                    'amount': float(tokens),
                    'total_amount': float(total_amount),
                    'avg_price': float(avg_price),
                    'value': float(amount_usd),
                    'pnl': 0
                }
                self.trade_history.append(trade_record)
                
                # 🔒 立即持久化
                self.record_trade_persistent(trade_record)
                
                print(f"📈 [模拟加仓] {symbol}: {float(tokens):.4f} @ ${float(price):.6f} = ${float(amount_usd):.2f} (总仓：{float(total_amount):.4f}, 均价：${float(avg_price):.6f})")
            
            else:
                # 新建仓
                amount_usd = self.simulation_balance * Decimal(str(position))
                
                # 🔒 检查最小建仓金额
                if float(amount_usd) < SAFETY_CONFIG['min_trade_amount_usd']:
                    print(f"⏭️ [跳过建仓] {symbol}: 建仓金额 ${float(amount_usd):.2f} < 最小 ${SAFETY_CONFIG['min_trade_amount_usd']}")
                    return
                
                # 🔒 检查余额是否足够
                if amount_usd > self.simulation_balance:
                    print(f"⏭️ [跳过建仓] {symbol}: 余额不足")
                    return
                
                tokens = amount_usd / price
                
                self.simulation_portfolio[symbol] = {
                    'amount': float(tokens),
                    'entry_price': float(price),
                    'entry_time': timestamp,
                    'stop_loss': float(signal['stop_loss']),
                    'take_profit': float(signal['take_profit'])
                }
                
                self.simulation_balance -= amount_usd
                self.total_trades += 1
                self.daily_trade_count += 1
                
                # 记录建仓历史
                trade_record = {
                    'type': '建仓',
                    'symbol': symbol,
                    'time': timestamp,
                    'price': float(price),
                    'amount': float(tokens),
                    'total_amount': float(tokens),
                    'avg_price': float(price),
                    'value': float(amount_usd),
                    'pnl': 0
                }
                self.trade_history.append(trade_record)
                
                # 🔒 立即持久化
                self.record_trade_persistent(trade_record)
                
                print(f"💰 [模拟建仓] {symbol}: {float(tokens):.4f} @ ${float(price):.6f} = ${float(amount_usd):.2f}")
        
        elif 'SELL' in signal['signal'] and symbol in self.simulation_portfolio:
            # 卖出逻辑
            holding = self.simulation_portfolio[symbol]
            tokens = Decimal(str(holding['amount']))
            revenue = tokens * price
            pnl = revenue - (tokens * Decimal(str(holding['entry_price'])))
            
            # 记录清仓历史
            trade_record = {
                'type': '清仓',
                'symbol': symbol,
                'time': timestamp,
                'price': float(price),
                'amount': float(tokens),
                'total_amount': 0,
                'avg_price': float(holding['entry_price']),
                'value': float(revenue),
                'pnl': float(pnl)
            }
            self.trade_history.append(trade_record)
            
            # 🔒 立即持久化
            self.record_trade_persistent(trade_record)
            
            self.simulation_balance += revenue
            self.daily_pnl += pnl
            del self.simulation_portfolio[symbol]
            self.total_trades += 1
            self.daily_trade_count += 1
            
            if pnl > 0:
                self.win_rate = (self.win_rate * (self.total_trades - 1) + 1) / self.total_trades
            else:
                self.win_rate = (self.win_rate * (self.total_trades - 1)) / self.total_trades
            
            pnl_text = "✅ 盈利" if pnl > 0 else "❌ 亏损"
            print(f"💰 [模拟清仓] {symbol}: {float(tokens):.4f} @ ${float(price):.6f} = ${float(revenue):.2f} ({pnl_text}: ${float(pnl):+.2f})")
    
    def record_trade_persistent(self, trade_record: Dict):
        """🔒 持久化记录交易（独立文件 + 备份）"""
        try:
            # 1. 追加到独立历史文件
            with open(TRADE_HISTORY_FILE, 'a', encoding='utf-8') as f:
                f.write(json.dumps(trade_record, ensure_ascii=False) + '\n')
            
            # 2. 创建备份
            self._create_backup()
            
            print(f"💾 交易已持久化：{trade_record['type']} {trade_record['symbol']}")
        except Exception as e:
            print(f"❌ 持久化失败：{e}")
    
    def _create_backup(self):
        """创建账户状态备份"""
        try:
            account_file = STRATEGY_DIR / "account_status.json"
            if not account_file.exists():
                return
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = BACKUP_DIR / f"account_status_{timestamp}.json"
            latest_backup = BACKUP_DIR / "account_status_latest.json"
            
            import shutil
            shutil.copy2(account_file, backup_file)
            shutil.copy2(account_file, latest_backup)
            
            # 清理旧备份
            backups = sorted(BACKUP_DIR.glob("account_status_*.json"))
            if len(backups) > MAX_BACKUPS:
                for old_backup in backups[:-MAX_BACKUPS]:
                    old_backup.unlink()
            
            print(f"📦 备份已创建：{backup_file.name}")
        except Exception as e:
            print(f"⚠️ 备份失败：{e}")
    
    def save_account_status(self):
        """保存账户状态"""
        account_file = STRATEGY_DIR / "account_status.json"
        
        # 转换 Decimal 为 float 用于 JSON 序列化
        account_status = {
            'balance': float(self.simulation_balance),
            'portfolio': self.simulation_portfolio,
            'daily_pnl': float(self.daily_pnl),
            'win_rate': self.win_rate,
            'total_trades': self.total_trades,
            'daily_trade_count': self.daily_trade_count,
            'last_trade_date': str(self.last_trade_date) if self.last_trade_date else None,
            'trade_history': self.trade_history[-100:],  # 保留最近 100 笔
            'timestamp': datetime.now().isoformat()
        }
        
        with open(account_file, 'w', encoding='utf-8') as f:
            json.dump(account_status, f, indent=2, ensure_ascii=False)
        
        print(f"💾 账户状态已保存")
    
    def print_portfolio(self):
        """打印投资组合"""
        print("\n" + "=" * 70)
        print("💼 模拟投资组合")
        print("=" * 70)
        print(f"可用余额：${float(self.simulation_balance):,.2f} USDC")
        print(f"持仓数量：{len(self.simulation_portfolio)}")
        print(f"今日盈亏：${float(self.daily_pnl):+.2f}")
        print(f"胜率：{self.win_rate*100:.1f}%")
        print(f"总交易数：{self.total_trades}")
        print(f"今日交易：{self.daily_trade_count}/{SAFETY_CONFIG['max_daily_trades']}")
        
        if self.simulation_portfolio:
            print("\n📦 当前持仓:")
            for symbol, holding in self.simulation_portfolio.items():
                current_value = Decimal(str(holding['amount'])) * Decimal(str(holding['entry_price']))
                print(f"  {symbol}: {holding['amount']:.4f} @ ${holding['entry_price']:.6f} = ${float(current_value):,.2f}")
        
        total_value = self.simulation_balance + sum(
            Decimal(str(h['amount'])) * Decimal(str(h['entry_price'])) for h in self.simulation_portfolio.values()
        )
        print(f"\n总资产：${float(total_value):,.2f} USDC")
        print(f"初始资金：${SIMULATION_CONFIG['initial_balance']:,.2f} USDC")
        print(f"总收益率：{((float(total_value) / SIMULATION_CONFIG['initial_balance']) - 1) * 100:+.2f}%")
        print("=" * 70)


# 导入原有的其他函数（generate_signal, analyze_all 等）
# 为简洁起见，这里省略，实际使用时需要从原文件复制
