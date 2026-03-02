# x402 Python SDK - README (完整版)

## 🚀 简介

x402 Python SDK 是一个简洁、强大的 Python 库，让开发者轻松集成 x402 协议，实现微支付。

**x402 协议** 是 Coinbase 推出的开放协议，用于 HTTP 402 响应，允许 AI 智能体自主支付。

---

## ✨ 特性

- ✅ 自动处理 HTTP 402 支付请求
- ✅ 支付证明生成和验证
- ✅ 简化的 API 调用
- ✅ 完整的错误处理
- ✅ 内置重试机制
- ✅ 无需额外依赖（仅 requests）

---

## 📦 安装

```bash
pip install x402-sdk
```

或从源码安装：

```bash
git clone https://github.com/ziwei/x402-python-sdk.git
cd x402-python-sdk
pip install -r requirements.txt
```

---

## 🚀 快速开始

### 基础使用

```python
from x402 import X402Client

# 创建客户端
client = X402Client(
    api_base_url="http://api.example.com",
    wallet_address="0x..."
)

# 调用 API（自动处理支付）
result = client.request_with_payment(
    endpoint="/api/v1/code-audit",
    json_data={
        "code": "def hello(): pass",
        "concurrency": "Python"
    }
)

print(result['result'])
```

### 返回结果格式

```python
{
    "success": True,
    "result": "AI 审计结果",
    "agent": "code-audit",
    "cost": 0.05,
    "payment": {
        "tx_hash": "0x...",
        "amount": 0.05
    },
    "model": "qwen3-coder-next",
    "tokens_used": 1473
}
```

---

## 📚 API 参考

### X402Client

#### `__init__(api_base_url, wallet_address=None)`

创建客户端实例。

**参数**:
- `api_base_url` (str): API 基础 URL
- `wallet_address` (str, 可选): 钱包地址

**示例**:
```python
client = X402Client(
    api_base_url="http://localhost:5002",
    wallet_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
)
```

#### `request_with_payment(endpoint, method='POST', json_data=None, **kwargs)`

发起带支付请求的 API 调用。

**参数**:
- `endpoint` (str): API 端点（如 `/api/v1/code-audit`）
- `method` (str): HTTP 方法（GET/POST）
- `json_data` (dict, 可选): 请求数据
- `**kwargs`: 其他 requests 参数

**返回**: API 响应字典

**示例**:
```python
result = client.request_with_payment(
    endpoint="/api/v1/translate",
    json_data={
        "text": "Hello, world!",
        "source_lang": "English",
        "target_lang": "Chinese"
    }
)
```

#### `get_stats()`

获取统计信息。

**返回**: 统计信息字典

**示例**:
```python
stats = client.get_stats()
print(stats['stats']['total_earnings'])
```

#### `health_check()`

健康检查。

**返回**: 健康状态字典

**示例**:
```python
health = client.health_check()
print(health['status'])
```

---

## 📄 API 端点

| 端点 | 功能 | 价格 | 请求限制 |
|------|------|------|---------|
| POST /api/v1/architect | 架构设计 | $0.10 | 100/分钟 |
| POST /api/v1/code-gen | 代码生成 | $0.08 | 200/分钟 |
| POST /api/v1/code-audit | 代码审计 | $0.05 | 300/分钟 |
| POST /api/v1/logic | 逻辑推理 | $0.06 | 200/分钟 |
| POST /api/v1/translate | 翻译 | $0.02 | 500/分钟 |
| POST /api/v1/long-text | 长文解析 | $0.03 | 400/分钟 |
| POST /api/v1/crawl | 网络爬虫 | $0.04 | 300/分钟 |
| POST /api/v1/vision | 视觉解析 | $0.15 | 10/分钟 |

---

## 💡 使用示例

### 示例 1: 代码审计

```python
from x402 import X402Client

client = X402Client(
    api_base_url="http://localhost:5002",
    wallet_address="0x..."
)

result = client.request_with_payment(
    endpoint="/api/v1/code-audit",
    json_data={
        "code": """
def insecure():
    user_input = input("命令：")
    exec(user_input)
        """,
        "language": "Python"
    }
)

print(result['result'])
```

### 示例 2: 翻译

```python
from x402 import X402Client

client = X402Client(
    api_base_url="http://localhost:5002"
)

result = client.request_with_payment(
    endpoint="/api/v1/translate",
    json_data={
        "text": "Hello, how are you?",
        "source_lang": "English",
        "target_lang": "Chinese"
    }
)

print(result['result'])
```

### 示例 3: 批量调用

```python
from x402 import X402Client

client = X402Client(
    api_base_url="http://localhost:5002"
)

# 批量翻译
texts = [
    "Hello",
    "Thank you",
    "Good morning"
]

for text in texts:
    result = client.request_with_payment(
        endpoint="/api/v1/translate",
        json_data={
            "text": text,
            "source_lang": "English",
            "target_lang": "Chinese"
        }
    )
    print(f"{text} → {result['result']}")
```

---

## 🔧 高级用法

### 错误处理

```python
from x402 import X402Client, X402Error, PaymentError

try:
    result = client.request_with_payment(
        endpoint="/api/v1/code-audit",
        json_data={"code": "..."}
    )
    print(result['result'])
except X402Error as e:
    print(f"调用失败: {e}")
except PaymentError as e:
    print(f"支付失败: {e}")
```

### 自定义超时

```python
from x402 import X402Client

client = X402Client(
    api_base_url="http://api.example.com",
    timeout=30  # 30秒超时
)

result = client.request_with_payment(
    endpoint="/api/v1/code-audit",
    json_data={"code": "..."}
)
```

---

## 📄 License

Apache License 2.0

---

## 📞 支持

- GitHub: https://github.com/ziwei/x402-python-sdk
- Email: Martin
- Issues: GitHub Issues

---

**让 AI 智能体自主付费，开启机器经济时代！**