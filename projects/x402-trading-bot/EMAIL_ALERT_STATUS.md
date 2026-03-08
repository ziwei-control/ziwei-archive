# 📧 邮件警报状态报告

**日期：** 2026-03-08 10:40  
**状态：** ⚠️ 待更新授权码

---

## 🔍 诊断结果

### 当前配置
```
发件人：pandac00@163.com
收件人：19922307306@189.cn
SMTP 服务器：smtp.163.com:465
密码长度：16 字符
```

### 测试结果
```
❌ SMTP 认证失败 (535 Error: authentication failed)
```

### 可能原因
1. **授权码已过期** - 163 邮箱授权码有时效性
2. **授权码错误** - 可能不是最新的
3. **SMTP 服务未开启** - 需要在 163 邮箱设置中开启

---

## 🔧 解决方案

### 方法 1：获取新的授权码（推荐）

1. **登录 163 邮箱**
   - 网址：https://mail.163.com
   - 账号：pandac00@163.com

2. **开启 SMTP 服务**
   - 设置 → POP3/SMTP/IMAP
   - 确保 "IMAP/SMTP 服务" 已开启

3. **生成新授权码**
   - 点击 "授权码管理"
   - 点击 "新增授权码"
   - 短信验证后获取新授权码

4. **更新配置**
   ```bash
   # 编辑 .env 文件
   nano /home/admin/Ziwei/projects/x402-trading-bot/.env
   
   # 更新这一行
   SENDER_PASSWORD=新授权码
   ```

5. **测试**
   ```bash
   cd /home/admin/Ziwei/projects/x402-trading-bot
   python3 -c "from strong_signal_monitor import send_email; send_email('测试', '测试内容')"
   ```

---

### 方法 2：使用备用邮箱

如果有其他邮箱（QQ、Gmail 等），可以改用：

```python
# 编辑 strong_signal_monitor.py

# QQ 邮箱
SMTP_SERVER = "smtp.qq.com"
SMTP_PORT = 465
SENDER_EMAIL = "your_qq@qq.com"

# Gmail
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
SENDER_EMAIL = "your@gmail.com"
```

---

## ✅ 当前可用通知方式

虽然邮件暂不可用，但以下通知方式**正常工作**：

### 1. 本地日志警报 ✅

**位置：** `/home/admin/Ziwei/data/logs/soul-trader/strong_signal_alerts.log`

**查看最新警报：**
```bash
tail -100 /home/admin/Ziwei/data/logs/soul-trader/strong_signal_alerts.log
```

**实时监控：**
```bash
tail -f /home/admin/Ziwei/data/logs/soul-trader/strong_signal_alerts.log
```

### 2. Dashboard 查看 ✅

**访问地址：**
- 内网：http://localhost:8081
- 公网：http://panda66.duckdns.org:8081

### 3. 策略引擎日志 ✅

**位置：** `/home/admin/Ziwei/data/logs/soul-trader/strategy_engine_*.out`

**查看最新信号：**
```bash
cat /home/admin/Ziwei/data/strategy/signals_*.json | tail -50
```

---

## 📋 授权码更新检查清单

更新授权码后执行：

- [ ] 编辑 `.env` 文件，更新 `SENDER_PASSWORD`
- [ ] 重启警报器：
  ```bash
  pkill -f strong_signal_monitor
  cd /home/admin/Ziwei/projects/x402-trading-bot
  nohup python3 strong_signal_monitor.py > /home/admin/Ziwei/data/logs/soul-trader/strong_signal_monitor.out 2>&1 &
  ```
- [ ] 测试邮件发送
- [ ] 确认收件人收到测试邮件

---

## 🎯 当前监控状态

| 组件 | 状态 | 说明 |
|------|------|------|
| 策略引擎 | ✅ 运行中 | PID: 414842 |
| 强信号警报器 | ✅ 运行中 | PID: 416441 |
| 本地日志记录 | ✅ 正常 | 实时记录 |
| 邮件通知 | ⏸️ 待配置 | 需更新授权码 |

---

## 📞 需要 Martin 操作

**请立即：**
1. 登录 163 邮箱获取新授权码
2. 将新授权码告诉我
3. 我会自动更新配置并测试

**或者：**
- 使用其他邮箱（QQ/Gmail）
- 只用本地日志（已正常工作）

---

**最后更新：** 2026-03-08 10:40  
**责任人：** 爱人
