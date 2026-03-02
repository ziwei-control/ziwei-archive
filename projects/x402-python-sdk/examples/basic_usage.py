"""
x402 Python SDK - 基础使用示例
"""

import sys
import os

# 添加 SDK 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from x402 import X402Client


def main():
    print("=" * 70)
    print("🚀 x402 Python SDK - 基础使用示例")
    print("=" * 70)
    print()

    # 创建客户端
    client = X402Client(
        api_base_url="http://localhost:5000",
        wallet_address="0x" + "1" * 40  # 模拟钱包地址
    )

    try:
        # 1. 健康检查
        print("🏥 健康检查...")
        health = client.health_check()
        print(f"✅ 服务状态: {health['status']}")
        print(f"   版本: {health['version']}")
        print()

        # 2. 获取统计
        print("📊 获取统计...")
        stats = client.get_stats()
        print(f"✅ 总收入: ${stats['stats']['total_earnings']}")
        print(f"   总交易: {stats['stats']['total_transactions']}")
        print()

        # 3. 调用代码审计 API
        print("🔍 代码审计...")
        result = client.request_with_payment(
            endpoint="/api/v1/code-audit",
            json_data={
                "code": "def add(a, b):\n    return a + b",
                "language": "Python"
            }
        )

        print(f"✅ 审计完成!")
        print(f"   结果: {result['result'][:100]}...")
        print(f"   花费: ${result['cost']}")
        print(f"   交易哈希: {result['payment']['tx_hash']}")
        print()

        # 4. 调用翻译 API
        print("🌐 翻译服务...")
        result = client.request_with_payment(
            endpoint="/api/v1/translate",
            json_data={
                "text": "Hello, world!",
                "source_lang": "English",
                "target_lang": "Chinese"
            }
        )

        print(f"✅ 翻译完成!")
        print(f"   结果: {result['result']}")
        print(f"   花费: ${result['cost']}")
        print()

    except Exception as e:
        print(f"❌ 错误: {e}")

    print("=" * 70)
    print("✅ 示例完成!")
    print("=" * 70)


if __name__ == "__main__":
    main()