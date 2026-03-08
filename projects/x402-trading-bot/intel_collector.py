#!/usr/bin/env python3
# =============================================================================
# 情报搜集器 - 24 小时监控加密货币信息
# 来源：谷歌新闻、推特、财经网站、链上数据
# =============================================================================

import os
import json
import time
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# 配置
INTEL_DIR = Path("/home/admin/Ziwei/data/intel")
INTEL_DIR.mkdir(parents=True, exist_ok=True)

# Top 100 代币列表（CoinMarketCap 前 100）
TOP_100_SYMBOLS = [
    "BTC", "ETH", "USDT", "BNB", "SOL", "XRP", "USDC", "STETH", "ADA", "DOGE",
    "TRX", "AVAX", "WBTC", "LINK", "MATIC", "TON", "SHIB", "DAI", "LTC", "BCH",
    "DOT", "UNI", "ATOM", "XLM", "ETC", "XMR", "OKB", "FIL", "LDO", "HBAR",
    "APT", "CRO", "NEAR", "VET", "ALGO", "ICP", "QNT", "GRT", "AAVE", "MKR",
    "SNX", "SAND", "MANA", "AXS", "THETA", "XTZ", "EOS", "EGLD", "RUNE", "FTM",
    "KLAY", "CHZ", "FLOW", "ZEC", "CAKE", "NEO", "BSV", "MINA", "KCS", "IOTA",
    "HNT", "XEC", "CRV", "BAT", "ENJ", "DASH", "ZIL", "COMP", "YFI", "1INCH",
    "SUSHI", "BAL", "REN", "KNC", "LRC", "STORJ", "ANT", "BNT", "REP", "NMR",
    "MLN", "OCEAN", "FET", "AGIX", "INJ", "IMX", "OP", "ARB", "BLUR", "PEPE",
    "FLOKI", "BONK", "WIF", "BOME", "SLERF", "WLD", "STRK", "PYTH", "JUP", "TIA"
]

# 新闻源配置
NEWS_SOURCES = {
    "coindesk": "https://www.coindesk.com/arc/outboundfeeds/rss",
    "cointelegraph": "https://cointelegraph.com/rss",
    "decrypt": "https://decrypt.co/feed",
    "theblock": "https://www.theblock.co/rss.xml",
}

# 社交媒体监控关键词
SOCIAL_KEYWORDS = ["moon", "pump", "breakout", "bullish", "bearish", "buy", "sell", "hodl"]


class IntelCollector:
    """情报搜集器"""
    
    def __init__(self):
        self.intel_cache = {}
        self.sentiment_cache = {}
        
    def fetch_google_news(self, symbol: str) -> List[Dict]:
        """搜索谷歌新闻（使用免费 API）"""
        try:
            # 使用 Google News RSS（免费）
            query = f"{symbol} cryptocurrency"
            url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
            
            response = requests.get(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }, timeout=10)
            
            if response.status_code == 200:
                # 简单解析 RSS
                articles = []
                for line in response.text.split('<item>')[1:11]:  # 取前 10 条
                    if '<title>' in line:
                        title = line.split('<title>')[1].split('</title>')[0]
                        link = line.split('<link>')[1].split('</link>')[0]
                        articles.append({
                            'title': title,
                            'link': link,
                            'source': 'Google News',
                            'time': datetime.now().isoformat()
                        })
                return articles
        except Exception as e:
            print(f"❌ 谷歌新闻搜索失败 {symbol}: {e}")
        
        return []
    
    def fetch_crypto_prices(self, symbols: List[str]) -> Dict:
        """获取加密货币价格数据（CoinGecko 免费 API）"""
        try:
            # CoinGecko API（免费，无需 key）
            ids = {
                'BTC': 'bitcoin', 'ETH': 'ethereum', 'BNB': 'binancecoin',
                'SOL': 'solana', 'XRP': 'ripple', 'ADA': 'cardano',
                'DOGE': 'dogecoin', 'TRX': 'tron', 'AVAX': 'avalanche-2',
                'DOT': 'polkadot', 'MATIC': 'matic-network', 'LINK': 'chainlink'
            }
            
            coin_ids = [ids.get(s, s.lower()) for s in symbols[:10]]  # 每次最多 10 个
            coin_ids_str = ','.join(coin_ids)
            
            url = f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids={coin_ids_str}&order=market_cap_desc&per_page=100&page=1&sparkline=false"
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                prices = {}
                for coin in data:
                    symbol = coin['symbol'].upper()
                    prices[symbol] = {
                        'price': coin['current_price'],
                        'change_24h': coin['price_change_percentage_24h'],
                        'market_cap': coin['market_cap'],
                        'volume_24h': coin['total_volume'],
                        'high_24h': coin['high_24h'],
                        'low_24h': coin['low_24h'],
                        'time': datetime.now().isoformat()
                    }
                return prices
        except Exception as e:
            print(f"❌ 获取价格数据失败：{e}")
        
        return {}
    
    def calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """计算 RSI 指标"""
        if len(prices) < period + 1:
            return 50.0  # 默认中性
        
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
    
    def analyze_sentiment(self, articles: List[Dict]) -> Dict:
        """简单情绪分析"""
        if not articles:
            return {'score': 0, 'label': 'neutral'}
        
        positive_words = ['bullish', 'moon', 'pump', 'breakout', 'buy', 'surge', 'rally', 'gain']
        negative_words = ['bearish', 'crash', 'dump', 'sell', 'drop', 'loss', 'decline', 'fall']
        
        score = 0
        for article in articles:
            title = article.get('title', '').lower()
            for word in positive_words:
                if word in title:
                    score += 1
            for word in negative_words:
                if word in title:
                    score -= 1
        
        if score > 0:
            label = 'bullish'
        elif score < 0:
            label = 'bearish'
        else:
            label = 'neutral'
        
        return {
            'score': score,
            'label': label,
            'articles_count': len(articles)
        }
    
    def collect_intel(self, symbols: List[str]) -> Dict:
        """搜集情报汇总"""
        print(f"📡 开始搜集 {len(symbols)} 个代币情报...")
        
        intel = {
            'timestamp': datetime.now().isoformat(),
            'prices': {},
            'news': {},
            'sentiment': {},
            'rsi': {},
            'hot_tokens': []
        }
        
        # 1. 获取价格数据
        print("💰 获取价格数据...")
        intel['prices'] = self.fetch_crypto_prices(symbols)
        
        # 2. 获取新闻和情绪（前 20 个代币）
        print("📰 搜集新闻...")
        for symbol in symbols[:20]:
            articles = self.fetch_google_news(symbol)
            if articles:
                intel['news'][symbol] = articles
                intel['sentiment'][symbol] = self.analyze_sentiment(articles)
        
        # 3. 计算热点代币（基于 24h 涨幅 + 情绪）
        print("🔥 分析热点代币...")
        hot_tokens = []
        for symbol, price_data in intel['prices'].items():
            score = 0
            
            # 24h 涨幅评分
            change = price_data.get('change_24h', 0)
            if change > 10:
                score += 3
            elif change > 5:
                score += 2
            elif change > 0:
                score += 1
            
            # 情绪评分
            sentiment = intel['sentiment'].get(symbol, {})
            if sentiment.get('label') == 'bullish':
                score += sentiment.get('score', 0)
            
            if score >= 2:
                hot_tokens.append({
                    'symbol': symbol,
                    'score': score,
                    'change_24h': change,
                    'sentiment': sentiment.get('label', 'neutral')
                })
        
        # 按热度排序
        hot_tokens.sort(key=lambda x: x['score'], reverse=True)
        intel['hot_tokens'] = hot_tokens[:10]  # 前 10 个热点
        
        return intel
    
    def save_intel(self, intel: Dict):
        """保存情报到文件"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filepath = INTEL_DIR / f"intel_{timestamp}.json"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(intel, f, indent=2, ensure_ascii=False)
        
        print(f"💾 情报已保存：{filepath}")
        return filepath


def main():
    """主函数"""
    print("=" * 70)
    print("🕵️ 紫微智控 - 情报搜集器")
    print("=" * 70)
    
    collector = IntelCollector()
    
    while True:
        try:
            # 搜集情报
            intel = collector.collect_intel(TOP_100_SYMBOLS[:30])  # 前 30 个
            
            # 保存
            collector.save_intel(intel)
            
            # 显示热点
            print("\n🔥 Top 5 热点代币:")
            for i, token in enumerate(intel['hot_tokens'][:5], 1):
                print(f"  {i}. {token['symbol']}: {token['change_24h']:.2f}% | {token['sentiment']}")
            
            # 等待下次更新（5 分钟）
            print("\n⏳ 等待 1 分钟后更新...\n")
            time.sleep(60)
            
        except KeyboardInterrupt:
            print("\n🛑 情报搜集已停止")
            break
        except Exception as e:
            print(f"❌ 错误：{e}")
            time.sleep(60)


if __name__ == '__main__':
    main()
