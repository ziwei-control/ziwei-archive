# 📡 x402 API 使用指南（5002 端口）

**最后更新：** 2026-03-06  
**版本：** v1.0.0

---

## 🎯 什么是 5002 端口？

**5002 端口是 x402 API 的实际服务端口**，提供 8 个 AI 能力 API 调用。

**重要说明：**
- ❌ **不是网站** - 不能直接在浏览器访问
- ✅ **是 API 后端** - 需要通过代码调用
- 🔑 **需要 API Key** - 必须先获取 API 访问凭证

---

## 🔑 第一步：获取 API Key

**访问：** http://8.213.149.224:8090/get-api-key.html

**流程：**
1. 发送 0.03-0.07 USDC 到 `0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb`（Base 网络）
2. 输入发送地址或交易 hash
3. 点击"验证交易并获取密钥"
4. 获得 API_BASE_URL 和 API_KEY

**示例凭证：**
```
API_BASE_URL: 8.213.149.224
API_KEY: x402_a1b2c3d4e5f67890_65f8a000
```

---

## 📋 可用 API 列表

| API | 端点 | 价格 | 说明 |
|-----|------|------|------|
| 翻译 | `/api/v1/translator` | $0.02 | 多语言翻译 |
| 长文解析 | `/api/v1/long-text` | $0.03 | 文档摘要 |
| 网络爬虫 | `/api/v1/crawl` | $0.04 | 数据抓取 |
| 代码审计 | `/api/v1/code-audit` | $0.05 | 安全检查 |
| 逻辑推理 | `/api/v1/logic` | $0.06 | 复杂分析 |
| 代码生成 | `/api/v1/code-gen` | $0.08 | 快速开发 |
| 架构设计 | `/api/v1/architect` | $0.10 | 技术方案 |
| 视觉解析 | `/api/v1/vision` | $0.15 | 图片分析 |

---

## 💻 调用示例

### Python 示例

```python
import requests

# 配置
API_BASE_URL = "http://8.213.149.224:5002"
API_KEY = "x402_a1b2c3d4e5f67890_65f8a000"  # 替换为你的 API Key

# 示例 1: 翻译 API
response = requests.post(
    f"{API_BASE_URL}/api/v1/translator",
    json={
        "text": "Hello, world!",
        "source": "en",
        "target": "zh"
    },
    headers={
        "X-API-Key": API_KEY,
        "X-Payment-Amount": "20000",  # 0.02 USDC (6 位小数)
        "X-Payment-Token": "USDC"
    }
)

result = response.json()
print(f"翻译结果：{result['data']['translated_text']}")
print(f"花费：{result['cost']}")
```

### JavaScript 示例

```javascript
const API_BASE_URL = "http://8.213.149.224:5002";
const API_KEY = "x402_a1b2c3d4e5f67890_65f8a000"; // 替换为你的 API Key

// 翻译 API
const response = await fetch(`${API_BASE_URL}/api/v1/translator`, {
    method: "POST",
    headers: {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY,
        "X-Payment-Amount": "20000",
        "X-Payment-Token": "USDC"
    },
    body: JSON.stringify({
        text: "Hello, world!",
        source: "en",
        target: "zh"
    })
});

const result = await response.json();
console.log(`翻译结果：${result.data.translated_text}`);
console.log(`花费：${result.cost}`);
```

### cURL 示例

```bash
API_KEY="x402_a1b2c3d4e5f67890_65f8a000"

curl -X POST http://8.213.149.224:5002/api/v1/translator \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -H "X-Payment-Amount: 20000" \
  -H "X-Payment-Token: USDC" \
  -d '{
    "text": "Hello, world!",
    "source": "en",
    "target": "zh"
  }'
```

---

## 📊 请求格式

### 请求头（Headers）

| 字段 | 必填 | 说明 | 示例 |
|------|------|------|------|
| `X-API-Key` | ✅ | API 密钥 | `x402_a1b2c3d4e5f67890_65f8a000` |
| `X-Payment-Amount` | ✅ | 支付金额（6 位小数） | `20000` (= 0.02 USDC) |
| `X-Payment-Token` | ✅ | 支付代币 | `USDC` |
| `Content-Type` | ✅ | 内容类型 | `application/json` |

### 请求体（Body）

不同 API 需要不同的参数，详见下方各 API 文档。

### 响应格式

**成功响应：**
```json
{
  "success": true,
  "data": {
    // API 返回的具体数据
  },
  "cost": "0.02 USDC",
  "transaction_id": "tx_xxxxxxxxxxxx"
}
```

**失败响应：**
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述"
  }
}
```

---

## 🔍 各 API 详细用法

### 1. 翻译 API (`/api/v1/translator`)

**价格：** $0.02 USDC

**请求参数：**
```json
{
  "text": "要翻译的文本",
  "source": "源语言代码",
  "target": "目标语言代码"
}
```

**示例：**
```python
response = requests.post(
    "http://8.213.149.224:5002/api/v1/translator",
    json={
        "text": "Hello, world!",
        "source": "en",
        "target": "zh"
    },
    headers=headers
)
```

**响应：**
```json
{
  "success": true,
  "data": {
    "translated_text": "你好，世界！",
    "source_language": "en",
    "target_language": "zh"
  },
  "cost": "0.02 USDC"
}
```

---

### 2. 代码生成 API (`/api/v1/code-gen`)

**价格：** $0.08 USDC

**请求参数：**
```json
{
  "prompt": "代码需求描述",
  "language": "编程语言"
}
```

**示例：**
```python
response = requests.post(
    "http://8.213.149.224:5002/api/v1/code-gen",
    json={
        "prompt": "用 Python 写一个快速排序函数",
        "language": "python"
    },
    headers=headers
)
```

**响应：**
```json
{
  "success": true,
  "data": {
    "code": "def quick_sort(arr):\n    if len(arr) <= 1:\n        return arr\n    ...",
    "explanation": "这是一个快速排序实现..."
  },
  "cost": "0.08 USDC"
}
```

---

### 3. 代码审计 API (`/api/v1/code-audit`)

**价格：** $0.05 USDC

**请求参数：**
```json
{
  "code": "要审计的代码",
  "language": "编程语言"
}
```

**示例：**
```python
response = requests.post(
    "http://8.213.149.224:5002/api/v1/code-audit",
    json={
        "code": "def login(user, pwd):\n    if user == 'admin':\n        return True",
        "language": "python"
    },
    headers=headers
)
```

**响应：**
```json
{
  "success": true,
  "data": {
    "issues": [
        {
            "severity": "high",
            "description": "硬编码的管理员凭证",
            "line": 2
        }
    ],
    "suggestions": [
        "使用环境变量存储凭证",
        "添加密码验证"
    ]
  },
  "cost": "0.05 USDC"
}
```

---

### 4. 架构设计 API (`/api/v1/architect`)

**价格：** $0.10 USDC

**请求参数：**
```json
{
  "requirements": "项目需求描述",
  "scale": "项目规模（small/medium/large）"
}
```

**示例：**
```python
response = requests.post(
    "http://8.213.149.224:5002/api/v1/architect",
    json={
        "requirements": "需要一个电商网站，支持用户注册、商品展示、购物车、支付",
        "scale": "medium"
    },
    headers=headers
)
```

---

### 5. 逻辑推理 API (`/api/v1/logic`)

**价格：** $0.06 USDC

**请求参数：**
```json
{
  "problem": "问题描述",
  "context": "背景信息（可选）"
}
```

---

### 6. 长文解析 API (`/api/v1/long-text`)

**价格：** $0.03 USDC

**请求参数：**
```json
{
  "text": "长文本内容",
  "max_length": "摘要最大长度（可选）"
}
```

---

### 7. 网络爬虫 API (`/api/v1/crawl`)

**价格：** $0.04 USDC

**请求参数：**
```json
{
  "url": "要抓取的网址",
  "selector": "CSS 选择器（可选）"
}
```

---

### 8. 视觉解析 API (`/api/v1/vision`)

**价格：** $0.15 USDC

**请求参数：**
```json
{
  "image_url": "图片 URL",
  "task": "任务类型（describe/detect/ocr 等）"
}
```

---

## ❌ 常见错误码

| 错误码 | HTTP 状态 | 说明 | 解决方案 |
|--------|---------|------|---------|
| `INVALID_API_KEY` | 401 | API Key 无效 | 检查 API Key 是否正确 |
| `INSUFFICIENT_PAYMENT` | 402 | 支付金额不足 | 增加 X-Payment-Amount |
| `RATE_LIMIT_EXCEEDED` | 429 | 超出频率限制 | 等待后重试 |
| `INVALID_PAYLOAD` | 400 | 请求参数错误 | 检查请求格式 |
| `SERVICE_UNAVAILABLE` | 503 | 服务不可用 | 稍后重试 |

---

## 💡 最佳实践

### 1. 错误处理

```python
try:
    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()
    result = response.json()
    
    if result.get("success"):
        print(f"成功：{result['data']}")
    else:
        print(f"API 错误：{result['error']['message']}")
        
except requests.exceptions.RequestException as e:
    print(f"网络错误：{e}")
```

### 2. 重试机制

```python
import time

def call_api_with_retry(url, data, headers, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.post(url, json=data, headers=headers, timeout=30)
            if response.status_code == 429:  # Rate limited
                time.sleep(2 ** attempt)  # 指数退避
                continue
            return response.json()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(1)
```

### 3. 成本监控

```python
class APICostTracker:
    def __init__(self):
        self.total_cost = 0
        self.call_count = 0
    
    def track(self, cost_str):
        cost = float(cost_str.split()[0])
        self.total_cost += cost
        self.call_count += 1
        print(f"本次：${cost:.4f} | 累计：${self.total_cost:.4f} ({self.call_count}次)")
```

---

## 🔗 相关资源

**获取 API Key：**
- http://8.213.149.224:8090/get-api-key.html

**用户登录验证：**
- http://8.213.149.224:8091

**监控 Dashboard：**
- http://8.213.149.224:8091

**GitHub 仓库：**
- https://github.com/ziwei-control/ziwei-archive

**技术支持：**
- https://github.com/ziwei-control/ziwei-archive/issues

---

## 📞 获取帮助

**遇到问题？**

1. **检查 API Key** - 确保正确复制
2. **检查金额** - 确保 X-Payment-Amount 正确（6 位小数）
3. **查看错误信息** - 响应中的 error.message
4. **提交 Issue** - GitHub Issues 寻求帮助

---

**开始构建你的 AI 应用吧！** 🚀

**获取 API Key：** http://8.213.149.224:8090/get-api-key.html
