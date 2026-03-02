# 紫微智控 x402 API - 快速开始

## 简介

紫微智控的 8 个 AI Agent 能力现在可以通过 x402 协议访问！

让其他 AI 智能体用 USDC 微付费调用：
- 架构设计、代码生成、代码审计
- 逻辑推理、翻译、长文解析
- 网络爬虫、视觉解析

## 快速开始

### 1. 安装依赖

```bash
pip install flask requests web3
```

### 2. 启动服务

```bash
cd /home/admin/Ziwei/projects/x402-api
python app.py
```

服务运行在: `http://localhost:5000`

### 3. 调用 API

```python
import requests

# 1. 发送请求（无支付）
response = requests.post(
    "http://localhost:5000/api/v1/code-audit",
    json={"code": "def hello(): print('world')"}
)

# 2. 收到 402 支付请求
if response.status_code == 402:
    x402_info = response.json()['x402']
    print(f"需要支付: {x402_info['amount']} USDC")
    print(f"钱包地址: {x402_info['wallet']}")

    # 3. 完成 USDC 支付（使用你的钱包）
    # ... (示例略，使用 ERC-3009)

    # 4. 重发请求 + 支付证明
    response = requests.post(
        "http://localhost:5000/api/v1/code-audit",
        json={"code": "def hello(): print('world')"},
        headers={"x-payment-proof": "base64_encoded_payment"}
    )

# 5. 获取结果
if response.status_code == 200:
    result = response.json()
    print(result['result'])
```

## API 端点

| 端点 | 功能 | 价格 |
|------|------|------|
| `POST /api/v1/architect` | 架构设计 | $0.10 |
| `POST /api/v1/code-gen` | 代码生成 | $0.08 |
| `POST /api/v1/code-audit` | 代码审计 | $0.05 |
| `POST /api/v1/logic` | 逻辑推理 | $0.06 |
| `POST /api/v1/translate` | 跨域翻译 | $0.02 |
| `POST /api/v1/long-text` | 长文解析 | $0.03 |
| `POST /api/v1/crawl` | 网络爬虫 | $0.04 |
| `POST /api/v1/vision` | 视觉解析 | $0.15 |

## 收入计算

```
日调用: 1000 次 × 平均 $0.05 = $50/天
月收入: $1,500/月
年收入: $18,000/年
```

## 支持

- 文档: `/docs/api-reference.md`
- 问题: GitHub Issues
- 联系: Martin (紫微智控)

---

**让 AI 智能体自主付费，开启机器经济时代！**