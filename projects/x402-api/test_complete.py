#!/usr/bin/env python3
# Simple test without requests
import json
import base64
import urllib.request

def make_api_call(endpoint, data, port=5002):
    """Make API call with payment proof"""
    # Create payment proof
    proof = {
        "tx_hash": "0x" + "a" * 64,
        "amount": "0.05",
        "sender": "0x" + "1" * 40,
        "recipient": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
        "timestamp": "2026-03-02T19:20:00"
    }
    proof_b64 = base64.b64encode(json.dumps(proof).encode()).decode()

    # Step 1: Request without payment (get 402)
    url = f"http://localhost:{port}{endpoint}"
    payload = json.dumps(data).encode('utf-8')

    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"}
    )

    print("📡 步骤 1: 发送请求（无支付）...")
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            print(f"   ❌ 预期收到 402，实际收到: {response.status}")
            return None
    except urllib.error.HTTPError as e:
        if e.code == 402:
            print("   ✅ 收到 402 Payment Required")
            x402_info = json.loads(e.read().decode('utf-8'))['x402']
            print(f"   💰 需要支付: {x402_info['amount']} {x402_info['currency']}")
            print(f"   📍 钱包: {x402_info['wallet']}")
        else:
            print(f"   ❌ 意外错误: {e.code}")
            return None

    # Step 2: Request with payment proof
    print()
    print("📡 步骤 2: 发送请求 + 支付证明...")

    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "x-payment-proof": proof_b64
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))

            if response.status == 200 and result.get('success'):
                return result
            else:
                print(f"   ❌ 调用失败: {result}")
                return None

    except Exception as e:
        print(f"   ❌ 错误: {e}")
        return None


def main():
    print("=" * 70)
    print("🧪 x402 API - 完整流程测试（真实 AI 模型）")
    print("=" * 70)
    print()

    # Test code audit
    result = make_api_call(
        endpoint="/api/v1/code-audit",
        data={
            "code": "def add(a, b):\n    return a + b\n\n# TODO: Add input validation",
            "language": "Python"
        },
        port=5002
    )

    if result:
        print()
        print("✅ 调用成功!")
        print()
        print(f"Agent: {result['agent']}")
        print(f"花费: ${result['cost']}")
        print(f"模型: {result['model']}")
        print(f"Token: {result['tokens_used']}")
        print()
        print("🔍 AI 审计结果:")
        print("=" * 70)
        print(result['result'])
        print("=" * 70)
        print()
        print(f"💳 交易: {result['payment']['tx_hash'][:20]}... (${result['payment']['amount']})")
        print()
        print("🎉 完美！真实 AI 模型调用成功！")
    else:
        print()
        print("❌ 测试失败")

    print()
    print("=" * 70)


if __name__ == "__main__":
    main()