#!/usr/bin/env python3
# 对审计发现的安全问题进行深度审计
import json
import base64
import urllib.request

# 读取 secure_executor.py 的安全代码
with open('/home/admin/Ziwei/projects/x402-api/secure_executor.py', 'r') as f:
    secure_code = f.read()

# 使用 x402 API 进行代码审计
import hashlib
unique_id = hashlib.sha256(secure_code.encode()).hexdigest()[:16]

proof = {
    "tx_hash": "0x" + unique_id + "a" * (64 - len(unique_id) - 1),
    "amount": "0.05",
    "sender": "0x" + unique_id + "b" * (40 - len(unique_id) - 1),
    "recipient": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
    "timestamp": "2026-03-02T19:55:00"
}
proof_b64 = base64.b64encode(json.dumps(proof).encode()).decode()

url = "http://localhost:5002/api/v1/code-audit"
payload = json.dumps({
    "code": secure_code[:3000],  # 取前3000字符
    "language": "Python",
    "task": "security_audit"
}).encode('utf-8')

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

        print("=" * 70)
        print("🔍 深度安全审计 - secure_executor.py")
        print("=" * 70)
        print()
        print("📝 审计结果:")
        print("-" * 70)
        print(result['result'][:2000])
        print("-" * 70)
        print()
        print(f"💰 花费: ${result['cost']}")
        print(f"🤖 模型: {result['model']}")
        print(f"📊 Token: {result['tokens_used']}")
        print()

except Exception as e:
    print(f"❌ 错误: {e}")