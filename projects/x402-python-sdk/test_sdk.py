#!/usr/bin/env python3
# x402 Python SDK 测试脚本

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from x402 import X402Client, Payment, X402Error, PaymentError


def test_payment():
    """测试支付处理"""
    print("🧪 测试支付处理...")

    # 创建支付证明
    proof = Payment.create_payment_proof(
        tx_hash="0x" + "a" * 64,
        amount="0.05",
        sender="0x" + "1" * 40,
        recipient="0x" + "2" * 40
    )

    print(f"✅ 支付证明创建成功")

    # 解码支付证明
    decoded = Payment.decode_payment_proof(proof)
    print(f"✅ 支付证明解码成功: {decoded['tx_hash'][:20]}...")

    # 验证支付证明
    Payment.validate_payment_proof(decoded)
    print(f"✅ 支付证明验证成功")
    print()


def test_client():
    """测试客户端"""
    print("🧪 测试客户端...")

    client = X402Client(api_base_url="http://localhost:5000")

    try:
        # 健康检查
        health = client.health_check()
        print(f"✅ 健康检查: {health['status']}")

        # 获取统计
        stats = client.get_stats()
        print(f"✅ 统计信息: {stats['stats']['total_transactions']} 笔交易")

    except Exception as e:
        print(f"⚠️ 客户端测试: {e}")

    print()


def main():
    print("=" * 70)
    print("🧪 x402 Python SDK - 测试脚本")
    print("=" * 70)
    print()

    test_payment()
    test_client()

    print("=" * 70)
    print("✅ 测试完成!")
    print("=" * 70)


if __name__ == "__main__":
    main()