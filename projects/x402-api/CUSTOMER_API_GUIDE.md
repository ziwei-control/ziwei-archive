# x402 API 客户调用指南

**最后更新：** 2026-03-05  
**适用对象：** 开发者、企业客户、合作伙伴

---

## 🚀 快速开始（5 分钟）

### 第一步：准备 USDC 钱包

1. **安装 MetaMask**（或其他支持 Base 链的钱包）
   - Chrome 扩展：[metamask.io](https://metamask.io/)
   - 手机 App：iOS/Android 应用商店

2. **添加 Base 网络**
   - Network Name: Base
   - RPC URL: https://mainnet.base.org
   - Chain ID: 8453
   - Currency Symbol: ETH

3. **充值 USDC**
   - 在币安/ Coinbase 购买 USDC
   - 提现到钱包（选择 Base 网络，手续费最低）
   - 建议充值：$10-50 USDC（可用很久）

---

## 💻 代码示例

### Python 完整示例

```python
#!/usr/bin/env python3
"""
x402 API 调用示例 - Python
"""
import requests
import json
from datetime import datetime

# ============ 配置 ============
API_BASE_URL = "http://8.213.149.224:5002"  # 合作后获取真实地址
API_KEY = "your_api_key"  # 合作后获取
WALLET_ADDRESS = "your_wallet_address"  # 你的 USDC 钱包地址

# ============ 签名函数（简化版） ============
def generate_signature(payload, wallet_private_key):
    """
    生成支付签名
    实际使用中需要用钱包私钥签名
    这里简化处理，实际项目会用 web3.py
    """
    import hashlib
    message = json.dumps(payload, sort_keys=True)
    signature = hashlib.sha256(message.encode()).hexdigest()
    return signature

# ============ 调用 API ============
def call_x402_api(endpoint, payload, price_usdc):
    """
    调用 x402 API
    
    Args:
        endpoint: API 端点，如 '/api/v1/translator'
        payload: 请求数据
        price_usdc: 价格（USDC，6 位小数）
    
    Returns:
        API 响应数据
    """
    url = f"{API_BASE_URL}{endpoint}"
    
    # 生成签名
    signature = generate_signature(payload, "your_private_key")
    
    # 设置请求头
    headers = {
        "Content-Type": "application/json",
        "X-Payment-Amount": str(int(price_usdc * 1000000)),  # 转为 6 位小数
        "X-Payment-Token": "USDC",
        "X-Payment-Signature": signature,
        "X-Wallet-Address": WALLET_ADDRESS,
        "X-API-Key": API_KEY
    }
    
    # 发送请求
    response = requests.post(url, json=payload, headers=headers)
    
    # 检查响应
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API 调用失败：{response.status_code} - {response.text}")

# ============ 使用示例 ============
if __name__ == "__main__":
    try:
        # 示例 1: 翻译 API
        print("📝 调用翻译 API...")
        result = call_x402_api(
            endpoint="/api/v1/translator",
            payload={
                "text": "Hello, world!",
                "source": "en",
                "target": "zh"
            },
            price_usdc=0.02
        )
        print(f"✅ 翻译结果：{result['data']['translated_text']}")
        print(f"💰 花费：{result['cost']}")
        
        # 示例 2: 代码生成 API
        print("\n💻 调用代码生成 API...")
        result = call_x402_api(
            endpoint="/api/v1/code-gen",
            payload={
                "prompt": "用 Python 写一个快速排序函数",
                "language": "python"
            },
            price_usdc=0.08
        )
        print(f"✅ 生成的代码：{result['data']['code'][:200]}...")
        print(f"💰 花费：{result['cost']}")
        
        # 示例 3: 代码审计 API
        print("\n🔍 调用代码审计 API...")
        result = call_x402_api(
            endpoint="/api/v1/code-audit",
            payload={
                "code": "def add(a, b): return a + b",
                "language": "python"
            },
            price_usdc=0.05
        )
        print(f"✅ 审计结果：{result['data']['issues']}")
        print(f"💰 花费：{result['cost']}")
        
    except Exception as e:
        print(f"❌ 错误：{e}")
```

---

### JavaScript/Node.js 完整示例

```javascript
/**
 * x402 API 调用示例 - JavaScript
 */
const crypto = require('crypto');
const axios = require('axios');

// ============ 配置 ============
const API_BASE_URL = 'http://8.213.149.224:5002';
const API_KEY = 'your_api_key';
const WALLET_ADDRESS = 'your_wallet_address';

/**
 * 生成支付签名
 */
function generateSignature(payload, privateKey) {
    const message = JSON.stringify(payload, Object.keys(payload).sort());
    const signature = crypto.createHash('sha256').update(message).digest('hex');
    return signature;
}

/**
 * 调用 x402 API
 */
async function callX402Api(endpoint, payload, priceUsdc) {
    const url = `${API_BASE_URL}${endpoint}`;
    
    // 生成签名
    const signature = generateSignature(payload, 'your_private_key');
    
    // 设置请求头
    const headers = {
        'Content-Type': 'application/json',
        'X-Payment-Amount': Math.floor(priceUsdc * 1000000).toString(),
        'X-Payment-Token': 'USDC',
        'X-Payment-Signature': signature,
        'X-Wallet-Address': WALLET_ADDRESS,
        'X-API-Key': API_KEY
    };
    
    // 发送请求
    const response = await axios.post(url, payload, { headers });
    
    return response.data;
}

// ============ 使用示例 ============
async function main() {
    try {
        // 示例 1: 翻译 API
        console.log('📝 调用翻译 API...');
        const translateResult = await callX402Api(
            '/api/v1/translator',
            {
                text: 'Hello, world!',
                source: 'en',
                target: 'zh'
            },
            0.02
        );
        console.log(`✅ 翻译结果：${translateResult.data.translated_text}`);
        console.log(`💰 花费：${translateResult.cost}`);
        
        // 示例 2: 代码生成 API
        console.log('\n💻 调用代码生成 API...');
        const codeGenResult = await callX402Api(
            '/api/v1/code-gen',
            {
                prompt: '用 JavaScript 写一个快速排序函数',
                language: 'javascript'
            },
            0.08
        );
        console.log(`✅ 生成的代码：${codeGenResult.data.code.substring(0, 200)}...`);
        console.log(`💰 花费：${codeGenResult.cost}`);
        
    } catch (error) {
        console.error('❌ 错误:', error.message);
    }
}

main();
```

---

### Go 完整示例

```go
package main

import (
	"bytes"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
)

// 配置
const (
	APIBaseURL  = "http://8.213.149.224:5002"
	APIKey      = "your_api_key"
	WalletAddr  = "your_wallet_address"
)

// 请求结构
type APIRequest struct {
	Text   string `json:"text,omitempty"`
	Source string `json:"source,omitempty"`
	Target string `json:"target,omitempty"`
	Prompt string `json:"prompt,omitempty"`
	Code   string `json:"code,omitempty"`
}

// 响应结构
type APIResponse struct {
	Success bool        `json:"success"`
	Data    interface{} `json:"data"`
	Cost    string      `json:"cost"`
}

// 生成签名
func generateSignature(payload APIRequest) string {
	data, _ := json.Marshal(payload)
	hash := sha256.Sum256(data)
	return hex.EncodeToString(hash[:])
}

// 调用 API
func callX402API(endpoint string, payload APIRequest, priceUSD float64) (*APIResponse, error) {
	url := APIBaseURL + endpoint
	
	// 序列化 payload
	payloadJSON, err := json.Marshal(payload)
	if err != nil {
		return nil, err
	}
	
	// 生成签名
	signature := generateSignature(payload)
	
	// 创建请求
	req, err := http.NewRequest("POST", url, bytes.NewBuffer(payloadJSON))
	if err != nil {
		return nil, err
	}
	
	// 设置请求头
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("X-Payment-Amount", fmt.Sprintf("%d", int(priceUSD*1000000)))
	req.Header.Set("X-Payment-Token", "USDC")
	req.Header.Set("X-Payment-Signature", signature)
	req.Header.Set("X-Wallet-Address", WalletAddr)
	req.Header.Set("X-API-Key", APIKey)
	
	// 发送请求
	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	
	// 读取响应
	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}
	
	var result APIResponse
	err = json.Unmarshal(body, &result)
	if err != nil {
		return nil, err
	}
	
	return &result, nil
}

func main() {
	// 示例：翻译 API
	fmt.Println("📝 调用翻译 API...")
	result, err := callX402API("/api/v1/translator", APIRequest{
		Text:   "Hello, world!",
		Source: "en",
		Target: "zh",
	}, 0.02)
	
	if err != nil {
		fmt.Printf("❌ 错误：%v\n", err)
		return
	}
	
	fmt.Printf("✅ 翻译成功：%v\n", result.Data)
	fmt.Printf("💰 花费：%s\n", result.Cost)
}
```

---

### cURL 命令行示例

```bash
#!/bin/bash

# x402 API 调用示例 - cURL

API_BASE_URL="http://8.213.149.224:5002"
API_KEY="your_api_key"
WALLET_ADDRESS="your_wallet_address"

# 示例 1: 翻译 API
echo "📝 调用翻译 API..."
curl -X POST "${API_BASE_URL}/api/v1/translator" \
  -H "Content-Type: application/json" \
  -H "X-Payment-Amount: 20000" \
  -H "X-Payment-Token: USDC" \
  -H "X-Payment-Signature: $(echo -n '{"text":"Hello","source":"en","target":"zh"}' | sha256sum | cut -d' ' -f1)" \
  -H "X-Wallet-Address: ${WALLET_ADDRESS}" \
  -H "X-API-Key: ${API_KEY}" \
  -d '{
    "text": "Hello, world!",
    "source": "en",
    "target": "zh"
  }'

echo ""

# 示例 2: 代码生成 API
echo "💻 调用代码生成 API..."
curl -X POST "${API_BASE_URL}/api/v1/code-gen" \
  -H "Content-Type: application/json" \
  -H "X-Payment-Amount: 80000" \
  -H "X-Payment-Token: USDC" \
  -H "X-Payment-Signature: $(echo -n '{"prompt":"Hello World","language":"python"}' | sha256sum | cut -d' ' -f1)" \
  -H "X-Wallet-Address: ${WALLET_ADDRESS}" \
  -H "X-API-Key: ${API_KEY}" \
  -d '{
    "prompt": "用 Python 写一个 Hello World 函数",
    "language": "python"
  }'

echo ""
```

---

## 📋 API 端点列表

| 端点 | 功能 | 价格 | 请求参数 | 响应示例 |
|------|------|------|----------|----------|
| `/api/v1/translator` | 翻译服务 | $0.02 | `text`, `source`, `target` | `{translated_text: "..."}` |
| `/api/v1/long-text` | 长文解析 | $0.03 | `text`, `max_length` | `{summary: "..."}` |
| `/api/v1/crawl` | 网络爬虫 | $0.04 | `url`, `selector` | `{content: "..."}` |
| `/api/v1/code-audit` | 代码审计 | $0.05 | `code`, `language` | `{issues: [...], suggestions: [...]}` |
| `/api/v1/logic` | 逻辑推理 | $0.06 | `problem`, `context` | `{analysis: "...", conclusion: "..."}` |
| `/api/v1/code-gen` | 代码生成 | $0.08 | `prompt`, `language` | `{code: "...", explanation: "..."}` |
| `/api/v1/architect` | 架构设计 | $0.10 | `requirements`, `scale` | `{architecture: "...", components: [...]}` |
| `/api/v1/vision` | 视觉解析 | $0.15 | `image_url`, `task` | `{description: "...", objects: [...]}` |

---

## 🔐 认证与支付

### 请求头说明

| 请求头 | 必填 | 说明 | 示例 |
|--------|------|------|------|
| `X-API-Key` | ✅ | API 密钥（合作后获取） | `ak_xxxxxxxxxxxx` |
| `X-Wallet-Address` | ✅ | USDC 钱包地址 | `0x1234...5678` |
| `X-Payment-Amount` | ✅ | 支付金额（6 位小数） | `20000` (= 0.02 USDC) |
| `X-Payment-Token` | ✅ | 支付代币 | `USDC` |
| `X-Payment-Signature` | ✅ | 支付签名 | `sha256 hash` |
| `Content-Type` | ✅ | 内容类型 | `application/json` |

### 签名生成流程

1. **序列化请求数据**
   ```python
   import json
   message = json.dumps(payload, sort_keys=True)
   ```

2. **生成 SHA256 哈希**
   ```python
   import hashlib
   signature = hashlib.sha256(message.encode()).hexdigest()
   ```

3. **（生产环境）用钱包私钥签名**
   ```python
   from web3 import Web3
   w3 = Web3()
   signature = w3.eth.account.sign(message, private_key)
   ```

---

## 📊 响应格式

### 成功响应

```json
{
  "success": true,
  "data": {
    "translated_text": "你好，世界！",
    "source_language": "en",
    "target_language": "zh"
  },
  "cost": "0.02 USDC",
  "transaction_id": "tx_xxxxxxxxxxxx",
  "timestamp": "2026-03-05T14:30:00Z"
}
```

### 错误响应

```json
{
  "success": false,
  "error": {
    "code": "INSUFFICIENT_PAYMENT",
    "message": "支付金额不足，需要 0.02 USDC",
    "required_amount": "20000",
    "provided_amount": "10000"
  },
  "timestamp": "2026-03-05T14:30:00Z"
}
```

### 常见错误码

| 错误码 | HTTP 状态码 | 说明 | 解决方案 |
|--------|-----------|------|----------|
| `INSUFFICIENT_PAYMENT` | 402 | 支付金额不足 | 检查 `X-Payment-Amount` |
| `INVALID_SIGNATURE` | 401 | 签名无效 | 重新生成签名 |
| `INVALID_API_KEY` | 401 | API 密钥无效 | 联系获取正确密钥 |
| `RATE_LIMIT_EXCEEDED` | 429 | 超出频率限制 | 等待后重试（60 次/分钟） |
| `INVALID_PAYLOAD` | 400 | 请求数据格式错误 | 检查请求参数 |
| `SERVICE_UNAVAILABLE` | 503 | 服务暂时不可用 | 稍后重试 |

---

## 💡 最佳实践

### 1. 错误处理

```python
def safe_call_api(endpoint, payload, price):
    """带重试的 API 调用"""
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            result = call_x402_api(endpoint, payload, price)
            return result
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)  # 指数退避
```

### 2. 批量调用

```python
def batch_translate(texts, source='en', target='zh'):
    """批量翻译（节省成本）"""
    results = []
    for text in texts:
        result = call_x402_api(
            '/api/v1/translator',
            {'text': text, 'source': source, 'target': target},
            0.02
        )
        results.append(result['data']['translated_text'])
    return results
```

### 3. 成本监控

```python
class APICostTracker:
    """API 成本追踪器"""
    
    def __init__(self):
        self.total_cost = 0
        self.call_count = 0
    
    def track(self, cost):
        self.total_cost += float(cost.split()[0])
        self.call_count += 1
        print(f"本次花费：${cost}")
        print(f"累计花费：${self.total_cost:.4f} ({self.call_count}次调用)")
```

---

## 🎯 快速集成检查清单

- [ ] 安装 MetaMask 钱包
- [ ] 充值 USDC（Base 网络）
- [ ] 获取 API 密钥（联系合作）
- [ ] 选择编程语言（Python/JS/Go）
- [ ] 复制对应示例代码
- [ ] 替换配置（API_KEY, WALLET_ADDRESS）
- [ ] 测试调用（翻译 API $0.02）
- [ ] 集成到自己的应用
- [ ] 监控成本和错误率

---

## 📞 获取帮助

**遇到问题？**

1. **查看日志：** 检查 API 响应中的错误信息
2. **查看文档：** [API_BEST_PRACTICES.md](API_BEST_PRACTICES.md)
3. **提交 Issue：** [GitHub Issues](https://github.com/ziwei-control/ziwei-archive/issues)
4. **联系合作：** DM 或邮件获取 API 访问权限

**合作联系：**
- GitHub: github.com/ziwei-control/ziwei-archive
- Dashboard: http://8.213.149.224:8091
- 邮箱：contact@x402.network（示例）

---

## 💰 成本计算示例

### 场景 1: 翻译网站

```
假设：每天 1000 次翻译调用
单次成本：$0.02
日成本：1000 × $0.02 = $20
月成本：$20 × 30 = $600

如果向用户收费 $0.05/次：
月收入：1000 × $0.05 × 30 = $1500
月利润：$1500 - $600 = $900
```

### 场景 2: 代码审计服务

```
假设：每天 50 次代码审计
单次成本：$0.05
日成本：50 × $0.05 = $2.5
月成本：$2.5 × 30 = $75

如果向用户收费 $0.15/次：
月收入：50 × $0.15 × 30 = $225
月利润：$225 - $75 = $150
```

### 场景 3: 综合 AI 服务

```
假设混合调用：
- 翻译 500 次 × $0.02 = $10/天
- 代码生成 100 次 × $0.08 = $8/天
- 代码审计 50 次 × $0.05 = $2.5/天
日成本：$20.5
月成本：$615

如果加价 50% 收费：
月收入：$922.5
月利润：$307.5
```

---

**开始构建你的 AI 应用吧！🚀**

---

*有任何问题，欢迎通过 GitHub Issues 或邮件联系我们。*
