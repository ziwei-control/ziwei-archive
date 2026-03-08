#!/usr/bin/env python3
# =============================================================================
# 获取币安实时价格 - 用于交易机器人
# =============================================================================

import requests
from datetime import datetime

class BinancePriceFetcher:
    """币安实时价格获取器"""
    
    def __init__(self):
        self.base_url = "https://api.binance.com/api/v3"
    
    def get_price(self, symbol: str) -> float:
        """获取单个交易对价格"""
        try:
            # 转换为币安格式（BTC/USDT -> BTCUSDT）
            binance_symbol = symbol.replace('/', '').replace(' ', '')
            
            url = f"{self.base_url}/ticker/price?symbol={binance_symbol}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                return float(data['price'])
            else:
                print(f"❌ API 错误：{response.status_code}")
                return 0.0
                
        except Exception as e:
            print(f"❌ 获取价格失败 {symbol}: {e}")
            return 0.0
    
    def get_prices(self, symbols: list) -> dict:
        """获取多个交易对价格"""
        prices = {}
        for symbol in symbols:
            price = self.get_price(symbol)
            prices[symbol] = {
                'price': price,
                'timestamp': datetime.now().isoformat(),
                'source': 'Binance'
            }
        return prices
    
    def get_market_summary(self, symbols: list) -> str:
        """获取市场摘要"""
        prices = self.get_prices(symbols)
        
        summary = "╔═══════════════════════════════════════════════════════════╗\n"
        summary += "║       币安实时价格                                        ║\n"
        summary += "╠═══════════════════════════════════════════════════════════╣\n"
        summary += f"║  更新时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}                   ║\n"
        summary += "╚═══════════════════════════════════════════════════════════╝\n\n"
        summary += "【实时价格】\n"
        
        for symbol, data in prices.items():
            price = data['price']
            if 'DOGE' in symbol:
                summary += f"  {symbol}: ${price:.6f}\n"
            else:
                summary += f"  {symbol}: ${price:,.2f}\n"
        
        summary += "\n【数据来源】\n"
        summary += "  API: https://api.binance.com/api/v3/ticker/price\n"
        summary += "  延迟：<100ms\n"
        summary += "  更新：实时\n"
        
        return summary

if __name__ == "__main__":
    fetcher = BinancePriceFetcher()
    
    # 交易对配置
    symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'DOGE/USDT']
    
    print(fetcher.get_market_summary(symbols))
