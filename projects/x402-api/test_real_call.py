#!/usr/bin/env python3
# 测试 x402 API 实际调用

import sys
sys.path.insert(0, "/home/admin/Ziwei/projects/x402-python-sdk")

from x402 import X402Client

client = X402Client(api_base_url="http://8.213.149.224:5000")

print("🧪 测试代码审计...")
result = client.request_with_payment(
    endpoint="/api/v1/code-audit",
    json_data={
        "code": "def login(username, password):\n    # TODO: 实现登录\n    pass",
        "language": "Python"
    }
)

print(f"\n✅ 调用成功!")
print(f"结果:\n{result['result']}")
print(f"\n花费: ${result['cost']}")
print(f"模型: {result['model']}")
print(f"Token: {result['tokens_used']}")