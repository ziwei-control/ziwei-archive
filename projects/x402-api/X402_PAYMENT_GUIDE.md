# 💰 x402 支付协议集成指南

## 📋 当前状态

```
✅ x402 支付网关已集成
✅ HTTP 402 响应已实现
✅ 支付验证逻辑已实现
✅ USDC 钱包地址已配置
⏳ 需要配置 Base 链 RPC
⏳ 需要测试真实支付
```

---

## 🎯 x402 支付流程

### 工作流程

```
1. 用户调用 API (无支付)
   ↓
2. API 返回 HTTP 402 + 支付信息
   {
     "x402": {
       "amount": "0.05",
       "currency": "USDC",
       "wallet": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
       "network": "base"
     }
   }
   ↓
3. 用户使用钱包支付 USDC (Base 链)
   ↓
4. 用户获取交易哈希 (tx_hash)
   ↓
5. 用户重发请求 + 支付证明
   Headers: x-payment-proof: base64({tx_hash, amount, sender, ...})
   ↓
6. API 验证支付
   ↓
7. 返回 API 结果
```

---

## 💼 配置信息

### USDC 收款钱包

```
地址：0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb
网络：Base (L2)
代币：USDC (ERC-20)
合约地址：0x833589fCD6eDb6E08f4c7C32D4f71b54bA02929
```

### API 价格

| 端点 | 价格 (USDC) |
|------|------------|
| /api/v1/architect | 0.10 |
| /api/v1/code-gen | 0.08 |
| /api/v1/code-audit | 0.05 |
| /api/v1/logic | 0.06 |
| /api/v1/translate | 0.02 |
| /api/v1/long-text | 0.03 |
| /api/v1/crawl | 0.04 |
| /api/v1/vision | 0.15 |

---

## 🔧 用户如何使用

### 步骤 1: 准备钱包

```
推荐钱包:
- MetaMask (浏览器插件)
- Coinbase Wallet
- Rainbow

配置 Base 网络:
1. 打开 MetaMask
2. 添加网络 → Base Mainnet
3. RPC: https://mainnet.base.org
4. Chain ID: 8453
```

### 步骤 2: 获取 USDC

```
方法:
1. 从交易所提现 USDC 到 Base 链
2. 使用跨链桥 (https://bridge.base.org)
3. 在 Base 链 DEX 购买
```

### 步骤 3: 调用 API

#### 第一次请求（获取支付信息）

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
  "request_id": "abc123...",
  "timestamp": "2026-03-03T17:45:00"
}
```

#### 步骤 4: 支付 USDC

使用钱包发送 USDC：
```
收款地址：0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb
金额：0.05 USDC
网络：Base
```

获取交易哈希：`0x...`

#### 步骤 5: 重发请求（带支付证明）

```bash
# 创建支付证明
PROOF=$(echo '{"tx_hash": "0x...", "amount": "0.05", "sender": "0x...", "recipient": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb", "timestamp": "2026-03-03T17:45:00"}' | base64)

# 重发请求
curl -X POST http://8.213.149.224/api/v1/code-audit \
  -H "Content-Type: application/json" \
  -H "x-payment-proof: $PROOF" \
  -d '{"code": "def hello(): pass", "language": "Python"}'
```

#### 步骤 6: 获取结果

```json
{
  "success": true,
  "result": "代码审计报告...",
  "agent": "code-audit",
  "cost": 0.05,
  "payment": {
    "tx_hash": "0x...",
    "amount": 0.05
  }
}
```

---

## 🧪 测试支付

### 测试环境

```
测试网：Base Sepolia
测试 USDC: 从水龙头获取
测试钱包：创建新地址
```

### 测试步骤

```bash
# 1. 测试健康检查
curl http://localhost/health

# 2. 测试 API 调用（无支付）
curl -X POST http://8.213.149.224/api/v1/code-audit \
  -H "Content-Type: application/json" \
  -d '{"code": "def test(): pass", "language": "Python"}'

# 应该返回 HTTP 402 + 支付信息
```

---

## 📊 查看收入

### 查看钱包余额

```
区块链浏览器：https://basescan.org
地址：0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb
```

### 查看支付记录

```bash
cat /home/admin/Ziwei/projects/x402-api/data/payments.json
```

### 查看统计

```bash
curl http://8.213.149.224/api/v1/stats
```

---

## 💰 提现 USDC

### 方法 1: 持有 USDC

```
优点:
✅ 稳定币，保值
✅ 随时可以使用
✅ 用于支付其他服务
```

### 方法 2: 兑换法币

```
步骤:
1. 跨链到 Ethereum 主网
2. 发送到交易所 (Binance/Coinbase)
3. 卖出为 USDT/法币
4. 提现到银行卡
```

### 方法 3: 直接使用

```
支持 USDC 支付的服务:
- 服务器费用
- 域名费用
- 其他 API 服务
```

---

## ⚠️ 注意事项

### 安全

```
✅ 私钥不要泄露
✅ 使用硬件钱包存储大额
✅ 定期提现到冷钱包
✅ 监控钱包活动
```

### 税务

```
⚠️ 加密货币收入可能需要报税
⚠️ 保留交易记录
⚠️ 咨询税务顾问
```

### 合规

```
⚠️ 了解当地加密货币法规
⚠️ 可能需要 KYC/AML
⚠️ 某些国家/地区可能受限
```

---

## 🎯 下一步

### 立即可做

```
1. 测试支付流程
2. 准备 USDC 钱包
3. 在 README 添加支付说明
4. 开始推广
```

### 本周可做

```
1. 创建使用文档
2. 录制教程视频
3. 发布到开发者社区
4. 获取第一批用户
```

### 本月可做

```
1. 优化支付体验
2. 添加批量支付
3. 集成更多支付方式
4. 规模化推广
```

---

## 📞 技术支持

### 常见问题

**Q: 支付后没收到结果？**
```
检查:
1. 交易是否确认 (basescan.org)
2. 支付证明格式是否正确
3. 交易哈希是否重复使用
```

**Q: 如何退款？**
```
加密货币支付不可逆
建议:
1. 提供免费额度测试
2. 明确服务说明
3. 建立客服渠道
```

**Q: 如何查看收入？**
```
1. basescan.org 查看钱包
2. payments.json 查看记录
3. /api/v1/stats 查看统计
```

---

**准备好开始收款了吗？** 💰
