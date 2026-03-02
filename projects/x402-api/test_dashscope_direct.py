#!/usr/bin/env python3
# Direct test of Dashscope API
import json
import urllib.request

API_KEY = "sk-sp-deb52dabf75c47308911359d51a0a420"
BASE_URL = "https://coding.dashscope.aliyuncs.com/v1"

url = f"{BASE_URL}/chat/completions"
payload = json.dumps({
    "model": "bailian/qwen3-coder-next",
    "messages": [{"role": "user", "content": "审计这段代码：def add(a, b): return a + b"}],
    "max_tokens": 500,
    "temperature": 0.7
}).encode('utf-8')

req = urllib.request.Request(
    url,
    data=payload,
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
)

print("🔍 直接测试阿里百炼 API...")
print(f"URL: {url}")
print(f"Model: bailian/qwen3-coder-next")
print()

try:
    with urllib.request.urlopen(req, timeout=30) as response:
        print(f"✅ 状态码: {response.status}")
        data = json.loads(response.read().decode('utf-8'))

        print()
        print("响应:")
        print(json.dumps(data, indent=2, ensure_ascii=False))

        if "choices" in data and len(data["choices"]) > 0:
            print()
            print("AI 回复:")
            print("-" * 70)
            print(data["choices"][0]["message"]["content"])
            print("-" * 70)

except urllib.error.HTTPError as e:
    print(f"❌ HTTP Error {e.code}:")
    print(e.read().decode('utf-8'))
except Exception as e:
    print(f"❌ 错误: {e}")