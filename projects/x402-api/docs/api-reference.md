# 紫微智控 x402 API - 完整 API 文档

## 基础信息

- **Base URL**: `http://localhost:5000`
- **支付协议**: x402 (HTTP 402)
- **支付货币**: USDC (Base 链)
- **认证方式**: x402 支付证明

---

## API 端点

### 健康检查

```http
GET /health
```

**响应**:
```json
{
  "status": "ok",
  "service": "紫微智控 x402 API",
  "version": "1.0.0"
}
```

---

### 收入统计

```http
GET /api/v1/stats
```

**响应**:
```json
{
  "success": true,
  "stats": {
    "total_earnings": 12.45,
    "today_earnings": 5.30,
    "today_transactions": 53,
    "total_transactions": 124
  },
  "prices": {
    "architect": 0.10,
    "code-gen": 0.08,
    "code-audit": 0.05,
    "logic": 0.06,
    "translate": 0.02,
    "long-text": 0.03,
    "crawl": 0.04,
    "vision": 0.15
  }
}
```

---

## Agent API

所有 Agent API 的流程相同：

### 步骤 1: 发送请求（无支付）

```http
POST /api/v1/{agent_type}
Content-Type: application/json

{请求体}
```

**响应 (402 Payment Required)**:
```json
{
  "x402": {
    "amount": "0.05",
    "currency": "USDC",
    "wallet": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
    "facilitator": "https://x402.coinbase.com/verify",
    "network": "base",
    "token_address": "0x833589fCD6eDb6E08f4c7C32D4f71b54bA02929"
  },
  "request_id": "a1b2c3d4e5f6",
  "timestamp": "2026-03-02T17:30:00"
}
```

### 步骤 2: 完成 USDC 支付

使用 ERC-3009 标准进行无 gas 转账：
- 从钱包发送 USDC 到收款地址
- 获取交易哈希

### 步骤 3: 重发请求 + 支付证明

```http
POST /api/v1/{agent_type}
Content-Type: application/json
x-payment-proof: base64_encoded_payment_proof

{请求体}
```

**支付证明格式**:
```json
{
  "tx_hash": "0x...",
  "amount": "0.05",
  "sender": "0x...",
  "recipient": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
  "timestamp": "2026-03-02T17:31:00"
}
```

**响应 (200 OK)**:
```json
{
  "success": true,
  "result": "Agent 返回的结果",
  "agent": "code-audit",
  "cost": 0.05,
  "payment": {
    "tx_hash": "0x...",
    "amount": 0.05
  },
  "model": "bailian/qwen3-coder-next",
  "tokens_used": 1250
}
```

---

## 具体端点

### 1. 架构设计 (T-01)

```http
POST /api/v1/architect
Content-Type: application/json

{
  "requirements": "设计一个微服务架构的电商系统"
}
```

**价格**: $0.10

---

### 2. 代码生成 (T-02)

```http
POST /api/v1/code-gen
Content-Type: application/json

{
  "language": "Python",
  "description": "实现一个 RESTful API，包含用户注册和登录功能"
}
```

**价格**: $0.08

---

### 3. 代码审计 (T-03)

```http
POST /api/v1/code-audit
Content-Type: application/json

{
  "code": "def login(username, password):\n    # TODO: 实现登录逻辑\n    pass",
  "language": "Python"
}
```

**价格**: $0.05

---

### 4. 逻辑推理 (T-04)

```http
POST /api/v1/logic
Content-Type: application/json

{
  "problem": "如果所有猫都喜欢鱼，而小花是一只猫，那么小花喜欢鱼吗？请分析推理过程。"
}
```

**价格**: $0.06

---

### 5. 翻译 (T-05)

```http
POST /api/v1/translate
Content-Type: application/json

{
  "text": "Hello, world! This is a test.",
  "source_lang": "English",
  "target_lang": "Chinese"
}
```

**价格**: $0.02

---

### 6. 长文解析 (T-06)

```http
POST /api/v1/long-text
Content-Type: application/json

{
  "text": "很长的文本内容...",
  "task": "summary"
}
```

**价格**: $0.03

---

### 7. 网络爬虫 (T-07)

```http
POST /api/v1/crawl
Content-Type: application/json

{
  "url": "https://example.com",
  "task": "extract"
}
```

**价格**: $0.04

---

### 8. 视觉解析 (V-01)

```http
POST /api/v1/vision
Content-Type: application/json

{
  "image_url": "https://example.com/image.jpg",
  "task": "describe"
}
```

**价格**: $0.15

---

## 错误响应

### 无效支付证明

```http
HTTP 402 Payment Required

{
  "error": "Invalid or expired payment proof"
}
```

### Agent 不存在

```http
HTTP 400 Bad Request

{
  "error": "Agent type 'invalid' not found"
}
```

### 内部错误

```http
HTTP 500 Internal Server Error

{
  "success": false,
  "error": "API 调用失败: timeout"
}
```

---

## 使用示例

### Python 示例

```python
import requests
import json
import base64

# 1. 发送请求（无支付）
response = requests.post(
    "http://localhost:5000/api/v1/code-audit",
    json={
        "code": "def login(username, password):\n    return True",
        "language": "Python"
    }
)

# 2. 收到 402 支付请求
if response.status_code == 402:
    x402_info = response.json()['x402']
    print(f"需要支付: {x402_info['amount']} USDC")

    # 3. 完成 USDC 支付（使用你的钱包）
    # ... 支付代码 ...

    # 4. 构造支付证明
    payment_proof = json.dumps({
        "tx_hash": "0x...",  # 你的交易哈希
        "amount": x402_info['amount'],
        "sender": "0x...",  # 你的钱包地址
        "recipient": x402_info['wallet'],
        "timestamp": "2026-03-02T17:31:00"
    })

    # 5. 重发请求 + 支付证明
    response = requests.post(
        "http://localhost:5000/api/v1/code-audit",
        json={
            "code": "def login(username, password):\n    return True",
            "language": "Python"
        },
        headers={"x-payment-proof": base64.b64encode(payment_proof.encode()).decode()}
    )

# 6. 获取结果
if response.status_code == 200:
    result = response.json()
    print("审计结果:")
    print(result['result'])
    print(f"花费: ${result['cost']}")
```

---

## 支持与联系

- **GitHub**: https://github.com/ziwei/x402-api
- **文档**: /docs/api-reference.md
- **问题**: GitHub Issues
- **联系**: Martin (紫微智控)