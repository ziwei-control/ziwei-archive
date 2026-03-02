# examples/advanced_usage.py
#!/usr/bin/env python3
"""
x402 Python SDK - 高级使用示例
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from x402 import X407Client, X402Error, PaymentError


def example_error_handling():
    """示例：错误处理"""
    print("=" * 70)
    print("🔧 示例：错误处理")
    print("=" * 70)
    print()

    client = X402Client(api_base_url="http://localhost:5002")

    try:
        result = client.request_with_payment(
            endpoint="/api/v1/code-audit",
            json_data={"code": "def test(): pass", "language": "Python"}
        )
        print(f"✅ 调用成功!")
        print(f"结果: {result['result'][:100]}...")
        print(f"花费: ${result['cost']}")

    except X402Error as e:
        print(f"❌ 调用失败: {e}")

    except PaymentError as e:
        print(f"❌ 支付失败: {e}")

    print()


def example_custom_timeout():
    """示例：自定义超时"""
    print("=" * 70)
    print("🔧 示例：自定义超时")
    print("=" * 70)
    print()

    client = X402Client(
        api_base_url="http://localhost:5002",
        timeout=60  # 60秒超时
    )

    try:
        result = client.request_with_payment(
            endpoint="/api/v1/long-text",
            json_data={
                "text": "很长的文本内容..." * 100
            }
        )
        print(f"✅ 调用成功（超时: 60秒）")

    except Exception as e:
        print(f"❌ 调用失败: {e}")

    print()


def example_batch_calls():
    """示例：批量调用"""
    print("=" * 70)
    print("🔧 示例：批量调用")
    print("=" * 70)
    print()

    client = X402Client(api_base_url="http://localhost:5002")

    # 批量翻译
    texts = [
        "Hello",
        "Thank you",
        "Good morning",
        "How are you?",
        "See you later"
    ]

    print(f"批量翻译 {len(texts)} 条消息:")
    print()

    success = 0
    for i, text in enumerate(texts, 1):
        try:
            result = client.request_with_payment(
                endpoint="/api/v1/translate",
                json_data={
                    "text": text,
                    "source_lang": "English",
                    "target_lang": "Chinese"
                }
            )
            print(f"  {i}. {text:20s} → {result['result']}")
            success += 1
        except Exception as e:
            print(f"  {i}. {text:20s} → 失败: {e}")

    print()
    print(f"成功率: {success}/{len(texts)}")

    print()


def example_get_stats():
    """示例：获取统计信息"""
    print("=" * 70)
    print("📊 示例：获取统计信息")
    print("=" * 70)
    print()

    client = X402Client(api_base_url="http://localhost:5002")

    try:
        stats = client.get_stats()

        print(f"💰 总收入: ${stats['stats']['total_earnings']}")
        print(f"📊 总交易: {stats['stats']['total_transactions']}")

        print()
        print("价格列表:")
        for token, price in stats['prices'].items():
            print(f"  {token}: ${price}")

    except Exception as e:
        print(f"❌ 获取统计失败: {e}")

    print()


def example_health_check():
    """示例：健康检查"""
    print("=" * 70)
    print("🏥 示例：健康检查")
    print("=" * 70)
    print()

    client = X402Client(api_base_url="http://localhost:5002")

    try:
        health = client.health_check()

        print(f"状态: {health['status']}")
        print(f"服务: {health['service']}")
        print(f"版本: {health['version']}")

    except Exception as e:
        print(f"❌ 健康检查失败: {e}")

    print()


def main():
    """主函数"""
    print()
    print("🎯 x402 Python SDK - 高级使用示例")
    print()
    print("示例列表:")
    print("  1. 错误处理")
    print("  2. 自定义超时")
    print("  3. 批量调用")
    print("  4. 获取统计")
    print("  5. 健康检查")
    print()

    example_error_handling()
    print()
    example_custom_timeout()
    print()
    example_batch_calls()
    print()
    example_get_stats()
    print()
    example_health_check()


if __name__ == "__main__":
    main()