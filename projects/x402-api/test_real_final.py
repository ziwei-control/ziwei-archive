#!/usr/bin/env python3
# Test with corrected port
import json
import base64
import urllib.request

proof = {
    "tx_hash": "0x" + "a" * 64,
    "amount": "0.05",
    "sender": "0x" + "1" * 40,
    "recipient": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
    "timestamp": "2026-03-02T19:18:00"
}
proof_b64 = base64.b64encode(json.dumps(proof).encode()).decode()

url = "http://localhost:5002/api/v1/code-audit"
payload = json.dumps({"code": "def add(a, b): return a + b", "language": "Python"}).encode('utf-8')

req = urllib.request.Request(
    url,
    data=payload,
    headers={
        "Content-Type": "application/json",
        "x-payment-proof": proof_b64
    }
)

print("🧪 测试代码审计（真实 AI 模型 - 生产模式）...")
print()

try:
    with urllib.request.urlopen(req, timeout=30) as response:
        result = json.loads(response.read().decode('utf-8'))

        print("✅ 调用成功!")
        print()
        print(f"Agent: {result['agent']}")
        print(f"花费: ${result['cost']}")
        print(f"模型: {result['model']}")
        print(f"Token: {result['tokens_used']}")
        print()
        print("🔍 审计结果:")
        print("=" * 70)
        print(result['result'])
        print("=" * 70)
        print()
        print(f"交易哈希: {result['payment']['tx_hash'][:20]}...")

except Exception as e:
    print(f"❌ 错误: {e}")