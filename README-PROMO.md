# 🚀 紫微智控 x402 API - 现已开放！

[![Status](https://img.shields.io/badge/status-online-green)](http://8.213.149.224/health)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![Payment](https://img.shields.io/badge/payment-USDC-yellow)](https://basescan.org/address/0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb)

**让 AI 智能体自主付费，开启机器经济时代！**

---

## 🌟 特性

- ✅ **8 个 AI Agent 端点** - 代码审计、翻译、架构设计等
- ✅ **x402 支付协议** - 自动支付，无需人工干预
- ✅ **USDC 支付** - 稳定币，全球通用
- ✅ **Base 链** - 低 Gas 费，快速确认
- ✅ **自动验证** - 支付后立即可用
- ✅ **24/7 服务** - 全年无休

---

## 💰 API 价格

| 端点 | 功能 | 价格 (USDC) | 约等于 |
|------|------|------------|--------|
| `POST /api/v1/code-audit` | 代码审计 | 0.05 | ¥0.36 |
| `POST /api/v1/translate` | 翻译 | 0.02 | ¥0.14 |
| `POST /api/v1/architect` | 架构设计 | 0.10 | ¥0.71 |
| `POST /api/v1/code-gen` | 代码生成 | 0.08 | ¥0.57 |
| `POST /api/v1/logic` | 逻辑推理 | 0.06 | ¥0.43 |
| `POST /api/v1/long-text` | 长文解析 | 0.03 | ¥0.21 |
| `POST /api/v1/crawl` | 网络爬虫 | 0.04 | ¥0.28 |
| `POST /api/v1/vision` | 视觉解析 | 0.15 | ¥1.07 |

**免费额度**: 前 10 次免费测试！

---

## 🚀 快速开始

### 步骤 1: 测试 API

```bash
# 健康检查
curl http://8.213.149.224/health
```

### 步骤 2: 调用 API（首次获取支付信息）

```bash
curl -X POST http://8.213.149.224/api/v1/code-audit \
  -H "Content-Type: application/json" \
  -d '{"code": "def hello(): pass", "language": "Python"}'
```

响应 (HTTP 402):
```json
{
  "x402": {
    "amount": "0.05",
    "currency": "USDC",
    "wallet": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
    "network": "base"
  },
  "request_id": "abc123..."
}
```

### 步骤 3: 支付 USDC

使用钱包发送 **0.05 USDC** 到：
```
地址：0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb
网络：Base (L2)
```

### 步骤 4: 重发请求（带支付证明）

```bash
# 创建支付证明
PROOF=$(echo '{"tx_hash": "0x...", "amount": "0.05", "sender": "0x...", "recipient": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"}' | base64 -w 0)

# 重发请求
curl -X POST http://8.213.149.224/api/v1/code-audit \
  -H "Content-Type: application/json" \
  -H "x-payment-proof: $PROOF" \
  -d '{"code": "def hello(): pass", "language": "Python"}'
```

### 步骤 5: 获取结果

```json
{
  "success": true,
  "result": "代码审计报告...",
  "cost": 0.05,
  "payment": {"tx_hash": "0x..."}
}
```

---

## 💼 准备钱包

### 推荐钱包

1. **MetaMask** (浏览器插件)
   - 下载：https://metamask.io
   - 添加 Base 网络

2. **Coinbase Wallet** (手机 App)
   - 支持 Base 链
   - 易于使用

### 配置 Base 网络

```
Network Name: Base Mainnet
RPC URL: https://mainnet.base.org
Chain ID: 8453
Currency Symbol: ETH
```

### 获取 USDC

1. 从交易所提现到 Base 链
2. 使用跨链桥：https://bridge.base.org
3. 在 Base DEX 购买

---

## 📊 查看收入

### 钱包地址

```
0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb
```

### 区块链浏览器

https://basescan.org/address/0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb

---

## 📚 文档

- [完整支付指南](projects/x402-api/X402_PAYMENT_GUIDE.md)
- [部署指南](projects/x402-api/DEPLOYMENT_TO_PUBLIC.md)
- [收费方案](projects/x402-api/MONETIZATION_GUIDE.md)
- [API 参考](projects/x402-api/docs/api-reference.md)

---

## 🎯 使用场景

### 开发者

```
- 代码审计：快速发现安全问题
- 代码生成：加速开发流程
- 架构设计：获取专业建议
```

### 企业

```
- 批量代码审计
- 自动化文档翻译
- 智能客服集成
```

### AI 智能体

```
- 自主付费调用 API
- 机器间微支付
- 自动化工作流
```

---

## 💡 为什么选择我们？

| 特性 | 我们 | 其他 |
|------|------|------|
| 支付自动化 | ✅ | ❌ |
| 加密货币支付 | ✅ | ❌ |
| 低费用 | ✅ USDC | ❌ 法币手续费高 |
| 全球可用 | ✅ | ❌ 地区限制 |
| 24/7 服务 | ✅ | ⏳ 工作时间 |
| 免费额度 | ✅ 10 次/天 | ❌ 无 |

---

## 📞 支持

- 📧 Email: pandac00@163.com
- 🐛 Issues: [GitHub Issues](https://github.com/ziwei-control/ziwei-archive/issues)
- 📚 文档：[完整文档](projects/x402-api/X402_PAYMENT_GUIDE.md)

---

## 📈 路线图

### 2026 Q1
- [x] x402 支付集成
- [x] 公网部署
- [ ] CodeCanyon SDK 上架
- [ ] 批量支付支持

### 2026 Q2
- [ ] 用户管理系统
- [ ] 订阅制收费
- [ ] 更多 AI 模型
- [ ] API 网关优化

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

## 🌟 统计

![Stars](https://img.shields.io/github/stars/ziwei-control/ziwei-archive?style=social)
![Forks](https://img.shields.io/github/forks/ziwei-control/ziwei-archive?style=social)
![Issues](https://img.shields.io/github/issues/ziwei-control/ziwei-archive)

---

**准备好开始使用了吗？** 🚀

立即测试：http://8.213.149.224/health

---

**让 AI 智能体自主付费，开启机器经济时代！** 🤖💰
