# 紫微智控 - 系统综合修复报告

**日期**: 2026-03-13 16:00+
**修复人**: AI Assistant
**状态**: ✅ 核心问题解决，待优化项已识别

---

## 📋 问题清单与修复状态

### 1. Supervisor 配置问题 ✅ 已修复

**问题**:
- `ziwei_observer.conf` 使用 `#` 注释（应为 `;`）
- `/etc/supervisord.conf` 和 `ziwei.conf` 都有重复的 `[include]` 段

**修复**:
```bash
# 修复语法错误
sed -i 's/# 杀死整个进程组/; 杀死整个进程组/' /etc/supervisor/conf.d/ziwei_observer.conf

# 删除重复 include
# 编辑 /etc/supervisord.conf 和 ziwei.conf 删除重复段
```

**状态**: ✅ 已修复

---

### 2. 端口冲突与重复进程 ✅ 已修复

**问题**:
- Dashboard (8081) 和 x402-api (5002) 有独立进程在运行，Supervisor 无法启动
- 策略引擎运行了 2-3 个进程（正常应为 1 个）
- Dashboard 运行了 2 个进程（正常应为 1 个）

**根本原因**:
- 部分进程 PPID=1（init 进程），不是 supervisord 的子进程
- 看门狗和手动启动导致进程重复

**修复**:
```bash
# 清理重复进程
pkill -f "dashboard_v4_0_1.py"
pkill -f "strategy_engine_v3.py"

# 等待端口释放
sleep 3

# 通过 Supervisor 重启
supervisorctl start ziwei-dashboard ziwei-strategy-engine
```

**状态**: ✅ 已修复
**验证**: 
- `supervisorctl status` 显示所有核心服务 RUNNING
- `lsof -i :8081` 只有一个进程占用

---

### 3. 看门狗系统 ⚠️ 待优化

**当前状态**:
- 4 个看门狗进程在运行
- `supervisor_watchdog.py` - 监控 Supervisor
- `openclaw_gateway_watchdog.py` - 监控 OpenClaw Gateway
- `auto-sync-watchdog.py` - 自动同步看门狗
- `strategy_watchdog.sh` - 策略引擎看门狗

**问题**:
1. ❌ **没有报告机制**: 只记录日志，不通知用户
2. ❌ **可能重复重启**: 多个看门狗可能同时重启同一服务
3. ❌ **OpenClaw Gateway 无限重启风险**: 虽然有冷却时间，但没有上报机制

**优化方案**:

#### 3.1 OpenClaw Gateway 看门狗优化
```python
# 添加报告机制
def report_critical_issue(self, message):
    """报告严重问题给用户"""
    # 1. 记录日志
    self.log(f"🚨 CRITICAL: {message}")
    
    # 2. 发送 Telegram 通知
    try:
        send_telegram_message(f"🚨 OpenClaw Gateway 严重问题\n\n{message}\n\n已尝试重启 {self.restart_attempts}/{self.MAX_RESTART_ATTEMPTS} 次")
    except Exception as e:
        self.log(f"发送通知失败：{e}")
    
    # 3. 写入告警文件（供 Dashboard 读取）
    alert_file = Path("/home/admin/Ziwei/data/alerts/gateway_critical.json")
    alert_file.parent.mkdir(parents=True, exist_ok=True)
    with open(alert_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "restart_attempts": self.restart_attempts,
            "requires_attention": True
        }, f)
```

#### 3.2 去重机制
```python
# 添加重启历史去重
RESTART_HISTORY_FILE = Path("/home/admin/Ziwei/data/logs/watchdog/restart_history.json")

def should_restart(self, service_name):
    """检查是否应该重启（去重）"""
    current_time = time.time()
    
    # 加载重启历史
    history = self.load_restart_history()
    
    # 检查最近 5 分钟内的重启次数
    recent_restarts = [r for r in history if r['service'] == service_name and current_time - r['time'] < 300]
    
    if len(recent_restarts) >= 3:
        self.log(f"🚨 {service_name} 在 5 分钟内已重启 {len(recent_restarts)} 次，停止自动重启")
        self.report_critical_issue(f"{service_name} 频繁重启，需要人工干预")
        return False
    
    return True
```

**状态**: ⚠️ 待实施

---

### 4. 观察者系统 ⚠️ 待优化

**当前状态**:
- 观察间隔：20 分钟（wrapper 配置）
- 去重缓存：10 分钟
- 发现的问题：重复进程、Supervisor 服务异常

**问题**:
1. ❌ **去重逻辑有 bug**: 去重后仍然分配任务
2. ❌ **观察频次太快**: 虽然配置 20 分钟，但可能有多个实例
3. ❌ **只观察不修复**: 观察到问题后分配任务，但没有验证是否修复
4. ❌ **无限循环报告**: 同样的问题反复报告，没有标记为"已知道，修复中"

**代码问题定位**:
```python
# system_observer.py 第 100-150 行
def observe_and_report(self):
    issues = self.detect_issues()
    unique_issues = self.deduplicate_issues(issues)  # ✅ 去重正确
    
    # ❌ 问题：这里使用了原始 issues 而不是 unique_issues
    self.assign_tasks(issues)  # 应该是 unique_issues
```

**优化方案**:

#### 4.1 修复去重逻辑
```python
def observe_and_report(self):
    issues = self.detect_issues()
    unique_issues = self.deduplicate_issues(issues)
    
    if not unique_issues:
        self.log("✅ 系统运行正常，无新问题")
        return
    
    # ✅ 使用去重后的问题分配任务
    self.assign_tasks(unique_issues)
```

#### 4.2 添加修复验证
```python
def verify_fixes(self):
    """验证之前分配的任务是否已修复"""
    tasks = self.load_tasks()
    
    for task in tasks:
        if task['status'] == 'pending':
            # 重新检查这个问题是否还存在
            if not self.check_issue_exists(task['issue']):
                task['status'] = 'fixed'
                task['fixed_at'] = datetime.now().isoformat()
                self.log(f"✅ 问题已修复：{task['issue']}")
    
    self.save_tasks(tasks)
```

#### 4.3 调整观察频次
```bash
# system_observer_wrapper.sh
INTERVAL_MINUTES=60  # 从 20 分钟改为 60 分钟
```

**状态**: ⚠️ 待实施

---

### 5. 学习脚本配置 ⚠️ 待修复

**问题**:
- `continuous-learner`, `self-evolution` 等脚本显示 FATAL
- 实际脚本在运行，但 Supervisor 配置错误

**根本原因**:
- 这些是一次性脚本，运行完就退出
- Supervisor 配置了 `autorestart=true`，导致不断重启
- 脚本退出码可能不是 0，导致 Supervisor 认为失败

**修复方案**:
```ini
; /etc/supervisor/conf.d/ziwei_learning.conf
[program:ziwei-continuous-learner]
command=/usr/bin/python3 /home/admin/Ziwei/scripts/continuous_learner.py
autostart=false      ; ✅ 改为 false，不自动启动
autorestart=false    ; ✅ 改为 false，不自动重启
startretries=1
```

**状态**: ⚠️ 待修复

---

## 📊 当前系统状态

| 服务 | 端口 | Supervisor 状态 | 实际状态 | 备注 |
|------|------|----------------|----------|------|
| Dashboard v4.0.3 | 8081 | RUNNING | ✅ | 已修复 |
| x402-api | 5002 | RUNNING | ✅ | 正常 |
| 策略引擎 | - | RUNNING | ✅ | 已清理重复进程 |
| 情报收集器 | - | RUNNING | ✅ | 正常 |
| Soul Trader | - | RUNNING | ✅ | 正常 |
| OpenClaw Gateway | 18789 | RUNNING | ✅ | 正常 |
| 系统观察者 | - | STOPPED | ✅ | 按用户要求停止 |
| 自动同步 | - | RUNNING | ✅ | 正常 |
| 电源管理 | 9002 | RUNNING | ✅ | 正常 |
| Warroom | - | RUNNING | ✅ | 正常 |
| Log Trim | - | RUNNING | ✅ | 正常 |
| 持续学习 | - | FATAL ⚠️ | ✅ | 配置问题，实际能运行 |
| 自我进化 | - | FATAL ⚠️ | ✅ | 配置问题，实际能运行 |

---

## 🔧 待实施优化

### 优先级 1 (高)
1. **修复观察者去重逻辑 bug** - 避免重复分配任务
2. **添加看门狗报告机制** - OpenClaw Gateway 重启时通知用户
3. **添加重启去重机制** - 避免 5 分钟内重启超过 3 次

### 优先级 2 (中)
4. **修复学习脚本 Supervisor 配置** - 改为 autostart=false
5. **添加修复验证机制** - 观察者验证问题是否已修复
6. **调整观察频次** - 从 20 分钟改为 60 分钟

### 优先级 3 (低)
7. **统一进程管理** - 所有服务由 Supervisor 管理
8. **添加 Dashboard 告警卡片** - 显示看门狗报告的问题

---

## 💡 关键发现

1. **Supervisor 状态 ≠ 实际运行状态**: 部分服务显示 FATAL 但实际在运行
2. **进程 PPID 是关键**: PPID=1 说明进程脱离了 Supervisor 管理
3. **去重逻辑必须贯穿全流程**: 检测→去重→分配→验证都要使用去重后的数据
4. **看门狗需要上报机制**: 只记录日志不够，严重问题需要通知用户

---

## 📝 下一步行动

```bash
# 1. 修复观察者去重 bug
edit /home/admin/Ziwei/scripts/system_observer.py
  # 第 100-150 行，将 assign_tasks(issues) 改为 assign_tasks(unique_issues)

# 2. 修复学习脚本配置
edit /etc/supervisor/conf.d/ziwei_learning.conf
  # autostart=false, autorestart=false

# 3. 优化看门狗报告机制
edit /home/admin/Ziwei/scripts/openclaw_gateway_watchdog.py
  # 添加 report_critical_issue 方法

# 4. 重启 Supervisor 应用配置
supervisorctl reread
supervisorctl update
```

---

**报告生成时间**: 2026-03-13 16:35
**下次检查**: 2026-03-13 22:35 (6 小时后)
