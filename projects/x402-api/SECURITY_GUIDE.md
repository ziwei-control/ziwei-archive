# 🛡️ x402 API - 安全防护系统

## 📋 安全功能清单

### ✅ 已实现功能

| 功能 | 状态 | 说明 |
|------|------|------|
| **DDoS 防护** | ✅ 已启用 | 每秒 100 请求阈值，自动封禁 1 小时 |
| **频率限制** | ✅ 已启用 | 60 次/分钟，1000 次/小时 |
| **IP 黑名单** | ✅ 已启用 | 自动 + 手动封禁 |
| **SQL 注入检测** | ✅ 已启用 | 检测常见 SQL 注入模式 |
| **XSS 检测** | ✅ 已启用 | 检测跨站脚本攻击 |
| **路径遍历检测** | ✅ 已启用 | 检测../等路径遍历 |
| **命令注入检测** | ✅ 已启用 | 检测系统命令注入 |
| **攻击日志** | ✅ 已启用 | 完整记录所有攻击 |
| **安全告警** | ✅ 已启用 | 攻击次数超阈值告警 |
| **安全监控面板** | ✅ 已启用 | 实时查看安全状态 |

---

## 🔧 安全配置

### 频率限制

```python
{
    "requests_per_minute": 60,      # 每分钟最大请求数
    "requests_per_hour": 1000,      # 每小时最大请求数
    "burst_limit": 10,              # 突发请求限制
}
```

### DDoS 防护

```python
{
    "threshold_per_second": 100,    # 每秒请求阈值
    "block_duration": 3600,         # 封禁时长 (秒)
    "detection_window": 60,         # 检测窗口 (秒)
}
```

### 攻击检测

```python
{
    "sql_injection": True,          # SQL 注入检测
    "xss": True,                    # XSS 检测
    "path_traversal": True,         # 路径遍历检测
    "command_injection": True,      # 命令注入检测
}
```

### IP 黑名单

```python
{
    "enabled": True,
    "auto_block": True,             # 自动封禁
    "manual_block_list": [],        # 手动封禁列表
}
```

### 告警配置

```python
{
    "enabled": True,
    "email_alert": True,            # 邮件告警
    "threshold": 10,                # 触发告警的攻击次数
}
```

---

## 📊 查看安全状态

### API 端点

```bash
# 查看安全统计
curl http://8.213.149.224/api/v1/security/stats

# 查看攻击日志
curl http://8.213.149.224/api/v1/security/attacks

# 查看黑名单
curl http://8.213.149.224/api/v1/security/blacklist
```

### 命令行工具

```bash
# 启动安全监控面板
python3 /home/admin/Ziwei/projects/x402-api/security_dashboard.py
```

### 日志文件

```bash
# 安全日志目录
ls -la /home/admin/Ziwei/data/logs/security/

# 查看今日安全日志
cat /home/admin/Ziwei/data/logs/security/security_$(date +%Y%m%d).log

# 查看攻击日志
cat /home/admin/Ziwei/data/security/attack_log.json | python3 -m json.tool

# 查看黑名单
cat /home/admin/Ziwei/data/security/blacklist.json | python3 -m json.tool
```

---

## 🚨 攻击检测类型

### 1. SQL 注入检测

检测模式：
```
SELECT, INSERT, UPDATE, DELETE, DROP, UNION, ALTER
--, ;, /*, */
OR 1=1, AND 1=1
```

示例攻击：
```json
{"code": "'; DROP TABLE users; --"}
```

### 2. XSS 检测

检测模式：
```
<script>
javascript:
onerror=, onclick=, onload=
<iframe>
```

示例攻击：
```json
{"text": "<script>alert('xss')</script>"}
```

### 3. 路径遍历检测

检测模式：
```
../
..\
```

示例攻击：
```json
{"file": "../../../etc/passwd"}
```

### 4. 命令注入检测

检测模式：
```
; | & `
$(command)
exec, system, eval, passthru
```

示例攻击：
```json
{"cmd": "ls; rm -rf /"}
```

---

## ⛔ IP 封禁机制

### 自动封禁条件

1. **频率超限**
   - 每分钟 > 60 次请求 → 封禁 5 分钟
   - 每小时 > 1000 次请求 → 封禁 10 分钟

2. **DDoS 疑似**
   - 每秒 > 100 次请求 → 封禁 1 小时

3. **攻击检测**
   - 检测到攻击行为 → 记录攻击次数
   - 攻击次数 ≥ 10 次 → 加入黑名单

### 手动管理黑名单

```bash
# 启动监控面板
python3 /home/admin/Ziwei/projects/x402-api/security_dashboard.py

# 选择操作:
# 3. 从黑名单移除 IP
```

或手动编辑：
```bash
nano /home/admin/Ziwei/data/security/blacklist.json
```

---

## 📧 安全告警

### 告警触发条件

```
攻击次数 ≥ 10 次 → 触发告警
```

### 告警日志

```bash
# 查看告警日志
cat /home/admin/Ziwei/data/security/alert_log.json | python3 -m json.tool
```

### 告警内容

```json
{
    "timestamp": "2026-03-03T18:05:30",
    "ip": "192.168.1.100",
    "reason": "检测到攻击：sql_injection",
    "attack_count": 10,
    "alert_id": 1
}
```

---

## 🔍 安全监控面板

### 启动面板

```bash
python3 /home/admin/Ziwei/projects/x402-api/security_dashboard.py
```

### 功能菜单

```
🛡️  x402 API - 安全监控面板
======================================================================

📊 安全统计
----------------------------------------------------------------------
  总 IP 数：0
  当前封禁：0
  黑名单 IP: 0
  总攻击数：0

🚨 最近攻击 (最近 10 条)
----------------------------------------------------------------------
  ⚠️  2026-03-03T18:05:30 | 192.168.1.100   | sql_injection

⛔ 黑名单 IP
----------------------------------------------------------------------
  192.168.1.100
  ...

🔧 操作菜单
----------------------------------------------------------------------
  1. 查看完整攻击日志
  2. 查看完整黑名单
  3. 从黑名单移除 IP
  4. 清空攻击日志
  5. 导出安全报告
  0. 退出
```

---

## 📈 安全统计 API

### 端点

```
GET /api/v1/security/stats
```

### 响应示例

```json
{
    "total_ips": 150,
    "blocked_ips": 5,
    "blacklisted_ips": 2,
    "total_attacks": 25,
    "attacks_last_hour": 3,
    "total_requests_last_hour": 500,
    "alerts": 2
}
```

---

## 🛡️ 最佳实践

### 日常监控

```bash
# 每天检查安全状态
python3 /home/admin/Ziwei/projects/x402-api/security_dashboard.py

# 查看今日攻击
tail -100 /home/admin/Ziwei/data/logs/security/security_$(date +%Y%m%d).log

# 检查黑名单
cat /home/admin/Ziwei/data/security/blacklist.json | python3 -m json.tool
```

### 应急响应

```bash
# 1. 发现异常流量
# 查看安全统计
curl http://8.213.149.224/api/v1/security/stats

# 2. 查看攻击来源
curl http://8.213.149.224/api/v1/security/attacks?limit=100

# 3. 手动封禁 IP
# 编辑黑名单
nano /home/admin/Ziwei/data/security/blacklist.json

# 4. 重启服务
systemctl restart ziwei-x402-api
```

### 定期清理

```bash
# 清理 30 天前的日志
find /home/admin/Ziwei/data/logs/security/ -name "*.log" -mtime +30 -delete

# 导出安全报告
python3 /home/admin/Ziwei/projects/x402-api/security_dashboard.py
# 选择 5. 导出安全报告
```

---

## ⚠️ 注意事项

### 误报处理

如果正常用户被误封：

```bash
# 1. 查看黑名单
cat /home/admin/Ziwei/data/security/blacklist.json

# 2. 移除 IP
python3 /home/admin/Ziwei/projects/x402-api/security_dashboard.py
# 选择 3. 从黑名单移除 IP

# 3. 记录误报原因
echo "2026-03-03 - IP 192.168.1.100 误报，已移除" >> /home/admin/Ziwei/data/security/false_positives.log
```

### 性能优化

```bash
# 如果日志文件过大，定期清理
find /home/admin/Ziwei/data/security/ -name "*.json" -size +100M -exec gzip {} \;

# 限制日志保留天数 (默认 30 天)
# 修改 security.py 中的 retention_days 配置
```

---

## 📞 安全事件报告

### 报告模板

```markdown
## 安全事件报告

**时间**: 2026-03-03 18:05:30
**类型**: DDoS / SQL 注入 / XSS / 其他
**来源 IP**: 192.168.1.100
**影响**: 服务中断 / 数据泄露 / 无影响
**处理**: IP 已封禁 / 漏洞已修复 / 其他
**建议**: 加强监控 / 更新规则 / 其他
```

### 联系方式

```
安全事件报告：pandac00@163.com
GitHub Issues: https://github.com/ziwei-control/ziwei-archive/issues
```

---

## 🎯 总结

### 当前安全状态

```
✅ DDoS 防护已启用
✅ 频率限制已启用
✅ IP 黑名单已启用
✅ 攻击检测已启用
✅ 安全日志已启用
✅ 告警系统已启用
✅ 监控面板已启用
```

### 下一步

```
⏳ 配置邮件告警
⏳ 添加更详细的攻击模式
⏳ 集成第三方安全服务 (Cloudflare 等)
⏳ 定期安全审计
```

---

**安全防护系统已完全启用！** 🛡️

**API 现在受到全面保护，可以安全运营！**
