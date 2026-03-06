# x402 API 快速开始指南

**5 分钟开始调用 AI API，按次付费 $0.02 起**

---

## 🎯 三步开始

### 1️⃣ 准备钱包（2 分钟）

1. 安装 [MetaMask](https://metamask.io/)
2. 添加 Base 网络
3. 充值 $10-50 USDC

### 2️⃣ 获取 API 密钥（1 分钟）

联系合作获取：
- API Key
- API 端点地址
- 钱包地址绑定

### 3️⃣ 开始调用（2 分钟）

复制下方代码，替换配置，立即使用！

---

## 💻 代码示例

### Python（最简单）

```python
import requests

# 配置（合作后获取）
API_URL = "http://8.213.149.224:5002/api/v1/translator"
API_KEY = "your_api_key"
WALLET = "your_wallet_address"

# 调用 API
response = requests.post(
    API_URL,
    json={"text": "Hello!", "source": "en", "target": "zh"},
    headers={
        "X-API-Key": API_KEY,
        "X-Wallet-Address": WALLET,
        "X-Payment-Amount": "20000",  # 0.02 USDC
        "X-Payment-Token": "USDC"
    }
)

print(response.json())
# 输出：{"success": true, "data": {"translated_text": "你好！"}, "cost": "0.02 USDC"}
```

### JavaScript

```javascript
const axios = require('axios');

const response = await axios.post(
    'http://8.213.149.224:5002/api/v1/translator',
    { text: 'Hello!', source: 'en', target: 'zh' },
    {
        headers: {
            'X-API-Key': 'your_api_key',
            'X-Wallet-Address': 'your_wallet_address',
            'X-Payment-Amount': '20000',
            'X-Payment-Token': 'USDC'
        }
    }
);

console.log(response.data);
```

### cURL（命令行）

```bash
curl -X POST http://8.213.149.224:5002/api/v1/translator \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key" \
  -H "X-Wallet-Address: your_wallet_address" \
  -H "X-Payment-Amount: 20000" \
  -H "X-Payment-Token: USDC" \
  -d '{"text":"Hello!","source":"en","target":"zh"}'
```

---

## 📋 API 列表

| API | 价格 | 用途 |
|-----|------|------|
| 翻译 | $0.02 | 多语言翻译 |
| 长文解析 | $0.03 | 文档摘要 |
| 网络爬虫 | $0.04 | 数据抓取 |
| 代码审计 | $0.05 | 安全检查 |
| 逻辑推理 | $0.06 | 复杂分析 |
| 代码生成 | $0.08 | 快速开发 |
| 架构设计 | $0.10 | 技术方案 |
| 视觉解析 | $0.15 | 图片分析 |

---

## 💰 成本示例

**场景：翻译网站**
- 向用户收费：$0.05/次
- x402 成本：$0.02/次
- 利润：$0.03/次

**1000 次调用 = $30 利润** 💰

---

## ❓ 常见问题

**Q: 如何获取 API 密钥？**  
A: 联系合作，DM 或邮件获取。

**Q: 支持哪些支付方式？**  
A: 目前仅支持 USDC（Base 网络）。

**Q: 有调用限制吗？**  
A: 每 IP 每分钟 60 次，企业可定制。

**Q: 可以退款吗？**  
A: 区块链支付不可逆，但 API 问题会补偿。

---

## 📞 联系合作

- **GitHub:** github.com/ziwei-control/ziwei-archive
- **Dashboard:** http://8.213.149.224:8081
- **完整文档:** [CUSTOMER_API_GUIDE.md](CUSTOMER_API_GUIDE.md)

---

**开始赚钱吧！🚀**
