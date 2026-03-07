# PayPal 集成计划

**目标：** 支持 PayPal 支付，覆盖全球 200+ 国家

**预计时间：** 2-3 天

---

## 【为什么需要 PayPal】

**当前问题：**
- ❌ 只有 USDC 支付（加密货币门槛高）
- ❌ 很多开发者没有加密货币钱包
- ❌ 法币支付更方便

**PayPal 优势：**
- ✅ 200+ 国家可用
- ✅ 10 亿 + 用户
- ✅ 支持信用卡/借记卡/银行转账
- ✅ 用户信任度高

---

## 【技术方案】

### 方案 1：PayPal Checkout（推荐）

**集成方式：**
```python
import paypalrestsdk

# 配置
paypalrestsdk.configure({
    "mode": "sandbox",  # 或 "live"
    "client_id": "YOUR_CLIENT_ID",
    "client_secret": "YOUR_CLIENT_SECRET"
})

# 创建支付
payment = paypalrestsdk.Payment({
    "intent": "sale",
    "payer": {"payment_method": "paypal"},
    "transactions": [{
        "amount": {
            "total": "10.00",
            "currency": "USD"
        },
        "description": "x402 API Credits"
    }],
    "redirect_urls": {
        "return_url": "http://8.213.149.224:8090/return",
        "cancel_url": "http://8.213.149.224:8090/cancel"
    }
})

# 执行支付
if payment.create():
    # 重定向用户到 PayPal
    for link in payment.links:
        if link.rel == "approval_url":
            redirect_url = link.href
```

**流程：**
1. 用户选择"Pay with PayPal"
2. 重定向到 PayPal 支付页面
3. 用户登录并确认支付
4. PayPal 回调我们的服务器
5. 验证支付并添加 API 额度

**预计工作量：** 2 天

---

### 方案 2：Stripe（备选）

**优势：**
- 开发者体验更好
- 文档更完善
- 支持更多支付方式

**劣势：**
- 不支持的国家更多
- 审核更严格

**预计工作量：** 3 天

---

## 【实施步骤】

### 第 1 天：准备

- [ ] 注册 PayPal Business 账号
- [ ] 获取 API 凭证（Client ID + Secret）
- [ ] 安装 PayPal SDK
- [ ] 创建测试环境

### 第 2 天：开发

- [ ] 集成 PayPal Checkout
- [ ] 添加支付回调处理
- [ ] 测试支付流程
- [ ] 添加错误处理

### 第 3 天：上线

- [ ] 切换到生产环境
- [ ] 更新前端支付选项
- [ ] 测试真实支付
- [ ] 监控和修复

---

## 【费用结构】

**PayPal 费率：**
- 国际支付：4.4% + $0.30/笔
- 国内支付：2.9% + $0.30/笔

**成本计算：**
- 用户充值$10
- PayPal 费用：$10 × 4.4% + $0.30 = $0.74
- 我们收到：$9.26
- API 成本：$9.26 × 50% = $4.63
- 毛利：$4.63

**仍然盈利！**

---

## 【前端更新】

**支付选项：**
```
💳 支付方式

[ ] USDC (Base 链) - $0.02/次
    当前汇率：1 USDC = 1 USD
    最低充值：0.1 USDC

[ ] PayPal - $0.025/次
    包含 PayPal 手续费
    最低充值：$5

[ ] 支付宝（即将支持）
```

---

## 【风险与应对】

| 风险 | 概率 | 影响 | 应对 |
|------|------|------|------|
| PayPal 账号被封 | 低 | 高 | 准备备用账号 |
| 欺诈支付 | 中 | 中 | 启用 PayPal 欺诈保护 |
| 退款纠纷 | 中 | 中 | 明确退款政策 |
| 汇率波动 | 低 | 低 | 使用 USD 结算 |

---

## 【时间表】

| 任务 | 开始 | 结束 | 状态 |
|------|------|------|------|
| 注册 PayPal | 2026-03-07 | 2026-03-07 | ⏳ 待开始 |
| 开发集成 | 2026-03-08 | 2026-03-09 | ⏳ 待开始 |
| 测试 | 2026-03-09 | 2026-03-09 | ⏳ 待开始 |
| 上线 | 2026-03-10 | 2026-03-10 | ⏳ 待开始 |

---

**准备状态：** 🟡 文档完成，等待执行
**负责人：** 如意
