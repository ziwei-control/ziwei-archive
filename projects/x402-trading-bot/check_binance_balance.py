#!/usr/bin/env python3
# =============================================================================
# Binance 账户余额查询
# =============================================================================

import sys

try:
    import ccxt
except ImportError:
    print("❌ 缺少 ccxt 库，请安装: pip3 install ccxt")
    sys.exit(1)

# API 配置
API_KEY = "0adWsF5X0HfPUfAo6uYSKpQYmJXmRryB8veStp4waJ3jvhBOsAHEcMPyN5srC9a1"
API_SECRET = "BE3kkKz0Q6Iu82bxKkJDAh1ATkWrpSHLuZhHFJPsHaDB6qScUI5ixjMWNnziKo3T"

def check_balance():
    """查询 Binance 账户余额"""
    print("=" * 70)
    print("💰 Binance 账户余额查询")
    print("=" * 70)
    print()

    if not API_SECRET:
        print("❌ 错误：缺少 API Secret")
        print()
        print("请提供完整的 API 密钥信息:")
        print("  - API Key: 已提供")
        print("  - API Secret: 需要提供")
        print()
        return

    try:
        # 创建交易所实例
        exchange = ccxt.binance({
            'apiKey': API_KEY,
            'secret': API_SECRET,
            'enableRateLimit': True,
        })

        # 获取账户余额
        balance = exchange.fetch_balance()

        # 显示总资产
        print("📊 账户总资产:")
        print("-" * 70)

        # 过滤有余额的币种
        assets = {}
        for currency, data in balance['total'].items():
            if data and data > 0:
                assets[currency] = data

        if not assets:
            print("⭕ 账户为空，没有资产")
        else:
            for currency, amount in sorted(assets.items(), key=lambda x: x[1], reverse=True):
                print(f"  {currency:10s}: {amount:>20.8f}")

        print()
        print("-" * 70)

        # 显示可用余额
        print("💵 可用余额:")
        print("-" * 70)

        for currency, data in balance['free'].items():
            if data and data > 0:
                print(f"  {currency:10s}: {data:>20.8f}")

        print()

        # 显示冻结余额
        frozen = {}
        for currency, data in balance['used'].items():
            if data and data > 0:
                frozen[currency] = data

        if frozen:
            print("🔒 冻结余额:")
            print("-" * 70)
            for currency, amount in frozen.items():
                print(f"  {currency:10s}: {amount:>20.8f}")
            print()

        print("=" * 70)
        print("✅ 查询完成")
        print("=" * 70)

    except ccxt.AuthenticationError as e:
        print(f"❌ 认证失败: {e}")
        print()
        print("可能原因:")
        print("  1. API Key 或 Secret 错误")
        print("  2. API Key 已过期或被禁用")
        print("  3. IP 地址不在白名单内")
    except ccxt.NetworkError as e:
        print(f"❌ 网络错误: {e}")
    except Exception as e:
        print(f"❌ 错误: {e}")


if __name__ == "__main__":
    check_balance()
