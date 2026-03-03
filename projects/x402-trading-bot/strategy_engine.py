#!/usr/bin/env python3
# =============================================================================
# 交易策略引擎 - AI 决策核心
# 功能：综合分析情报、技术指标、情绪，生成交易信号
# 原则：本金安全第一，宁可错过不做错
# =============================================================================

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# 配置
STRATEGY_DIR = Path("/home/admin/Ziwei/data/strategy")
STRATEGY_DIR.mkdir(parents=True, exist_ok=True)

# 安全参数（核心！）
SAFETY_CONFIG = {
    'max_position_per_trade': 0.05,  # 单笔交易最多 5% 仓位
    'max_total_position': 0.30,      # 总仓位最多 30%
    'stop_loss': -0.05,              # 止损 -5%（严格）
    'take_profit': 0.15,             # 止盈 +15%（保守）
    'trailing_stop': 0.08,           # 移动止盈 8%
    'min_volume_24h': 1000000,       # 最小 24h 交易量 $1M（防小币种）
    'min_holders': 10000,            # 最小持仓人数 1 万（防骗局）
    'max_risk_per_trade': 0.02,      # 单笔最大风险 2%
}


class StrategyEngine:
    """交易策略引擎"""
    
    def __init__(self):
        self.positions = {}
        self.trade_history = []
        self.signal_cache = {}
        
    def load_intel(self, limit: int = 1) -> Optional[Dict]:
        """加载最新情报"""
        intel_dir = Path("/home/admin/Ziwei/data/intel")
        
        if not intel_dir.exists():
            return None
        
        # 获取最新情报文件
        intel_files = sorted(intel_dir.glob("intel_*.json"), reverse=True)
        
        if not intel_files:
            return None
        
        with open(intel_files[0], 'r') as f:
            return json.load(f)
    
    def check_rsi_signal(self, rsi: float) -> Tuple[bool, str]:
        """RSI 信号判断"""
        if rsi < 30:
            return True, "RSI 超卖 (<30)"
        elif rsi > 70:
            return False, "RSI 超买 (>70)"
        return None, "RSI 中性"
    
    def check_trend(self, price_data: Dict) -> Tuple[bool, str]:
        """趋势判断"""
        change_24h = price_data.get('change_24h', 0)
        
        if change_24h > 5:
            return True, f"上涨趋势 (+{change_24h:.1f}%)"
        elif change_24h < -5:
            return False, f"下跌趋势 ({change_24h:.1f}%)"
        return None, "横盘震荡"
    
    def check_sentiment(self, sentiment: Dict) -> Tuple[bool, str]:
        """情绪判断"""
        label = sentiment.get('label', 'neutral')
        score = sentiment.get('score', 0)
        
        if label == 'bullish' and score >= 2:
            return True, f"看涨情绪 (score={score})"
        elif label == 'bearish' and score <= -2:
            return False, f"看跌情绪 (score={score})"
        return None, "情绪中性"
    
    def check_safety(self, symbol: str, price_data: Dict) -> Tuple[bool, List[str]]:
        """安全检查（防骗/防风险）"""
        warnings = []
        safe = True
        
        # 1. 检查交易量
        volume = price_data.get('volume_24h', 0)
        if volume < SAFETY_CONFIG['min_volume_24h']:
            warnings.append(f"⚠️ 交易量过低 (${volume:,.0f} < ${SAFETY_CONFIG['min_volume_24h']:,.0f})")
            safe = False
        
        # 2. 检查市值（太小的容易操纵）
        market_cap = price_data.get('market_cap', 0)
        if market_cap < 100000000:  # $100M
            warnings.append(f"⚠️ 市值过小 (${market_cap:,.0f})")
            # 不直接否决，但警告
        
        # 3. 检查价格波动（太大风险高）
        high = price_data.get('high_24h', 0)
        low = price_data.get('low_24h', 0)
        if low > 0:
            volatility = (high - low) / low
            if volatility > 0.3:  # 30% 波动
                warnings.append(f"⚠️ 波动过大 ({volatility*100:.1f}%)")
        
        return safe, warnings
    
    def generate_signal(self, symbol: str, intel: Dict) -> Optional[Dict]:
        """生成交易信号"""
        price_data = intel.get('prices', {}).get(symbol, {})
        sentiment = intel.get('sentiment', {}).get(symbol, {})
        
        if not price_data:
            return None
        
        # 安全检查
        is_safe, warnings = self.check_safety(symbol, price_data)
        if not is_safe:
            print(f"❌ {symbol} 安全检查未通过:")
            for w in warnings:
                print(f"   {w}")
            return None
        
        # 多维度评分
        score = 0
        reasons = []
        
        # 1. RSI 评分（权重 30%）
        # 注意：这里简化处理，实际需要历史价格计算 RSI
        rsi_signal, rsi_reason = self.check_rsi_signal(50)  # 默认中性
        if rsi_signal is True:
            score += 30
            reasons.append(rsi_reason)
        elif rsi_signal is False:
            score -= 30
        
        # 2. 趋势评分（权重 40%）
        trend_signal, trend_reason = self.check_trend(price_data)
        if trend_signal is True:
            score += 40
            reasons.append(trend_reason)
        elif trend_signal is False:
            score -= 40
        
        # 3. 情绪评分（权重 30%）
        sentiment_signal, sentiment_reason = self.check_sentiment(sentiment)
        if sentiment_signal is True:
            score += 30
            reasons.append(sentiment_reason)
        elif sentiment_signal is False:
            score -= 30
        
        # 4. 热点加成
        hot_tokens = intel.get('hot_tokens', [])
        for hot in hot_tokens:
            if hot.get('symbol') == symbol:
                score += 20
                reasons.append(f"热点代币 (#{hot_tokens.index(hot)+1})")
                break
        
        # 决策
        signal = None
        if score >= 60:
            signal = 'STRONG_BUY'
        elif score >= 40:
            signal = 'BUY'
        elif score >= 20:
            signal = 'WEAK_BUY'
        elif score <= -60:
            signal = 'STRONG_SELL'
        elif score <= -40:
            signal = 'SELL'
        elif score <= -20:
            signal = 'WEAK_SELL'
        else:
            signal = 'HOLD'
        
        # 生成信号
        trade_signal = {
            'symbol': symbol,
            'signal': signal,
            'score': score,
            'price': price_data.get('price', 0),
            'change_24h': price_data.get('change_24h', 0),
            'reasons': reasons,
            'warnings': warnings,
            'timestamp': datetime.now().isoformat(),
            'suggested_position': self.calculate_position(score, price_data),
            'stop_loss': price_data.get('price', 0) * (1 + SAFETY_CONFIG['stop_loss']),
            'take_profit': price_data.get('price', 0) * (1 + SAFETY_CONFIG['take_profit'])
        }
        
        return trade_signal
    
    def calculate_position(self, score: int, price_data: Dict) -> float:
        """计算建议仓位（基于评分和风险）"""
        base_position = SAFETY_CONFIG['max_position_per_trade']
        
        # 根据评分调整
        if score >= 60:
            position = base_position * 1.0  # 满分仓位
        elif score >= 40:
            position = base_position * 0.7
        elif score >= 20:
            position = base_position * 0.4
        else:
            position = 0
        
        # 确保不超过最大风险
        max_risk_position = SAFETY_CONFIG['max_risk_per_trade'] / abs(SAFETY_CONFIG['stop_loss'])
        position = min(position, max_risk_position)
        
        return round(position, 4)
    
    def analyze_all(self, intel: Dict) -> List[Dict]:
        """分析所有代币，生成信号列表"""
        signals = []
        
        symbols = list(intel.get('prices', {}).keys())
        
        print(f"\n📊 分析 {len(symbols)} 个代币...")
        
        for symbol in symbols:
            signal = self.generate_signal(symbol, intel)
            if signal:
                signals.append(signal)
        
        # 按评分排序
        signals.sort(key=lambda x: x['score'], reverse=True)
        
        return signals
    
    def save_signals(self, signals: List[Dict]):
        """保存信号"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filepath = STRATEGY_DIR / f"signals_{timestamp}.json"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(signals, f, indent=2, ensure_ascii=False)
        
        print(f"💾 信号已保存：{filepath}")
        return filepath
    
    def print_top_signals(self, signals: List[Dict], limit: int = 5):
        """打印最佳信号"""
        print("\n" + "=" * 70)
        print(f"🎯 Top {limit} 交易信号")
        print("=" * 70)
        
        for i, signal in enumerate(signals[:limit], 1):
            print(f"\n{i}. {signal['symbol']} - {signal['signal']}")
            print(f"   评分：{signal['score']}")
            print(f"   价格：${signal['price']:.6f}")
            print(f"   24h 变化：{signal['change_24h']:+.2f}%")
            print(f"   建议仓位：{signal['suggested_position']*100:.1f}%")
            print(f"   止损：${signal['stop_loss']:.6f}")
            print(f"   止盈：${signal['take_profit']:.6f}")
            print(f"   理由：{', '.join(signal['reasons'])}")
            
            if signal['warnings']:
                print(f"   警告：{', '.join(signal['warnings'])}")


def main():
    """主函数"""
    print("=" * 70)
    print("🧠 紫微智控 - 交易策略引擎")
    print("=" * 70)
    
    engine = StrategyEngine()
    
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
            
            # 显示最佳信号
            engine.print_top_signals(signals)
            
            # 等待下次分析（1 分钟）
            print("\n⏳ 等待 1 分钟后重新分析...\n")
            time.sleep(60)
            
        except KeyboardInterrupt:
            print("\n🛑 策略引擎已停止")
            break
        except Exception as e:
            print(f"❌ 错误：{e}")
            time.sleep(60)


if __name__ == '__main__':
    main()
