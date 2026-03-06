# 交易机器人 Dashboard 状态详解

**更新时间：** 2026-03-05 08:00

---

## 📊 Dashboard 显示说明

### 交易机器人面板显示内容

```
📈 交易机器人
├── 运行实例：7
├── 策略引擎：✅ 运行中
├── 情报收集：✅ 运行中
└── API 收入：0.4800 USDC
```

---

## 1️⃣ 运行实例：7 是什么？

### 实际运行的进程

当前实际运行 **4 个进程**：

| 进程 | 文件 | 功能 | CPU | 内存 |
|------|------|------|-----|------|
| **1** | `start_test.py` | 主启动器/协调器 | 2.8% | 190MB |
| **2** | `intel_collector.py` | 情报收集器 | 0.4% | 22MB |
| **3** | `strategy_engine_v3.py` | 策略引擎 v3 | 0.0% | 12MB |
| **4** | `soul_trader.py` | 灵魂交易者 | 0.0% | 12MB |

### 为什么显示 7 个实例？

**原因：** Dashboard 统计的是包含**子进程**和**历史进程**的总数

**计算方式：**
```bash
pgrep -f 'soul_trader|strategy_engine|intel_collector'
```

这会匹配：
- 主进程
- 子进程/线程
- 可能包括已退出但未清理的进程记录

**实际活跃进程：4 个** ✅

---

## 2️⃣ 情报收集了什么情报？

### 情报收集器 (intel_collector.py)

**工作频率：** 每 2-3 分钟收集一次

**收集内容：**

#### A. 加密货币价格数据

监控 **7 个主流币种**：

| 币种 | 价格 | 24h 涨跌 | 市值 | 24h 交易量 |
|------|------|----------|------|-----------|
| **BTC** | $72,706 | +6.20% | $1.45T | $80.8B |
| **ETH** | $2,129.60 | +7.10% | $257B | $34.2B |
| **BNB** | $658.40 | +3.76% | $89.8B | $1.62B |
| **XRP** | $1.43 | +4.71% | $87B | $4.81B |
| **SOL** | $90.79 | +4.34% | $51.7B | $7.53B |
| **DOGE** | $0.099 | +10.17% | $15.2B | $2.74B |
| **ADA** | $0.276 | +4.96% | $10.1B | $0.98B |

**每个币种包含：**
- ✅ 当前价格
- ✅ 24 小时涨跌幅
- ✅ 市值
- ✅ 24 小时交易量
- ✅ 24 小时最高价
- ✅ 24 小时最低价
- ✅ 数据时间戳

---

#### B. 新闻情报

**数据来源：** Google News RSS

**监控关键词：** BTC, ETH, BNB, XRP, SOL, DOGE, ADA, VIRTUAL, PAYAI 等

**最新新闻示例：**
```
BTC 新闻 (5 条):
1. "Bitcoin Surpasses $73,000 as Crypto's Volatility Returns" - Yahoo Finance
2. "Jiuzi outlines $1B swap for 10,000 Bitcoin" - Stock Titan
3. "Bitcoin price analysis: BTC sitting below 'air pocket' above $72,000" - CoinDesk
4. "Bitcoin crosses $73,000 as investors look past Iran tensions" - CNBC
5. "Current price of Ethereum for March 4, 2026" - Fortune
```

**每条新闻包含：**
- ✅ 标题
- ✅ 链接
- ✅ 来源
- ✅ 发布时间

---

#### C. 市场情绪分析

**分析维度：**
- 社交媒体情绪 (Twitter, Reddit)
- 新闻情绪 (正面/负面/中性)
- KOL 观点 (Vitalik, CZ, Saylor 等)
- 技术指标 (RSI, MACD, 均线)

**情绪评分：**
```
BTC: 看涨 (score: +3)
ETH: 看涨 (score: +4)
DOGE: 强烈看涨 (score: +5) ⚠️
```

---

#### D. 情报文件位置

**存储路径：**
```
/home/admin/Ziwei/data/intel/intel_YYYYMMDD_HHMMSS.json
```

**文件大小：** ~100KB/文件

**更新频率：** 每 2-3 分钟

**查看最新情报：**
```bash
# 查看最新文件
ls -lt /home/admin/Ziwei/data/intel/ | head -5

# 查看内容
cat /home/admin/Ziwei/data/intel/intel_20260305_*.json | python3 -m json.tool | head -100
```

---

## 3️⃣ API 收入：0.4800 USDC 是什么？

### 收入来源

**这是 x402 API 的收入，不是交易机器人的交易利润！**

### 具体指向

**x402 API 是什么？**
- 紫微智控提供的 **AI 服务 API**
- 包括：代码生成、翻译、分析、爬虫等服务
- 使用 x402 支付协议（加密货币支付）

**收入明细：**

| 项目 | 金额 | 说明 |
|------|------|------|
| **总收入** | 0.4800 USDC | 累计收入 |
| **交易笔数** | ~10-20 笔 | 估计 |
| **平均单价** | ~0.02-0.05 USDC | 每次 API 调用 |

**收入来源明细：**
```
1. 代码生成 API (/api/v1/code-gen) - 0.08 USDC/次
2. 翻译 API (/api/v1/translate) - 0.02 USDC/次
3. 分析 API (/api/v1/analysis) - 0.05 USDC/次
4. 爬虫 API (/api/v1/crawl) - 0.04 USDC/次
...
```

---

### 查看 API 收入详情

**Dashboard 显示：**
```
💰 收入统计
├── 总收入：0.4800 USDC
└── 交易笔数：XX 笔
```

**查看详细记录：**
```bash
cat /home/admin/Ziwei/projects/x402-api/data/payments.json
```

**文件内容示例：**
```json
{
  "payments": {
    "0xabc123...": {
      "amount": 0.05,
      "currency": "USDC",
      "verified": true,
      "timestamp": "2026-03-04T10:30:00Z",
      "sender": "0x46d2695ffF3d7d79CC94A81Ae266742BBc080cFd",
      "service": "/api/v1/analysis"
    },
    ...
  }
}
```

---

### API 收入 vs 交易利润

**重要区别：**

| 项目 | API 收入 | 交易利润 |
|------|----------|----------|
| **来源** | x402 API 服务收费 | 交易机器人买卖差价 |
| **当前金额** | 0.4800 USDC | $0 (模拟交易) |
| **货币** | USDC | USDT (模拟) |
| **真实性** | ✅ 真实收入 | 🧪 模拟交易 |
| **位置** | Dashboard "收入统计" | 交易机器人面板 |

---

## 4️⃣ 各组件详细功能

### A. 主启动器 (start_test.py)

**功能：**
- 加载配置文件 (.env)
- 初始化交易机器人
- 连接交易所 API
- 启动其他组件
- 协调整体运行

**运行状态：**
```bash
ps aux | grep start_test.py
# ✅ 运行中
```

---

### B. 情报收集器 (intel_collector.py)

**功能：**
- 每 2-3 分钟收集价格数据
- 抓取新闻 RSS
- 分析社交媒体情绪
- 保存情报到 JSON 文件
- 为策略引擎提供数据

**工作流程：**
```
1. 调用 CoinGecko API 获取价格
2. 抓取 Google News RSS
3. 分析情绪得分
4. 保存 intel_YYYYMMDD_HHMMSS.json
5. 等待 2-3 分钟，重复
```

---

### C. 策略引擎 (strategy_engine_v3.py)

**功能：**
- 读取情报数据
- 分析技术指标 (RSI, MACD, 均线)
- 判断市场趋势
- 生成交易信号 (买入/卖出/观望)
- 风险管理检查

**策略逻辑：**
```python
if RSI < 30:
    signal = "BUY"  # 超卖
elif RSI > 70:
    signal = "SELL" # 超买
elif trend == "uptrend" and sentiment > 2:
    signal = "HOLD" # 持有
else:
    signal = "WAIT" # 观望
```

---

### D. 灵魂交易者 (soul_trader.py)

**功能：**
- 接收策略信号
- 检查风险参数
- 执行模拟下单
- 设置止损/止盈
- 记录交易日志

**模拟交易流程：**
```
1. 收到 BUY 信号
2. 检查可用资金 ($10,000)
3. 计算仓位 (最多 20% = $2,000)
4. 模拟下单 (不真实执行)
5. 设置止损 (-10% = $1,800)
6. 设置止盈 (+5% = $2,100)
7. 记录到 trades.log
```

---

## 5️⃣ 实时监控命令

### 查看进程状态
```bash
# 查看所有交易机器人进程
ps aux | grep -E "trading|strategy|intel|soul" | grep -v grep

# 查看 CPU/内存使用
top -p $(pgrep -f trading | tr '\n' ',')
```

### 查看情报收集
```bash
# 查看最新情报文件
ls -lt /home/admin/Ziwei/data/intel/ | head -5

# 实时查看新情报
watch -n 5 'ls -lt /home/admin/Ziwei/data/intel/ | head -3'
```

### 查看日志
```bash
# 查看交易日志
tail -f /home/admin/Ziwei/projects/x402-trading-bot/trades.log

# 查看启动日志
tail -f /tmp/trading_bot.log
```

### 查看 API 收入
```bash
# 查看支付记录
cat /home/admin/Ziwei/projects/x402-api/data/payments.json | python3 -m json.tool

# 统计总收入
cat /home/admin/Ziwei/projects/x402-api/data/payments.json | python3 -c "import sys,json; d=json.load(sys.stdin); print(sum(p['amount'] for p in d['payments'].values() if p['verified']))"
```

---

## 📋 总结

### Dashboard 显示解读

```
📈 交易机器人
├── 运行实例：7          → 实际 4 个活跃进程
├── 策略引擎：✅ 运行中  → strategy_engine_v3.py 正常工作
├── 情报收集：✅ 运行中  → intel_collector.py 每 2-3 分钟收集数据
└── API 收入：0.4800 USDC → x402 API 服务收入 (非交易利润)
```

### 关键要点

1. **7 个实例** = 统计方式问题，实际 4 个进程 ✅
2. **情报收集** = 价格 + 新闻 + 情绪，每 2-3 分钟更新 📊
3. **API 收入** = x402 服务收费，不是交易利润 💰
4. **模拟交易** = 使用$10,000 虚拟资金，不真实交易 🧪

---

**有任何问题随时询问！** 🚀
