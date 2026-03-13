# 紫微智控 - Supervisor 看门狗系统

## 概述

看门狗系统确保 Supervisor 本身持续运行，形成双重保护机制：
- **Supervisor** → 管理所有业务进程，自动重启
- **看门狗** → 管理 Supervisor，自动重启

## 架构

```
┌─────────────────────────────────────────────────────┐
│                   systemd (开机自启)                 │
├─────────────────────────────────────────────────────┤
│  ┌─────────────────────┐   ┌─────────────────────┐  │
│  │  supervisord.service│   │ziwei-supervisor-    │  │
│  │  (Supervisor 主进程) │   │watchdog.service     │  │
│  │  ✅ 开机自启         │   │(看门狗进程)          │  │
│  │  ✅ 失败自动重启     │   │✅ 开机自启           │  │
│  │                     │   │✅ 失败自动重启       │  │
│  └──────────┬──────────┘   └──────────┬──────────┘  │
│             │                          │              │
│             │ 监控                      │ 监控          │
│             ▼                          ▼              │
│  ┌─────────────────────────────────────────────────┐ │
│  │          11 个业务进程                           │ │
│  │  - x402-api, dashboard, strategy-engine, ...    │ │
│  └─────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

## 组件

### 1. systemd 服务

#### supervisord.service
- **位置**: `/etc/systemd/system/supervisord.service`
- **功能**: 管理 Supervisor 主进程
- **开机自启**: ✅ 已启用
- **自动重启**: ✅ 失败后 10 秒重启

#### ziwei-supervisor-watchdog.service
- **位置**: `/etc/systemd/system/ziwei-supervisor-watchdog.service`
- **功能**: 运行看门狗脚本
- **开机自启**: ✅ 已启用
- **自动重启**: ✅ 失败后 10 秒重启

### 2. 看门狗脚本

**文件**: `/home/admin/Ziwei/scripts/supervisor_watchdog.py`

**功能**:
- 每 30 秒检查 Supervisor 是否运行
- 检测 Supervisor 无响应时自动重启
- 检查管理的进程状态，重启异常进程
- 限制重启次数（最多 5 次），防止无限重启循环
- 重启冷却时间 60 秒，避免频繁重启

**配置参数**:
```python
WATCHDOG_INTERVAL = 30      # 检查间隔（秒）
MAX_RESTART_ATTEMPTS = 5    # 最大重启次数
RESTART_COOLDOWN = 60       # 重启冷却时间（秒）
```

## 管理命令

### 查看状态

```bash
# 查看 Supervisor 服务状态
systemctl status supervisord.service

# 查看看门狗服务状态
systemctl status ziwei-supervisor-watchdog.service

# 查看所有进程状态
supervisorctl status
```

### 启动/停止/重启

```bash
# Supervisor 服务
systemctl start supervisord.service
systemctl stop supervisord.service
systemctl restart supervisord.service

# 看门狗服务
systemctl start ziwei-supervisor-watchdog.service
systemctl stop ziwei-supervisor-watchdog.service
systemctl restart ziwei-supervisor-watchdog.service
```

### 开机自启管理

```bash
# 启用开机自启（已配置）
systemctl enable supervisord.service
systemctl enable ziwei-supervisor-watchdog.service

# 禁用开机自启
systemctl disable supervisord.service
systemctl disable ziwei-supervisor-watchdog.service
```

## 日志位置

### 看门狗日志
- **运行日志**: `/home/admin/Ziwei/data/logs/supervisor/watchdog.log`
- **标准输出**: `/home/admin/Ziwei/data/logs/supervisor/watchdog.out.log`
- **错误输出**: `/home/admin/Ziwei/data/logs/supervisor/watchdog.err.log`

### Supervisor 日志
- **主日志**: `/home/admin/Ziwei/data/logs/supervisor/supervisord.log`
- **进程日志**: `/home/admin/Ziwei/data/logs/supervisor/*.out.log`
- **进程错误**: `/home/admin/Ziwei/data/logs/supervisor/*.err.log`

### systemd 日志

```bash
# 查看 Supervisor 服务日志
journalctl -u supervisord.service -f

# 查看看门狗服务日志
journalctl -u ziwei-supervisor-watchdog.service -f

# 查看最近 100 行
journalctl -u supervisord.service -n 100
```

## 保护机制

### 三层保护

1. **systemd 层**
   - 开机自动启动 Supervisor 和看门狗
   - 服务失败后自动重启（Restart=always）
   - 重启延迟 10 秒，避免瞬时故障

2. **看门狗层**
   - 独立于 Supervisor 运行
   - 每 30 秒检查 Supervisor 状态
   - 发现异常自动重启 Supervisor
   - 限制重启次数，避免无限循环

3. **Supervisor 层**
   - 管理所有业务进程
   - 进程崩溃后秒级重启
   - 自动重启尝试 3 次

### 故障场景处理

| 场景 | 检测方式 | 处理措施 |
|------|---------|---------|
| Supervisor 进程退出 | PID 文件检查 | 看门狗重启 Supervisor |
| Supervisor 无响应 | supervisorctl 超时 | 看门狗重启 Supervisor |
| 业务进程崩溃 | Supervisor 监控 | Supervisor 自动重启 |
| 多个进程异常 | 状态扫描 | 看门狗批量重启 |
| 系统重启 | systemd | 自动启动所有服务 |

## 验证测试

### 测试 Supervisor 自启

```bash
# 1. 停止 Supervisor
systemctl stop supervisord.service

# 2. 等待看门狗检测（30 秒内）
journalctl -u ziwei-supervisor-watchdog.service -f

# 3. 查看 Supervisor 是否被重启
systemctl status supervisord.service
```

### 测试进程自启

```bash
# 1. 停止某个业务进程
supervisorctl stop ziwei-dashboard

# 2. 查看是否自动重启
supervisorctl status ziwei-dashboard

# 3. 查看 Supervisor 日志
tail -f /home/admin/Ziwei/data/logs/supervisor/supervisord.log
```

### 测试开机自启

```bash
# 重启系统
reboot

# 系统启动后检查
systemctl status supervisord.service
systemctl status ziwei-supervisor-watchdog.service
supervisorctl status
```

## 故障排除

### Supervisor 无法启动

```bash
# 1. 检查配置文件
supervisord -c /etc/supervisord.conf -t

# 2. 检查端口占用
netstat -tlnp | grep -E "(9001|8081|5002)"

# 3. 查看错误日志
journalctl -u supervisord.service -n 50
tail -100 /home/admin/Ziwei/data/logs/supervisor/supervisord.log
```

### 看门狗不工作

```bash
# 1. 检查服务状态
systemctl status ziwei-supervisor-watchdog.service

# 2. 查看日志
tail -f /home/admin/Ziwei/data/logs/supervisor/watchdog.log

# 3. 手动运行测试
python3 /home/admin/Ziwei/scripts/supervisor_watchdog.py
```

### 进程频繁重启

```bash
# 1. 查看进程错误日志
tail -100 /home/admin/Ziwei/data/logs/supervisor/<进程名>.err.log

# 2. 检查系统资源
top -p $(pgrep -d, -f "python3.*ziwei")

# 3. 临时禁用自动重启
supervisorctl stop <进程名>
```

## 配置修改

### 添加新进程

1. 在 `/etc/supervisor/conf.d/` 创建配置文件
2. 重新加载配置：
   ```bash
   supervisorctl reread
   supervisorctl update
   ```

### 修改看门狗参数

1. 编辑 `/home/admin/Ziwei/scripts/supervisor_watchdog.py`
2. 重启看门狗服务：
   ```bash
   systemctl restart ziwei-supervisor-watchdog.service
   ```

### 修改 systemd 配置

1. 编辑对应的 `.service` 文件
2. 重新加载 systemd：
   ```bash
   systemctl daemon-reload
   systemctl restart <服务名>
   ```

## 安全提示

⚠️ **重要**:
- 不要同时运行多个 Supervisor 实例
- 修改配置前先备份
- 生产环境重启前确保数据已保存
- 定期查看日志，提前发现潜在问题

---

**最后更新**: 2026-03-13  
**版本**: v1.0  
**责任人**: AI Assistant
