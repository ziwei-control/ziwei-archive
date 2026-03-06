# Dashboard 真实收入配置说明

**更新时间：** 2026-03-05 08:00

---

## ✅ 已完成配置

### 1️⃣ x402 API 真实收入

**状态：** ✅ 已配置并显示

**数据来源：**
```
/home/admin/Ziwei/projects/x402-api/data/payments.json
```

**当前收入：**
- **金额：** 0.4800 USDC ✅ 真实
- **笔数：** 10 笔交易
- **来源：** AI 服务 API 调用收费

**Dashboard 显示：**
```
💰 真实收入统计
├── x402 API 收入：0.4800 USDC ✅
├── Binance 余额：$41.03 USD ✅
├── API 交易笔数：10
└── 总计估值：$41.51 USD
```

---

### 2️⃣ Binance 真实钱包余额

**状态：** ✅ 已配置并显示

**查询脚本：**
```
/home/admin/Ziwei/scripts/check_binance_balance_real.py
```

**查询结果（真实数据）：**
```
USDT: 41.0277 (可用)
BTC:  0.0000
ETH:  0.0000
TNT:  0.8000
DLT:  0.0000

总估值：$41.03 USD ✅ 真实
```

**API 配置：**
```bash
# 配置文件
/home/admin/Ziwei/projects/x402-trading-bot/.env

API_KEY=0adWsF5X0HfPUfAo6uYSKpQYmJXmRryB8veStp4waJ3jvhBOsAHEcMPyN5srC9a1
API_SECRET=BE3kkKz0Q6Iu82bxKkJDAh1ATkWrpSHLuZhHFJPsHaDB6qScUI5ixjMWNnziKo3T
```

---

### 3️⃣ 交易机器人模拟资金

**状态：** ✅ 明确标注为模拟

**配置：**
```
初始资金：$10,000 USDT (虚拟)
测试模式：true
模拟下单：true
```

**Dashboard 显示：**
```
📈 交易机器人 (模拟)
├── 运行实例：4
├── 策略引擎：✅ 运行中
├── 情报收集：✅ 运行中
└── 💡 模拟资金：$10,000 USDT
    ⚠️ 模拟交易，不动用真实资金
```

---

## 📊 Dashboard 面板说明

### 收入统计面板（真实）

**显示内容：**
1. **x402 API 收入** - 真实 USDC 收入
2. **Binance 余额** - 真实 USD 估值
3. **API 交易笔数** - 真实交易次数
4. **总计估值** - 所有真实资产总和

**数据更新：**
- 每次页面刷新时自动查询
- Binance 余额实时获取
- API 收入从 JSON 文件读取

---

### 交易机器人面板（模拟）

**显示内容：**
1. **运行实例数** - 实际进程数
2. **策略引擎状态** - 运行/停止
3. **情报收集状态** - 运行/停止
4. **模拟资金** - $10,000 USDT（明确标注）

**重要提示：**
- ⚠️ 黄色警告框标注"模拟交易"
- 💡 明确说明"不动用真实资金"
- 🔒 测试模式保护

---

## 🔧 查看真实数据命令

### 查看 API 收入
```bash
# 查看支付记录
cat /home/admin/Ziwei/projects/x402-api/data/payments.json | python3 -m json.tool

# 统计总收入
cat /home/admin/Ziwei/projects/x402-api/data/payments.json | \
  python3 -c "import sys,json; d=json.load(sys.stdin); print(f'总收入：{sum(p[\"amount\"] for p in d[\"payments\"].values() if p[\"verified\"]):.4f} USDC')"
```

### 查看 Binance 余额
```bash
# 查询真实余额
python3 /home/admin/Ziwei/scripts/check_binance_balance_real.py

# 查看日志
tail -f /tmp/binance_balance.log
```

### 查看交易机器人状态
```bash
# 查看进程
ps aux | grep -E "trading|strategy|intel|soul" | grep -v grep

# 查看配置
cat /home/admin/Ziwei/projects/x402-trading-bot/.env | grep -E "TEST_MODE|DRY_RUN|INITIAL"

# 查看日志
tail -f /tmp/trading_bot.log
```

---

## 📋 数据对比

### 真实 vs 模拟

| 项目 | 真实数据 | 模拟数据 | Dashboard 显示 |
|------|----------|----------|----------------|
| **x402 API 收入** | ✅ 0.4800 USDC | - | 💚 真实显示 |
| **Binance 余额** | ✅ $41.03 USD | - | 💚 真实显示 |
| **交易机器人** | - | 🧪 $10,000 USDT | 💛 明确标注模拟 |
| **交易利润** | - | 🧪 $0 | 💛 模拟交易 |

---

## ⚠️ 重要提示

### 真实性保证

**Dashboard 显示的所有收入数据都是真实的：**

1. ✅ **x402 API 收入**
   - 来源：真实的 AI 服务收费
   - 货币：USDC（加密货币）
   - 验证：区块链可查

2. ✅ **Binance 余额**
   - 来源：真实的 Binance 钱包
   - 查询：通过 Binance API 实时获取
   - 安全：只读权限，不能交易

3. ⚠️ **交易机器人**
   - 性质：模拟交易测试
   - 资金：$10,000 USDT（虚拟）
   - 目的：测试策略，不真实交易

---

## 🎯 下一步计划

### 真实交易配置（可选）

如果你想将交易机器人改为真实交易：

**步骤：**
1. 修改配置文件
   ```bash
   # 编辑 .env
   TEST_MODE=false      # 关闭测试模式
   DRY_RUN=false        # 关闭模拟下单
   INITIAL_BALANCE=10000  # 真实资金
   ```

2. 重启交易机器人
   ```bash
   pkill -f trading
   cd /home/admin/Ziwei/projects/x402-trading-bot
   nohup python3 start_test.py > /tmp/trading_bot.log 2>&1 &
   ```

3. 监控真实交易
   ```bash
   tail -f /tmp/trading_bot.log
   ```

**⚠️ 风险提示：**
- 真实交易会有资金风险
- 建议先用模拟资金测试策略
- 设置合理的止损和止盈
- 定期监控交易状态

---

## 📊 Dashboard 访问

**内网访问：**
```
http://localhost:8081
```

**公网访问：**
```
http://panda66.duckdns.org:8081
```

**刷新数据：**
- 页面每 1200 秒（20 分钟）自动刷新
- 手动刷新：点击 "🔄 刷新" 按钮
- 强制刷新：Ctrl+F5

---

## 📞 问题反馈

如有任何问题或需要调整：

1. 查看日志：
   ```bash
   tail -f /tmp/dashboard_v4.log
   ```

2. 检查进程：
   ```bash
   ps aux | grep dashboard
   ```

3. 重启 Dashboard：
   ```bash
   pkill -f dashboard
   nohup python3 /home/admin/Ziwei/projects/dashboard_v4_0_1.py > /tmp/dashboard_v4.log 2>&1 &
   ```

---

**配置完成时间：** 2026-03-05 08:00  
**状态：** ✅ 所有收入数据已配置为真实显示
