#!/usr/bin/env python3
# =============================================================================
# Binance 余额查询脚本 - 获取真实钱包余额
# =============================================================================

import requests
import hmac
import hashlib
import time
import os
from dotenv import load_dotenv

load_dotenv('/home/admin/Ziwei/projects/x402-trading-bot/.env')

API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')

def get_binance_balance():
    """获取 Binance 真实余额"""
    try:
        # 准备请求
        timestamp = int(time.time() * 1000)
        params = f'timestamp={timestamp}'
        
        # 生成签名
        signature = hmac.new(
            API_SECRET.encode('utf-8'),
            params.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        # 请求余额
        url = 'https://api.binance.com/api/v3/account'
        headers = {
            'X-MBX-APIKEY': API_KEY
        }
        params = {
            'timestamp': timestamp,
            'signature': signature
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            balances = {}
            total_usdt = 0
            
            for balance in data.get('balances', []):
                asset = balance['asset']
                free = float(balance['free'])
                locked = float(balance['locked'])
                total = free + locked
                
                if total > 0:
                    # 获取 USDT 价格（简单估算）
                    if asset == 'USDT':
                        usd_value = total
                    elif asset == 'BTC':
                        # 这里简化处理，实际应该调用价格 API
                        usd_value = total * 72000
                    elif asset == 'ETH':
                        usd_value = total * 2100
                    else:
                        usd_value = total
                    
                    balances[asset] = {
                        'free': free,
                        'locked': locked,
                        'total': total,
                        'usd_value': usd_value
                    }
                    total_usdt += usd_value
            
            return {
                'success': True,
                'balances': balances,
                'total_usdt': total_usdt,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
        else:
            return {
                'success': False,
                'error': f'API 错误：{response.status_code}',
                'message': response.text
            }
    
    except Exception as e:
        return {
            'success': False,
            'error': '查询失败',
            'message': str(e)
        }

if __name__ == '__main__':
    result = get_binance_balance()
    
    if result['success']:
        print("=" * 70)
        print("💰 Binance 真实钱包余额")
        print("=" * 70)
        print(f"查询时间：{result['timestamp']}")
        print()
        
        if result['balances']:
            for asset, data in result['balances'].items():
                print(f"{asset}:")
                print(f"  可用：{data['free']:.4f}")
                print(f"  冻结：{data['locked']:.4f}")
                print(f"  总计：{data['total']:.4f}")
                print(f"  估值：${data['usd_value']:.2f} USD")
                print()
            
            print("-" * 70)
            print(f"总估值：${result['total_usdt']:.2f} USD")
            print("=" * 70)
        else:
            print("⚠️ 钱包余额为空")
    else:
        print(f"❌ 查询失败：{result['error']}")
        print(f"详情：{result['message']}")
