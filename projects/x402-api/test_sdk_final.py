#!/usr/bin/env python3
import sys
sys.path.insert(0, '/home/admin/Ziwei/projects/x402-python-sdk')

from x402 import X402Client

client = X402Client(api_base_url='http://8.213.149.224:5002')

print("🧪 测试代码审计（真实 AI 模型 - 生产模式）...")
print()

result = client.request_with_payment(
    endpoint='/api/v1/code-audit',
    json_data={
        'code': 'def add(a, b): return a + b',
        'language': 'Python'
    }
)

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