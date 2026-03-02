#!/usr/bin/env python3
# Debug payment verification
import json
import base64
import urllib.request

# Create simple payment proof
proof = {
    "tx_hash": "0x" + "b" * 64,  # Use different hash to avoid duplication
    "amount": "0.05",
    "sender": "0x" + "2" * 40,
    "recipient": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
    "timestamp": "2026-03-02T19:21:00"
}

proof_b64 = base64.b64encode(json.dumps(proof).encode()).decode()

print("🔍 支付证明（编码前）:")
print(json.dumps(proof, indent=2))
print()
print("🔍 支付证明（Base64）:")
print(proof_b64[:100] + "...")
print()

# Try direct API call
url = "http://localhost:5002/api/v1/code-audit"
payload = json.dumps({"code": "def test(): pass", "language": "Python"}).encode('utf-8')

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
        print("✅ 响应:")
        print(json.dumps(result, indent=2, ensure_ascii=False)[:500])
except urllib.error.HTTPError as e:
    print(f"❌ HTTP {e.code}:")
    print(e.read().decode('utf-8'))
except Exception as e:
    print(f"❌ 错误: {e}")