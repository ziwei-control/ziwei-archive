#!/usr/bin/env python3
# =============================================================================
# 紫微智控 x402 API - 测试脚本
# 功能：测试所有 API 端点
# =============================================================================

import requests
import json
import base64

API_BASE_URL = "http://8.213.149.224:5000"

def test_health():
    """测试健康检查"""
    print("🔍 测试健康检查...")
    response = requests.get(f"{API_BASE_URL}/health")
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()


def test_stats():
    """测试收入统计"""
    print("🔍 测试收入统计...")
    response = requests.get(f"{API_BASE_URL}/api/v1/stats")
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()


def test_agent_endpoint(endpoint, data):
    """测试 Agent 端点"""
    print(f"🔍 测试端点: {endpoint}")
    print(f"请求数据: {json.dumps(data, indent=2)}")

    # 步骤 1: 发送请求（无支付）
    response = requests.post(f"{API_BASE_URL}/api/v1/{endpoint}", json=data)

    print(f"步骤 1 - 状态码: {response.status_code}")

    if response.status_code == 402:
        x402_info = response.json()['x402']
        print(f"步骤 1 - 收到 402 支付请求")
        print(f"  需要支付: {x402_info['amount']} {x402_info['currency']}")
        print(f"  钱包地址: {x402_info['wallet']}")
        print(f"  请求 ID: {response.json()['request_id']}")

        # 模拟支付证明（生产环境中应该是真实的交易哈希）
        payment_proof = json.dumps({
            "tx_hash": "0x" + "0" * 64,
            "amount": x402_info['amount'],
            "sender": "0x" + "1" * 40,
            "recipient": x402_info['wallet'],
            "timestamp": "2026-03-02T17:31:00"
        })

        # 步骤 2: 重发请求 + 支付证明
        response = requests.post(
            f"{API_BASE_URL}/api/v1/{endpoint}",
            json=data,
            headers={
                "x-payment-proof": base64.b64encode(payment_proof.encode()).decode()
            }
        )

        print(f"步骤 2 - 状态码: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"✅ 调用成功!")
            print(f"  Agent: {result['agent']}")
            print(f"  花费: ${result['cost']}")
            print(f"  模型: {result['model']}")
            print(f"  Token 使用: {result['tokens_used']}")
            print(f"  结果预览: {result['result'][:200]}..." if len(result['result']) > 200 else f"  结果: {result['result']}")
        else:
            print(f"❌ 调用失败: {response.json()}")
    else:
        print(f"❌ 未收到 402 响应: {response.json()}")

    print()


def main():
    print("=" * 70)
    print("🧪 紫微智控 x402 API - 测试脚本")
    print("=" * 70)
    print()

    # 基础测试
    test_health()
    test_stats()

    # Agent 测试
    print("=" * 70)
    print("🤖 Agent 端点测试")
    print("=" * 70)
    print()

    # T-01 架构设计
    test_agent_endpoint("architect", {
        "requirements": "设计一个简单的 To-Do 应用后端 API"
    })

    # T-02 代码生成
    test_agent_endpoint("code-gen", {
        "language": "Python",
        "description": "实现一个计算斐波那契数列的函数"
    })

    # T-03 代码审计
    test_agent_endpoint("code-audit", {
        "code": "def add(a, b):\n    return a + b",
        "language": "Python"
    })

    # T-05 翻译
    test_agent_endpoint("translate", {
        "text": "Hello, world!",
        "source_lang": "English",
        "target_lang": "Chinese"
    })

    print("=" * 70)
    print("✅ 测试完成!")
    print("=" * 70)


if __name__ == "__main__":
    main()