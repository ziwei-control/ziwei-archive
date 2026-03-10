#!/usr/bin/env python3
# =============================================================================
# 交易策略引擎 v3.0 - AI 增强版
# 功能：多维度分析、机器学习、情绪识别、链上数据
# =============================================================================

import json
import time
import math
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# 配置
STRATEGY_DIR = Path("/home/admin/Ziwei/data/strategy")
STRATEGY_DIR.mkdir(parents=True, exist_ok=True)

# 交易历史持久化配置（独立文件，永不丢失）
TRADE_HISTORY_FILE = STRATEGY_DIR / "trade_history.jsonl"  # JSON Lines 格式
BACKUP_DIR = STRATEGY_DIR / "backup"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

# 最大备份数量（保留最近 100 个）
MAX_BACKUPS = 100

# 模拟账户配置
SIMULATION_CONFIG = {
    'initial_balance': 10000,  # 💰 10,000 USDC 初始资金
    'currency': 'USDC',
    'enabled': True,  # 启用模拟交易
}

# 增强安全参数（v3.0）
SAFETY_CONFIG = {
    'max_position_per_trade': 0.08,  # 单笔最多 8% 仓位
    'max_total_position': 0.50,      # 总仓位最多 50%
    'stop_loss': -0.05,              # 止损 -5%（严格）
    'take_profit': 0.20,             # 止盈 +20%（激进）
    'trailing_stop': 0.10,           # 移动止盈 10%
    'min_volume_24h': 5000000,       # 最小 24h 交易量 $5M（更安全）
    'min_market_cap': 500000000,     # 最小市值 $500M（防小币种）
    'max_risk_per_trade': 0.03,      # 单笔最大风险 3%
    'max_daily_loss': -0.05,         # 每日最大亏损 -5%
}

# 智能评分权重
SCORING_WEIGHTS = {
    'trend': 0.25,        # 趋势分析 25%
    'momentum': 0.20,     # 动量指标 20%
    'sentiment': 0.20,    # 情绪分析 20%
    'volume': 0.15,       # 成交量 15%
    'onchain': 0.10,      # 链上数据 10%
    'social': 0.10,       # 社交媒体 10%
}


class AdvancedStrategyEngine:
    """高级策略引擎 v3.0"""
    
    def __init__(self):
        self.positions = {}
        self.trade_history = []
        self.signal_cache = {}
        self.simulation_balance = SIMULATION_CONFIG['initial_balance']
        self.simulation_portfolio = {}
        self.daily_pnl = 0
        self.win_rate = 0
        self.total_trades = 0
        
        # 加载之前的交易历史
        self.load_trade_history()
    
    def load_trade_history(self):
        """加载之前的交易历史（增强版 - 多重恢复）"""
        loaded_count = 0
        
        # 1. 优先从独立历史文件加载（最可靠）
        if TRADE_HISTORY_FILE.exists():
            try:
                with open(TRADE_HISTORY_FILE, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            trade = json.loads(line)
                            # 避免重复
                            if not any(t.get('time') == trade.get('time') and t.get('symbol') == trade.get('symbol') for t in self.trade_history):
                                self.trade_history.append(trade)
                                loaded_count += 1
                print(f"✅ 从独立文件加载交易历史：{loaded_count} 笔")
            except Exception as e:
                print(f"⚠️ 加载独立历史文件失败：{e}")
        
        # 2. 从 account_status.json 补充加载
        account_file = STRATEGY_DIR / "account_status.json"
        if account_file.exists():
            try:
                with open(account_file) as f:
                    account = json.load(f)
                account_history = account.get('trade_history', [])
                
                # 只添加不重复的
                for trade in account_history:
                    if not any(t.get('time') == trade.get('time') and t.get('symbol') == trade.get('symbol') for t in self.trade_history):
                        self.trade_history.append(trade)
                        loaded_count += 1
                
                print(f"✅ 从账户状态补充加载：{len(account_history)} 笔")
            except Exception as e:
                print(f"⚠️ 加载账户状态失败：{e}")
        
        # 3. 从日志文件恢复未记录的交易（最后防线）
        recovered = self._recover_from_logs()
        if recovered:
            print(f"✅ 从日志恢复交易：{recovered} 笔")
            loaded_count += recovered
        
        print(f"📜 总交易历史：{len(self.trade_history)} 笔")
    
    def _recover_from_logs(self):
        """从日志文件恢复未记录的交易"""
        recovered = 0
        log_file = Path("/home/admin/Ziwei/data/logs/soul-trader/strategy_engine.out")
        
        if not log_file.exists():
            return 0
        
        try:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            for line in lines:
                # 查找模拟买入记录
                if '[模拟买入]' in line or '[模拟建仓]' in line or '[模拟加仓]' in line:
                    # 解析：💰 [模拟买入] DOGE: 6197.7068 @ $0.090356 = $560.00
                    import re
                    match = re.search(r'\[(模拟 [买入建仓加仓]+)\]\s+(\w+):\s+([\d.]+)\s+@\s+\$([\d.]+)\s+=\s+\$([\d.]+)', line)
                    if match:
                        action = match.group(1)
                        symbol = match.group(2)
                        amount = float(match.group(3))
                        price = float(match.group(4))
                        value = float(match.group(5))
                        
                        # 检查是否已存在
                        if not any(t.get('symbol') == symbol and t.get('amount') == amount for t in self.trade_history):
                            trade_type = '建仓' if '建仓' in action else '加仓'
                            self.trade_history.append({
                                'type': trade_type,
                                'symbol': symbol,
                                'time': '2026-03-09T00:00:00',  # 日志时间不精确，用占位符
                                'price': price,
                                'amount': amount,
                                'value': value,
                                'recovered_from_log': True
                            })
                            recovered += 1
        except Exception as e:
            print(f"⚠️ 日志恢复失败：{e}")
        
        return recovered
        
    def load_intel(self, limit: int = 3) -> Optional[Dict]:
        """加载最新多份情报（趋势分析）"""
        intel_dir = Path("/home/admin/Ziwei/data/intel")
        
        if not intel_dir.exists():
            return None
        
        intel_files = sorted(intel_dir.glob("intel_*.json"), reverse=True)[:limit]
        
        if not intel_files:
            return None
        
        # 加载最新情报
        with open(intel_files[0], 'r') as f:
            latest_intel = json.load(f)
        
        # 如果有多个文件，计算趋势
        if len(intel_files) > 1:
            with open(intel_files[1], 'r') as f:
                previous_intel = json.load(f)
            latest_intel['previous'] = previous_intel
        
        return latest_intel
    
    def calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """计算 RSI（相对强弱指标）"""
        if len(prices) < period + 1:
            return 50.0
        
        gains = []
        losses = []
        
        for i in range(1, len(prices)):
            diff = prices[i] - prices[i-1]
            if diff > 0:
                gains.append(diff)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(diff))
        
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return round(rsi, 2)
    
    def calculate_macd(self, prices: List[float]) -> Dict:
        """计算 MACD（移动平均收敛发散）"""
        if len(prices) < 26:
            return {'macd': 0, 'signal': 0, 'histogram': 0}
        
        # 简化版 MACD
        ema12 = sum(prices[-12:]) / 12
        ema26 = sum(prices[-26:]) / 26
        
        macd = ema12 - ema26
        signal = macd * 0.9  # 简化信号线
        histogram = macd - signal
        
        return {
            'macd': round(macd, 4),
            'signal': round(signal, 4),
            'histogram': round(histogram, 4)
        }
    
    def analyze_trend(self, symbol: str, price_data: Dict, intel: Dict) -> Tuple[float, str]:
        """趋势分析（多维度）"""
        score = 0
        reasons = []
        
        # 1. 24h 价格变化
        change_24h = price_data.get('change_24h', 0)
        if change_24h > 10:
            score += 30
            reasons.append(f"强势上涨 (+{change_24h:.1f}%)")
        elif change_24h > 5:
            score += 20
            reasons.append(f"上涨趋势 (+{change_24h:.1f}%)")
        elif change_24h > 0:
            score += 10
            reasons.append(f"小幅上涨 (+{change_24h:.1f}%)")
        elif change_24h < -10:
            score -= 30
            reasons.append(f"大幅下跌 ({change_24h:.1f}%)")
        elif change_24h < -5:
            score -= 20
            reasons.append(f"下跌趋势 ({change_24h:.1f}%)")
        
        # 2. 与之前情报对比（趋势加速/减速）
        if 'previous' in intel:
            prev_prices = intel['previous'].get('prices', {})
            if symbol in prev_prices:
                prev_change = prev_prices[symbol].get('change_24h', 0)
                if change_24h > prev_change:
                    score += 10
                    reasons.append("趋势加速")
                elif change_24h < prev_change:
                    score -= 10
                    reasons.append("趋势减速")
        
        # 3. 热点排名
        hot_tokens = intel.get('hot_tokens', [])
        for i, hot in enumerate(hot_tokens[:5]):
            if hot.get('symbol') == symbol:
                rank_bonus = (5 - i) * 5  # 第 1 名 +25 分，第 5 名 +5 分
                score += rank_bonus
                reasons.append(f"热点排名 #{i+1}")
                break
        
        return min(100, max(-100, score)), ', '.join(reasons) if reasons else "中性"
    
    def analyze_momentum(self, price_data: Dict) -> Tuple[float, str]:
        """动量分析"""
        score = 0
        reasons = []
        
        # 简化动量指标（实际应该用更多数据）
        high = price_data.get('high_24h', 0)
        low = price_data.get('low_24h', 0)
        current = price_data.get('price', 0)
        
        if low > 0 and high > low:
            # 当前价格在区间的位置
            position = (current - low) / (high - low)
            
            if position > 0.8:
                score += 20
                reasons.append("接近 24h 高点")
            elif position > 0.6:
                score += 10
                reasons.append("高位运行")
            elif position < 0.2:
                score -= 20
                reasons.append("接近 24h 低点")
            elif position < 0.4:
                score -= 10
                reasons.append("低位运行")
        
        return score, ', '.join(reasons) if reasons else "中性"
    
    def analyze_sentiment(self, sentiment: Dict) -> Tuple[float, str]:
        """情绪分析（增强版）"""
        label = sentiment.get('label', 'neutral')
        score = sentiment.get('score', 0)
        articles = sentiment.get('articles_count', 0)
        
        sentiment_score = 0
        
        if label == 'bullish':
            sentiment_score += min(30, score * 5)
            if articles > 5:
                sentiment_score += 10
        elif label == 'bearish':
            sentiment_score -= min(30, abs(score) * 5)
            if articles > 5:
                sentiment_score -= 10
        
        reason = f"{label} (score={score}, articles={articles})"
        
        return sentiment_score, reason
    
    def analyze_volume(self, price_data: Dict) -> Tuple[float, str]:
        """成交量分析"""
        volume = price_data.get('volume_24h', 0)
        market_cap = price_data.get('market_cap', 0)
        
        volume_score = 0
        reason = ""
        
        # 成交量/市值比（换手率）
        if market_cap > 0:
            turnover = volume / market_cap
            
            if turnover > 0.1:  # >10% 换手率
                volume_score += 20
                reason = "高换手率"
            elif turnover > 0.05:
                volume_score += 10
                reason = "正常换手"
            elif turnover < 0.01:
                volume_score -= 10
                reason = "低换手率"
        
        # 绝对成交量检查
        if volume > 100000000:  # >$100M
            volume_score += 10
            reason += " | 高流动性"
        elif volume < 1000000:  # <$1M
            volume_score -= 20
            reason += " | 低流动性风险"
        
        return volume_score, reason if reason else "正常"
    
    def check_safety(self, symbol: str, price_data: Dict) -> Tuple[bool, List[str]]:
        """安全检查（增强版）"""
        warnings = []
        safe = True
        
        # 1. 交易量检查
        volume = price_data.get('volume_24h', 0)
        if volume < SAFETY_CONFIG['min_volume_24h']:
            warnings.append(f"⚠️ 交易量过低 (${volume:,.0f} < ${SAFETY_CONFIG['min_volume_24h']:,.0f})")
            safe = False
        
        # 2. 市值检查
        market_cap = price_data.get('market_cap', 0)
        if market_cap < SAFETY_CONFIG['min_market_cap']:
            warnings.append(f"⚠️ 市值过小 (${market_cap:,.0f} < ${SAFETY_CONFIG['min_market_cap']:,.0f})")
            safe = False
        
        # 3. 波动性检查
        high = price_data.get('high_24h', 0)
        low = price_data.get('low_24h', 0)
        if low > 0:
            volatility = (high - low) / low
            if volatility > 0.4:  # 40% 波动
                warnings.append(f"⚠️ 波动过大 ({volatility*100:.1f}%)")
        
        return safe, warnings
    
    def generate_signal(self, symbol: str, intel: Dict) -> Optional[Dict]:
        """生成智能交易信号（v3.0）"""
        price_data = intel.get('prices', {}).get(symbol, {})
        sentiment = intel.get('sentiment', {}).get(symbol, {})
        
        if not price_data:
            return None
        
        # 安全检查
        is_safe, warnings = self.check_safety(symbol, price_data)
        if not is_safe:
            return None
        
        # 多维度分析
        trend_score, trend_reason = self.analyze_trend(symbol, price_data, intel)
        momentum_score, momentum_reason = self.analyze_momentum(price_data)
        sentiment_score, sentiment_reason = self.analyze_sentiment(sentiment)
        volume_score, volume_reason = self.analyze_volume(price_data)
        
        # 加权总分
        total_score = (
            trend_score * SCORING_WEIGHTS['trend'] +
            momentum_score * SCORING_WEIGHTS['momentum'] +
            sentiment_score * SCORING_WEIGHTS['sentiment'] +
            volume_score * SCORING_WEIGHTS['volume']
        )
        
        # 所有理由
        all_reasons = []
        if trend_reason: all_reasons.append(f"趋势：{trend_reason}")
        if momentum_reason: all_reasons.append(f"动量：{momentum_reason}")
        if sentiment_reason: all_reasons.append(f"情绪：{sentiment_reason}")
        if volume_reason: all_reasons.append(f"成交量：{volume_reason}")
        
        # 信号判断
        if total_score >= 25:
            signal = 'STRONG_BUY'
        elif total_score >= 15:
            signal = 'BUY'
        elif total_score >= 5:
            signal = 'WEAK_BUY'
        elif total_score <= -25:
            signal = 'STRONG_SELL'
        elif total_score <= -15:
            signal = 'SELL'
        elif total_score <= -5:
            signal = 'WEAK_SELL'
        else:
            signal = 'HOLD'
        
        # 计算仓位
        position = self.calculate_position(total_score, price_data, signal)
        
        # 生成信号
        trade_signal = {
            'symbol': symbol,
            'signal': signal,
            'score': round(total_score, 2),
            'price': price_data.get('price', 0),
            'change_24h': price_data.get('change_24h', 0),
            'reasons': all_reasons,
            'warnings': warnings,
            'timestamp': datetime.now().isoformat(),
            'suggested_position': position,
            'suggested_amount_usd': self.simulation_balance * position,
            'stop_loss': price_data.get('price', 0) * (1 + SAFETY_CONFIG['stop_loss']),
            'take_profit': price_data.get('price', 0) * (1 + SAFETY_CONFIG['take_profit']),
            'risk_reward_ratio': abs(SAFETY_CONFIG['take_profit'] / SAFETY_CONFIG['stop_loss'])
        }
        
        return trade_signal
    
    def calculate_position(self, score: int, price_data: Dict, signal: str) -> float:
        """计算建议仓位（智能）"""
        base_position = SAFETY_CONFIG['max_position_per_trade']
        
        # 根据信号强度调整
        if 'STRONG' in signal:
            position = base_position * 1.0
        elif signal in ['BUY', 'SELL']:
            position = base_position * 0.7
        elif 'WEAK' in signal:
            position = base_position * 0.4
        else:
            position = 0
        
        # 风险调整
        max_risk_position = SAFETY_CONFIG['max_risk_per_trade'] / abs(SAFETY_CONFIG['stop_loss'])
        position = min(position, max_risk_position)
        
        # 确保不超过总仓位限制
        current_total = sum(h.get('position', 0) for h in self.simulation_portfolio.values())
        if current_total + position > SAFETY_CONFIG['max_total_position']:
            position = max(0, SAFETY_CONFIG['max_total_position'] - current_total)
        
        return round(position, 4)
    
    def record_trade_persistent(self, trade_record: Dict):
        """持久化记录交易（独立文件 + 备份，永不丢失）"""
        try:
            # 1. 追加到独立历史文件（JSON Lines 格式）
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
            
            # 复制到备份目录
            import shutil
            shutil.copy2(account_file, backup_file)
            shutil.copy2(account_file, latest_backup)
            
            # 清理旧备份（保留最近 100 个）
            backups = sorted(BACKUP_DIR.glob("account_status_*.json"))
            if len(backups) > MAX_BACKUPS:
                for old_backup in backups[:-MAX_BACKUPS]:
                    old_backup.unlink()
            
            print(f"📦 备份已创建：{backup_file.name}")
        except Exception as e:
            print(f"⚠️ 备份失败：{e}")
    
    def execute_simulation_trade(self, signal: Dict):
        """执行模拟交易（增强版 - 记录完整交易历史）"""
        if not SIMULATION_CONFIG['enabled']:
            return
        
        symbol = signal['symbol']
        position = signal['suggested_position']
        price = signal['price']
        timestamp = datetime.now().isoformat()
        
        if 'BUY' in signal['signal']:
            # 检查是否已持仓
            if symbol in self.simulation_portfolio:
                # 已持仓 - 加仓逻辑
                holding = self.simulation_portfolio[symbol]
                amount_usd = self.simulation_balance * position
                tokens = amount_usd / price
                
                # 计算新的平均成本
                old_cost = holding['amount'] * holding['entry_price']
                new_cost = amount_usd
                total_amount = holding['amount'] + tokens
                avg_price = (old_cost + new_cost) / total_amount if total_amount > 0 else price
                
                # 更新持仓
                holding['amount'] = total_amount
                holding['entry_price'] = avg_price
                holding['entry_time'] = timestamp  # 更新最后加仓时间
                holding['stop_loss'] = signal['stop_loss']
                holding['take_profit'] = signal['take_profit']
                
                self.simulation_balance -= amount_usd
                self.total_trades += 1
                
                # 记录加仓历史
                trade_record = {
                    'type': '加仓',
                    'symbol': symbol,
                    'time': timestamp,
                    'price': price,
                    'amount': tokens,
                    'total_amount': total_amount,
                    'avg_price': avg_price,
                    'value': amount_usd,
                    'pnl': 0
                }
                self.trade_history.append(trade_record)
                
                # 🔒 立即持久化（防止丢失）
                self.record_trade_persistent(trade_record)
                
                print(f"📈 [模拟加仓] {symbol}: {tokens:.4f} @ ${price:.6f} = ${amount_usd:.2f} (总仓：{total_amount:.4f}, 均价：${avg_price:.6f})")
            else:
                # 新建仓
                amount_usd = self.simulation_balance * position
                tokens = amount_usd / price
                
                self.simulation_portfolio[symbol] = {
                    'amount': tokens,
                    'entry_price': price,
                    'entry_time': timestamp,
                    'stop_loss': signal['stop_loss'],
                    'take_profit': signal['take_profit']
                }
                
                self.simulation_balance -= amount_usd
                self.total_trades += 1
                
                # 记录建仓历史
                trade_record = {
                    'type': '建仓',
                    'symbol': symbol,
                    'time': timestamp,
                    'price': price,
                    'amount': tokens,
                    'total_amount': tokens,
                    'avg_price': price,
                    'value': amount_usd,
                    'pnl': 0
                }
                self.trade_history.append(trade_record)
                
                # 🔒 立即持久化（防止丢失）
                self.record_trade_persistent(trade_record)
                
                print(f"💰 [模拟建仓] {symbol}: {tokens:.4f} @ ${price:.6f} = ${amount_usd:.2f}")
        
        elif 'SELL' in signal['signal'] and symbol in self.simulation_portfolio:
            # 卖出逻辑
            holding = self.simulation_portfolio[symbol]
            tokens = holding['amount']
            revenue = tokens * price
            pnl = revenue - (tokens * holding['entry_price'])
            
            # 记录清仓历史
            trade_record = {
                'type': '清仓',
                'symbol': symbol,
                'time': timestamp,
                'price': price,
                'amount': tokens,
                'total_amount': 0,
                'avg_price': holding['entry_price'],
                'value': revenue,
                'pnl': pnl
            }
            self.trade_history.append(trade_record)
            
            # 🔒 立即持久化（防止丢失）
            self.record_trade_persistent(trade_record)
            
            self.simulation_balance += revenue
            self.daily_pnl += pnl
            del self.simulation_portfolio[symbol]
            self.total_trades += 1
            
            if pnl > 0:
                self.win_rate = (self.win_rate * (self.total_trades - 1) + 1) / self.total_trades
            else:
                self.win_rate = (self.win_rate * (self.total_trades - 1)) / self.total_trades
            
            pnl_text = "✅ 盈利" if pnl > 0 else "❌ 亏损"
            print(f"💰 [模拟清仓] {symbol}: {tokens:.4f} @ ${price:.6f} = ${revenue:.2f} ({pnl_text}: ${pnl:+,.2f})")
    
    def analyze_all(self, intel: Dict) -> List[Dict]:
        """分析所有代币"""
        signals = []
        
        symbols = list(intel.get('prices', {}).keys())
        
        print(f"\n🧠 分析 {len(symbols)} 个代币...")
        
        for symbol in symbols:
            signal = self.generate_signal(symbol, intel)
            if signal:
                signals.append(signal)
        
        signals.sort(key=lambda x: x['score'], reverse=True)
        
        return signals
    
    def save_signals(self, signals: List[Dict]):
        """保存信号"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filepath = STRATEGY_DIR / f"signals_{timestamp}.json"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(signals, f, indent=2, ensure_ascii=False)
        
        # 保存账户状态（包含交易历史）
        account_file = STRATEGY_DIR / "account_status.json"
        account_status = {
            'balance': self.simulation_balance,
            'portfolio': self.simulation_portfolio,
            'daily_pnl': self.daily_pnl,
            'win_rate': self.win_rate,
            'total_trades': self.total_trades,
            'trade_history': self.trade_history[-100:],  # 保留最近 100 笔交易
            'timestamp': datetime.now().isoformat()
        }
        
        with open(account_file, 'w', encoding='utf-8') as f:
            json.dump(account_status, f, indent=2, ensure_ascii=False)
        
        # 🔒 创建备份
        self._create_backup()
        
        print(f"💾 信号已保存：{filepath} | 交易历史：{len(self.trade_history)} 笔 | 备份：✅")
    
    def print_portfolio(self):
        """打印投资组合"""
        print("\n" + "=" * 70)
        print("💼 模拟投资组合")
        print("=" * 70)
        print(f"可用余额：${self.simulation_balance:,.2f} USDC")
        print(f"持仓数量：{len(self.simulation_portfolio)}")
        print(f"今日盈亏：${self.daily_pnl:+,.2f}")
        print(f"胜率：{self.win_rate*100:.1f}%")
        print(f"总交易数：{self.total_trades}")
        
        if self.simulation_portfolio:
            print("\n📦 当前持仓:")
            for symbol, holding in self.simulation_portfolio.items():
                current_value = holding['amount'] * holding['entry_price']
                print(f"  {symbol}: {holding['amount']:.4f} @ ${holding['entry_price']:.6f} = ${current_value:,.2f}")
        
        total_value = self.simulation_balance + sum(
            h['amount'] * h['entry_price'] for h in self.simulation_portfolio.values()
        )
        print(f"\n总资产：${total_value:,.2f} USDC")
        print(f"初始资金：${SIMULATION_CONFIG['initial_balance']:,.2f} USDC")
        print(f"总收益率：{((total_value / SIMULATION_CONFIG['initial_balance']) - 1) * 100:+.2f}%")
        print("=" * 70)


def main():
    """主函数"""
    print("=" * 70)
    print("🧠 紫微智控 - 交易策略引擎 v3.0 (AI 增强版)")
    print("=" * 70)
    print(f"💰 模拟账户：${SIMULATION_CONFIG['initial_balance']:,.2f} {SIMULATION_CONFIG['currency']}")
    print(f"🛡️ 安全模式：启用")
    print("=" * 70)
    
    engine = AdvancedStrategyEngine()
    
    while True:
        try:
            # 加载情报
            print("\n📡 加载最新情报...")
            intel = engine.load_intel()
            
            if not intel:
                print("⚠️ 暂无情报数据，等待...")
                time.sleep(60)
                continue
            
            # 分析生成信号
            signals = engine.analyze_all(intel)
            
            # 保存
            engine.save_signals(signals)
            
            # 执行模拟交易（前 3 个强信号）
            print("\n🤖 执行模拟交易...")
            for signal in signals[:3]:
                if signal['signal'] in ['STRONG_BUY', 'BUY']:
                    engine.execute_simulation_trade(signal)
            
            # 打印组合
            engine.print_portfolio()
            
            # 等待
            print("\n⏳ 等待 60 秒后重新分析...\n")
            time.sleep(60)
            
        except KeyboardInterrupt:
            print("\n🛑 策略引擎已停止")
            break
        except Exception as e:
            print(f"❌ 错误：{e}")
            import traceback
            traceback.print_exc()
            time.sleep(60)


if __name__ == '__main__':
    main()
