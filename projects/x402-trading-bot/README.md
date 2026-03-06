# x402 交易机器人 - 系统记忆文档

**版本：** v1.0  
**更新时间：** 2026-03-05  
**状态：** 🟡 模拟交易测试中

---

## 🎯 核心功能

### 监控范围
**交易机器人监控加密市场排名前 100 的加密货币**

- ✅ 实时监控 CoinMarketCap 前 100 名币种
- ✅ 自动分析价格、成交量、市值变化
- ✅ 策略交易：基于技术指标和市场情绪
- ✅ 动态调整监控列表（根据市值排名）

---

## 📊 监控币种分类

### A 类：主流币种（前 10 名）
```
BTC  - Bitcoin
ETH  - Ethereum
BNB  - Binance Coin
XRP  - Ripple
SOL  - Solana
ADA  - Cardano
DOGE - Dogecoin
TRX  - Tron
LINK - Chainlink
MATIC - Polygon
```

**策略：** 重点监控，大资金流向，市场风向标

---

### B 类：潜力币种（11-50 名）
```
DOT   - Polkadot
AVAX  - Avalanche
SHIB  - Shiba Inu
LTC   - Litecoin
UNI   - Uniswap
ATOM  - Cosmos
XMR   - Monero
ETC   - Ethereum Classic
BCH   - Bitcoin Cash
...等 40 个币种
```

**策略：** 寻找增长机会，中等仓位配置

---

### C 类：小市值币种（51-100 名）
```
前 100 名中的其他币种
```

**策略：** 高风险高回报，小仓位试探

---

### D 类：x402 生态代币（特别关注）
```
VIRTUAL - x402 生态
PAYAI   - x402 生态
PING    - x402 生态
```

**策略：** 重点关注，长期持有

---

## 🤖 策略分析维度

### 1️⃣ 技术指标分析

**RSI（相对强弱指数）**
```python
if RSI < 30:
    signal = "BUY"   # 超卖，可能反弹
elif RSI > 70:
    signal = "SELL"  # 超买，可能回调
else:
    signal = "HOLD"  # 中性
```

**MACD（移动平均收敛散度）**
```python
if MACD_line > Signal_line:
    trend = "上涨"
elif MACD_line < Signal_line:
    trend = "下跌"
```

**均线系统**
```python
MA20 > MA50 > MA200  # 多头排列，看涨
MA20 < MA50 < MA200  # 空头排列，看跌
```

**成交量分析**
```python
if 成交量 > 均量 * 2:
    异常放量，关注突破
```

---

### 2️⃣ 市场情绪分析

**数据来源：**
- Twitter 提及量
- Reddit 讨论热度
- Google 搜索指数
- 新闻情绪评分
- KOL 观点汇总

**情绪评分：**
```
+5: 极度看涨
+3: 看涨
 0: 中性
-3: 看跌
-5: 极度看跌
```

---

### 3️⃣ 风险评估

**波动率监控：**
```python
if 24h 波动率 > 20%:
    高风险，降低仓位
elif 24h 波动率 > 10%:
    中等风险，正常仓位
else:
    低风险，可加仓
```

**相关性分析：**
```python
# 避免持仓高度相关的币种
if BTC_相关性 > 0.8:
    分散投资，降低单一风险
```

---

## 💰 资金管理

### 模拟资金配置
```
初始资金：$10,000 USDT（虚拟）
测试模式：true
模拟下单：true
```

### 仓位管理
```
单币种最大仓位：20% ($2,000)
总仓位上限：80% ($8,000)
保留现金：20% ($2,000)
```

### 风险控制
```
止损：-10%（单笔最大亏损）
止盈：+5%（单笔最小盈利）
最大回撤：-15%（总资金）
```

---

## 📋 运行流程

### 情报收集（每 2-3 分钟）
```
1. 调用 CoinGecko API 获取前 100 币种价格
2. 抓取 Google News RSS 获取相关新闻
3. 分析社交媒体情绪
4. 计算技术指标（RSI, MACD, 均线）
5. 保存情报到 intel_YYYYMMDD_HHMMSS.json
```

### 策略分析（每 5 分钟）
```
1. 读取最新情报数据
2. 筛选符合条件的币种（RSI < 30 或 > 70）
3. 分析市场情绪
4. 生成交易信号（BUY/SELL/HOLD）
5. 风险评估
```

### 交易执行（当信号触发时）
```
1. 接收策略信号
2. 检查可用资金
3. 计算仓位大小
4. 模拟下单（测试模式）
5. 设置止损/止盈
6. 记录交易日志
```

---

## 📊 监控币种列表（前 100 名）

### 实时更新
**数据来源：** CoinMarketCap API

**获取命令：**
```bash
curl -s "https://api.coinmarketcap.com/data-api/v3/cryptocurrency/listing?start=1&limit=100" | python3 -m json.tool
```

**本地缓存：**
```
/home/admin/Ziwei/data/crypto/top100.json
```

---

## 🔧 配置文件

### .env 配置
```bash
# 交易所配置
EXCHANGE=binance
API_KEY=your_api_key
API_SECRET=your_api_secret

# 测试配置
TEST_MODE=true          # 测试模式：不下真实订单
DRY_RUN=true            # 模拟运行：不真实交易
INITIAL_BALANCE=10000   # $10,000 USDT 模拟启动资金

# 风险控制
MAX_POSITION_SIZE=0.2   # 最大仓位 20%
STOP_LOSS=-0.10         # 止损 -10%
TAKE_PROFIT=0.05        # 止盈 +5%
MAX_DRAWDOWN=-0.15      # 最大回撤 -15%

# 监控配置
MONITOR_TOP=100         # 监控前 100 名币种
UPDATE_INTERVAL=5       # 价格更新间隔（秒）
CHECK_INTERVAL=60       # 风险检查间隔（秒）
```

---

## 📈 日志位置

**交易日志：**
```
/home/admin/Ziwei/projects/x402-trading-bot/trades.log
```

**情报数据：**
```
/home/admin/Ziwei/data/intel/intel_YYYYMMDD_HHMMSS.json
```

**每日报告：**
```
/home/admin/Ziwei/projects/x402-trading-bot/daily_report_YYYY-MM-DD.json
```

**系统日志：**
```
/tmp/trading_bot.log
```

---

## 🎯 关键指标

### 性能指标
- 监控币种数：100 个
- 情报更新频率：每 2-3 分钟
- 策略分析频率：每 5 分钟
- 交易日志：实时记录

### 风险指标
- 单币种最大亏损：10%
- 总资金最大回撤：15%
- 最大仓位：80%
- 最小现金保留：20%

---

## 📞 快速命令

### 查看状态
```bash
# 查看进程
ps aux | grep -E "trading|strategy|intel|soul" | grep -v grep

# 查看最新情报
ls -lt /home/admin/Ziwei/data/intel/ | head -5

# 查看交易日志
tail -f /home/admin/Ziwei/projects/x402-trading-bot/trades.log
```

### 重启机器人
```bash
# 停止
pkill -f trading

# 启动
cd /home/admin/Ziwei/projects/x402-trading-bot
nohup python3 start_test.py > /tmp/trading_bot.log 2>&1 &
```

### 查看监控币种
```bash
# 查看前 100 名列表
cat /home/admin/Ziwei/data/crypto/top100.json | python3 -m json.tool | head -50
```

---

## 📖 相关文档

| 文档 | 位置 |
|------|------|
| 系统记忆 | `/root/.openclaw/workspace/memory/2026-03-05.md` |
| 状态说明 | `/home/admin/Ziwei/projects/x402-trading-bot/STATUS_EXPLANATION.md` |
| 收入配置 | `/home/admin/Ziwei/projects/x402-trading-bot/REAL_INCOME_SETUP.md` |
| 使用指南 | `/root/.openclaw/workspace/TERMINAL_GUIDE.md` |

---

## ⚠️ 重要提示

### 模拟交易说明
- ✅ 当前为模拟交易模式
- ✅ 不会动用真实资金
- ✅ 所有交易都是虚拟的
- ✅ 用于测试策略有效性

### 真实交易切换
如需切换到真实交易：
```bash
# 修改 .env
TEST_MODE=false
DRY_RUN=false

# 重启机器人
pkill -f trading
python3 start_test.py
```

**⚠️ 风险提示：** 真实交易有风险，投资需谨慎！

---

**文档版本：** v1.0  
**最后更新：** 2026-03-05 08:00  
**维护者：** 紫微智控 AI Assistant  
**状态：** ✅ 已固化到系统记忆
