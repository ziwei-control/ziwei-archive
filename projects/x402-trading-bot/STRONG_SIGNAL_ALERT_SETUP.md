# 📧 强信号邮件通知系统

**创建日期：** 2026-03-08  
**状态：** ✅ 已部署（邮件需更新授权码）

---

## 🎯 功能说明

监控系统自动监控策略引擎生成的交易信号，当发现**强信号**时立即通知：

### 信号强度阈值

| 信号类型 | 分数阈值 | 通知级别 |
|---------|---------|---------|
| **STRONG_BUY** | ≥15.0 | 🚨 紧急警报 |
| **BUY** | ≥10.0 | ⚠️ 重要通知 |
| WEAK_BUY | <10.0 | 不通知 |
| HOLD/SELL | 任意 | 不通知 |

---

## 📋 监控脚本

### 1. `strong_signal_alert.py` - 主监控器 ✅

**功能：**
- 每 30 秒检查最新信号
- 发现强信号自动记录到日志
- 避免重复发送（基于时间戳去重）

**启动命令：**
```bash
cd /home/admin/Ziwei/projects/x402-trading-bot
python3 strong_signal_alert.py
```

**后台运行：**
```bash
nohup python3 strong_signal_alert.py > /home/admin/Ziwei/data/logs/soul-trader/strong_signal_alert.out 2>&1 &
```

**日志位置：**
- 警报日志：`/home/admin/Ziwei/data/logs/soul-trader/strong_signal_alerts.log`
- 运行日志：`/home/admin/Ziwei/data/logs/soul-trader/strong_signal_alert.out`

---

### 2. `strong_signal_monitor.py` - 邮件通知 ⏸️

**功能：**
- 监控强信号
- 发送 HTML 格式邮件
- 包含详细信号信息和操作建议

**配置：**
```bash
# 编辑 .env 文件
SENDER_PASSWORD=YOUR_163_SMTP_AUTH_CODE
```

**获取 163 SMTP 授权码：**
1. 登录 163 邮箱 (pandac00@163.com)
2. 设置 → POP3/SMTP/IMAP
3. 开启 SMTP 服务
4. 生成授权码
5. 更新到 `.env` 文件

**启动命令：**
```bash
cd /home/admin/Ziwei/projects/x402-trading-bot
python3 strong_signal_monitor.py
```

---

## 📊 收件人配置

**当前配置：**
- `19922307306@189.cn` (康纳)

**添加收件人：**
编辑 `strong_signal_monitor.py`：
```python
RECEIVERS = [
    "19922307306@189.cn",  # 康纳
    "pandac00@163.com",    # Martin
    # 添加更多收件人...
]
```

---

## 🔔 通知示例

### 邮件主题
```
🚨 紫微智控 - 发现 3 个强信号 (03-08 10:35)
```

### 邮件内容包含：
- 📊 信号详情表格（代币、信号、分数、价格）
- 💰 建议仓位、止损、止盈
- 📈 风险回报比
- 💡 操作建议
- 🔗 Dashboard 快速链接

---

## 🧪 测试

### 测试邮件发送
```bash
cd /home/admin/Ziwei/projects/x402-trading-bot
python3 -c "
from strong_signal_monitor import send_email
send_email('测试邮件', '<h1>测试</h1>')
"
```

### 测试警报器
```bash
# 手动创建一个强信号文件
cat > /home/admin/Ziwei/data/strategy/test_signal.json << 'EOF'
[
  {
    "symbol": "BTC",
    "signal": "STRONG_BUY",
    "score": 20.0,
    "price": 67000,
    "suggested_amount_usd": 1000,
    "stop_loss": 63000,
    "take_profit": 80000
  }
]
EOF

# 运行警报器（会检测到测试信号）
python3 strong_signal_alert.py
```

---

## 📈 监控状态检查

### 检查进程
```bash
ps aux | grep strong_signal
```

### 查看最新警报
```bash
tail -50 /home/admin/Ziwei/data/logs/soul-trader/strong_signal_alerts.log
```

### 查看最新信号
```bash
cat /home/admin/Ziwei/data/strategy/signals_*.json | tail -100
```

---

## ⚙️ 阈值调整

**编辑 `strong_signal_alert.py`：**
```python
# 信号强度阈值
STRONG_BUY_THRESHOLD = 15.0  # STRONG_BUY 阈值
BUY_THRESHOLD = 10.0         # BUY 阈值
```

**建议：**
- 激进策略：降低阈值（BUY ≥ 8.0）
- 保守策略：提高阈值（STRONG_BUY ≥ 18.0）
- 当前配置：中等风险（STRONG_BUY ≥ 15.0, BUY ≥ 10.0）

---

## 🔄 自动化

### 添加到 crontab（可选）
```bash
# 每分钟检查一次强信号
* * * * * cd /home/admin/Ziwei/projects/x402-trading-bot && python3 strong_signal_alert.py --check-only
```

### 开机自启动
编辑 `/etc/rc.local`：
```bash
cd /home/admin/Ziwei/projects/x402-trading-bot
nohup python3 strong_signal_alert.py > /var/log/strong_signal.log 2>&1 &
```

---

## 📝 当前状态

| 组件 | 状态 | 说明 |
|------|------|------|
| `strong_signal_alert.py` | ✅ 运行中 | PID: 416441 |
| `strong_signal_monitor.py` | ⏸️ 待配置 | 需要 SMTP 授权码 |
| 警报日志 | ✅ 正常 | `/home/admin/Ziwei/data/logs/soul-trader/strong_signal_alerts.log` |
| 信号缓存 | ✅ 正常 | `/home/admin/Ziwei/data/strategy/.last_signal_cache` |

---

## 🎯 下一步

1. **立即：** 警报器已启动，自动监控中
2. **待办：** 更新 163 SMTP 授权码
3. **待办：** 测试邮件发送功能
4. **待办：** 添加更多收件人

---

**责任人：** 信念 × 如意 × 爱人  
**最后更新：** 2026-03-08 10:35
