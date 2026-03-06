# 🌍 全球战情室 - 新闻市场影响分析系统

**紫微智控智能智慧系统**

---

## 🎯 功能概述

通过 AI 智能分析时效新闻保管库中的新闻，预测对加密市场具体币种的价格影响，**准确到具体数字**。

---

## 🤖 核心能力

### 1️⃣ 新闻情感分析

**分析维度：**
- 情感得分：-5 到 5（负数为利空，正数为利好）
- 置信度：0-1（越高越可靠）
- 影响程度：7 个等级

**影响程度分类：**
```
极大利好 (extremely_positive)    → +15%
重大利好 (very_positive)         → +8%
利好 (positive)                  → +3%
中性 (neutral)                   → 0%
利空 (negative)                  → -3%
重大利空 (very_negative)         → -8%
极大利空 (extremely_negative)    → -15%
```

### 2️⃣ 价格预测（准确到具体数字）

**预测内容：**
- 当前价格：实时获取（美元）
- 预测价格：准确到小数点后 2 位
- 变化幅度：百分比（如 +3.50%）
- 支撑位：具体价格（美元）
- 阻力位：具体价格（美元）

**示例：**
```
币种：BTC
当前价格：$72,706.00
预测价格：$83,611.90
变化幅度：+15.00%
支撑位：$69,070.70
阻力位：$87,792.50
```

### 3️⃣ 监控币种

**20+ 主流币种：**
```
BTC, ETH, BNB, XRP, SOL, ADA, DOGE, TRX, AVAX, LINK,
MATIC, TON, SHIB, LTC, BCH, UNI, ATOM, DOT, USDT, USDC
```

---

## 🔧 使用命令

### 1️⃣ 分析新闻市场影响

```bash
python3 /home/admin/Ziwei/scripts/news_market_analyzer.py analyze
```

**输出示例：**
```
======================================================================
🌍 全球战情室 - 新闻市场影响分析系统
🤖 紫微智控智能智慧系统
======================================================================

📊 分析新闻市场影响...
✅ 分析完成
   分析新闻：150 条
   看涨币种：5
   看跌币种：4
   中性币种：6
   报告文件：/home/admin/Ziwei/data/warroom/analysis/reports/market_report_20260305_113136.json
```

### 2️⃣ 获取 Dashboard 数据

```bash
python3 /home/admin/Ziwei/scripts/news_market_analyzer.py dashboard
```

**输出：** JSON 格式数据（用于 Dashboard 显示）

### 3️⃣ 预测特定币种

```bash
python3 /home/admin/Ziwei/scripts/news_market_analyzer.py predict BTC
```

**输出示例：**
```
🔮 预测 BTC 价格走势...
币种：BTC
交易对：BTC/USDT
情感得分：3.50
影响程度：very_positive
当前价格：$72,706.00
预测价格：$83,611.90
变化幅度：+15.00%
支撑位：$69,070.70
阻力位：$87,792.50
置信度：high
```

### 4️⃣ 生成 Dashboard HTML

```bash
python3 /home/admin/Ziwei/scripts/get_market_analysis_dashboard.py
```

**输出：** HTML 代码（直接嵌入 Dashboard）

---

## 📊 Dashboard 显示

### 面板布局

**全球战情室 - 市场影响分析**

```
┌────────────────────────────────────────────────────────────┐
│  📈 看涨    📉 看跌    ➖ 中性    📰 分析新闻               │
│    5          4          6          150                    │
└────────────────────────────────────────────────────────────┘

🔮 价格预测（按影响程度排序）
┌──────┬────────┬──────────┬──────────┬────────┬─────────┬───────┐
│ 币种  │ 情感得分│ 当前价格  │ 预测价格  │ 变化   │ 影响    │ 置信度│
├──────┼────────┼──────────┼──────────┼────────┼─────────┼───────┤
│ SOL  │ +2.00  │ $89.92   │ $92.62   │ +3.00% │ Positive│ Medium│
│ BTC  │ -1.00  │ $72,706  │ $70,525  │ -3.00% │ Negative│ Medium│
│ ...  │ ...    │ ...      │ ...      │ ...    │ ...     │ ...   │
└──────┴────────┴──────────┴──────────┴────────┴─────────┴───────┘

💡 投资建议
🟢 BUY SOL/USDT - 新闻情感积极 (得分：2.00)
   目标：$92.62  置信度：Medium

🔴 SELL BTC/USDT - 新闻情感消极 (得分：-1.00)
   目标：$70,525  置信度：Medium
```

---

## 📁 文件位置

| 文件 | 位置 | 说明 |
|------|------|------|
| **分析脚本** | `/home/admin/Ziwei/scripts/news_market_analyzer.py` | 主分析程序 |
| **Dashboard 接口** | `/home/admin/Ziwei/scripts/get_market_analysis_dashboard.py` | Dashboard 数据 |
| **分析报告** | `/home/admin/Ziwei/data/warroom/analysis/reports/` | JSON 报告 |
| **时效新闻** | `/home/admin/Ziwei/data/warroom/temp_news/` | 新闻源 |

---

## 🔄 自动化配置

### 定时任务

**配置文件：** `/etc/cron.d/ziwei_market_analysis`

```cron
# 市场影响分析（每 4 小时执行一次）
0 */4 * * * root /usr/bin/python3 /home/admin/Ziwei/scripts/news_market_analyzer.py analyze >> /tmp/market_analysis.log 2>&1

# Dashboard 数据更新（每小时执行一次）
30 * * * * root /usr/bin/python3 /home/admin/Ziwei/scripts/get_market_analysis_dashboard.py > /home/admin/Ziwei/data/warroom/analysis/dashboard_data.json 2>&1
```

### 日志位置

```
/tmp/market_analysis.log      # 分析日志
/tmp/dashboard_update.log     # Dashboard 更新日志
```

---

## 📋 分析流程

### 1️⃣ 读取新闻
```
从时效新闻保管库读取最新新闻文件
↓
提取各币种的新闻标题和内容
```

### 2️⃣ 情感分析
```
对每篇新闻进行 AI 情感分析
↓
计算情感得分（-5 到 5）
↓
确定影响程度（7 个等级）
```

### 3️⃣ 价格计算
```
获取当前价格（实时）
↓
应用影响权重（如 +15%）
↓
计算预测价格（准确到小数点后 2 位）
↓
计算支撑位和阻力位
```

### 4️⃣ 生成报告
```
汇总所有币种分析结果
↓
生成投资建议（BUY/SELL）
↓
保存 JSON 报告
↓
更新 Dashboard 显示
```

---

## 🎯 实际案例

### 案例 1：BTC 重大利好新闻

**新闻标题：**
```
"Bitcoin Surpasses $73,000 as Institutional Adoption Surges"
```

**分析结果：**
```
情感得分：+4.0
影响程度：very_positive
当前价格：$72,706.00
预测价格：$78,522.48 (+8%)
支撑位：$69,070.70
阻力位：$82,448.60
置信度：high
建议：BUY
```

### 案例 2：ETH 利空新闻

**新闻标题：**
```
"Ethereum Network Faces Congestion Issues, Gas Fees Spike"
```

**分析结果：**
```
情感得分：-3.5
影响程度：very_negative
当前价格：$2,129.60
预测价格：$1,959.23 (-8%)
支撑位：$1,861.27
阻力位：$2,236.08
置信度：high
建议：SELL
```

### 案例 3：SOL 中性新闻

**新闻标题：**
```
"Solana Daily Development Update"
```

**分析结果：**
```
情感得分：+0.5
影响程度：neutral
当前价格：$89.92
预测价格：$89.92 (0%)
支撑位：$88.12
阻力位：$91.72
置信度：low
建议：HOLD
```

---

## ⚠️ 重要说明

### 1️⃣ 预测准确性

**影响因素：**
- 新闻质量（标题是否准确反映内容）
- 新闻时效性（越新的新闻影响越大）
- 市场情绪（整体市场环境影响）
- 其他外部因素（宏观经济、政策等）

**置信度说明：**
- **high**：情感得分绝对值 ≥ 3，预测较可靠
- **medium**：情感得分绝对值 1-3，预测中等可靠
- **low**：情感得分绝对值 < 1，预测仅供参考

### 2️⃣ 风险提示

⚠️ **本系统预测仅供参考，不构成投资建议！**

- 加密货币市场波动性极大
- 新闻影响可能被市场过度反应或反应不足
- 请结合其他分析工具综合判断
- 投资需谨慎，做好风险管理

### 3️⃣ 数据更新

**更新频率：**
- 新闻数据：每小时更新
- 价格数据：实时获取
- 分析报告：每 4 小时生成
- Dashboard：每小时刷新

---

## 📞 维护命令

### 查看分析状态
```bash
python3 /home/admin/Ziwei/scripts/news_market_analyzer.py status
```

### 手动触发分析
```bash
python3 /home/admin/Ziwei/scripts/news_market_analyzer.py analyze
```

### 查看最新报告
```bash
ls -lt /home/admin/Ziwei/data/warroom/analysis/reports/ | head -5
cat /home/admin/Ziwei/data/warroom/analysis/reports/market_report_*.json | python3 -m json.tool | head -50
```

### 查看日志
```bash
tail -f /tmp/market_analysis.log
```

---

## 🌐 Dashboard 集成

**访问地址：**
```
http://panda66.duckdns.org/dashboard
```

**面板位置：**
全球战情室 → 市场影响分析

**显示内容：**
- 📊 市场概览（看涨/看跌/中性币种数量）
- 🔮 价格预测表（准确到具体数字）
- 💡 投资建议（BUY/SELL）
- 🕐 更新时间

---

**文档版本：** v1.0  
**创建时间：** 2026-03-05  
**维护者：** 紫微智控 AI Assistant  
**状态：** ✅ 已启用
