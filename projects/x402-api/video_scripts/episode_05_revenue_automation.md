# 视频教程第 5 集：收入自动化与监控

**时长：** 20 分钟  
**难度：** ⭐⭐⭐⭐ 中高级  
**主题：** 自动化运营

---

## 📝 脚本

### 开场（0:00-2:00）

```
[画面：Dashboard 演示]
🎬 收入自动化与监控
第 5 集：构建被动收入系统

[主持人]
欢迎来到最后一集！
这一集我们学习如何建立自动化的收入监控系统。

[演示 Dashboard]
这是一个实时监控面板，显示：
- 今日收入
- 交易记录
- API 调用统计
- 成本分析

所有数据自动更新，无需人工干预。
```

### 收入追踪（2:00-7:00）

```
[屏幕共享：代码演示]
#!/usr/bin/env python3
# x402-daily-revenue.py

import json
from datetime import datetime
from pathlib import Path

def generate_daily_report():
    """生成每日收入报告"""
    today = datetime.now().strftime('%Y-%m-%d')
    transactions_file = Path(f"data/transactions/{today}.json")
    
    if not transactions_file.exists():
        return "今日无交易"
    
    with open(transactions_file) as f:
        transactions = json.load(f)
    
    # 统计
    total_revenue = sum(t['amount'] for t in transactions)
    total_calls = len(transactions)
    avg_order = total_revenue / total_calls if total_calls > 0 else 0
    
    # 按 API 端点统计
    by_endpoint = {}
    for t in transactions:
        endpoint = t['endpoint']
        by_endpoint[endpoint] = by_endpoint.get(endpoint, 0) + t['amount']
    
    # 生成报告
    report = f"""
📊 x402 API 每日收入报告
日期：{today}

💰 总收入：{total_revenue:.4f} USDC
📞 总调用：{total_calls} 次
📈 平均客单：{avg_order:.4f} USDC

📋 按端点统计：
"""
    for endpoint, revenue in sorted(by_endpoint.items(), key=lambda x: -x[1]):
        report += f"  - {endpoint}: {revenue:.4f} USDC\n"
    
    return report

if __name__ == "__main__":
    print(generate_daily_report())
```

### 自动告警（7:00-12:00）

```
[屏幕共享：代码演示]
#!/usr/bin/env python3
# x402-anomaly-detection.py

def detect_anomalies():
    """检测异常交易模式"""
    recent_transactions = get_recent_transactions(hours=1)
    
    alerts = []
    
    # 1. 交易频率突增
    if len(recent_transactions) > 1000:
        alerts.append(f"⚠️ 交易频率异常：{len(recent_transactions)} 次/小时")
    
    # 2. 大额交易
    large_txs = [t for t in recent_transactions if t['amount'] > 10]
    if large_txs:
        alerts.append(f"💰 大额交易：{len(large_txs)} 笔 > $10 USDC")
    
    # 3. 同一 IP 高频调用
    ip_counts = {}
    for t in recent_transactions:
        ip = t['ip']
        ip_counts[ip] = ip_counts.get(ip, 0) + 1
    
    suspicious_ips = [ip for ip, count in ip_counts.items() if count > 100]
    if suspicious_ips:
        alerts.append(f"🚨 可疑 IP：{suspicious_ips}")
    
    # 4. 失败率突增
    failure_rate = calculate_failure_rate()
    if failure_rate > 0.05:
        alerts.append(f"❌ 失败率过高：{failure_rate:.1f}%")
    
    # 发送告警
    if alerts:
        send_alert_email("\n".join(alerts))
        send_telegram_alert("\n".join(alerts))
    
    return alerts
```

### Dashboard 集成（12:00-17:00）

```
[屏幕共享：Dashboard 代码]
def get_income_stats():
    """收入统计 - Dashboard 板块"""
    payments_file = Path("data/payments.json")
    
    with open(payments_file) as f:
        payments = json.load(f).get('payments', {})
    
    api_income = sum(p.get('amount', 0) for p in payments.values())
    
    # 交易记录详情
    tx_rows = ""
    sorted_payments = sorted(payments.values(), key=lambda x: x['timestamp'], reverse=True)
    
    for tx in sorted_payments[:10]:
        tx_hash = tx['tx_hash']
        amount = tx['amount']
        timestamp = tx['timestamp'][:19].replace('T', ' ')
        
        tx_rows += f"""
        <div class="transaction">
            <span>+{amount:.2f} USDC</span>
            <span>{timestamp}</span>
            <a href="https://basescan.org/tx/{tx_hash}">查看 🔗</a>
        </div>
        """
    
    return f"""
    <div class="card">
        <h2>💰 真实收入统计</h2>
        <div class="stats">
            <div class="stat">总收入：{api_income:.4f} USDC</div>
            <div class="stat">交易笔数：{len(payments)}</div>
        </div>
        <div class="transactions">{tx_rows}</div>
    </div>
    """
```

### 财务安全（17:00-19:00）

```
[画面：财务原则]
💰 财务安全原则

✅ 可以做的：
- 送 API 调用次数（成本 $0.0013/次）
- 送 API 额度（用户感知 $0.05/次）
- 收入分成（从真实收入中分）

❌ 不能做的：
- 送现金 USDC（收入无法覆盖前）
- 承诺现金奖励
- 预付奖励

[主持人]
记住：现金流是生命线。
永远不要承诺无法兑现的奖励。
```

### 课程总结（19:00-20:00）

```
[画面：系列回顾]
🎓 课程回顾

第 1 集：x402 API 入门
第 2 集：5 分钟集成
第 3 集：SDK 使用详解
第 4 集：多语言客服系统
第 5 集：收入自动化与监控

[主持人]
恭喜你完成了整个系列！
现在你有了构建 AI 微付费系统的所有知识。

开始构建你的项目吧！

[结束动画]
```

---

## 🎬 拍摄要点

**重点展示：**
- 真实数据演示
- 自动化流程
- 财务安全原则

**情感共鸣：**
- 强调被动收入
- 鼓励立即行动
- 提供持续支持

---

**脚本版本：** v1.0  
**创建时间：** 2026-03-05
