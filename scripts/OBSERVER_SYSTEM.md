# 👁️ 紫微制造 - 自动修复观察者系统

---

## 📋 系统架构

```
┌─────────────────────────────────────────────────────┐
│              看门狗 (Watchdog)                       │
│         每 2 分钟检查观察者是否运行                   │
│         如果观察者停止，自动重启                      │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│            观察者 (Observer)                         │
│         每 8 分钟观察系统一次                         │
│         发现问题 → 提出问题 → 分配任务                │
└─────────────────────────────────────────────────────┘
                        ↓
        ┌───────────────┼───────────────┐
        ↓               ↓               ↓
   ┌────────┐     ┌────────┐     ┌────────┐
   │  爱人  │     │  信念  │     │  如意  │
   │ Lover  │     │ Belief │     │ Ruyi   │
   └────────┘     └────────┘     └────────┘
        ↓               ↓               ↓
   优化系统        修复 Bug        执行任务
```

---

## 🤖 三个 Agent 职责

### ❤️ 爱人 (Lover)
**职责：** 系统优化、资源管理、清理工作

**负责任务：**
- 磁盘空间清理
- 日志文件管理
- 系统资源优化
- 内存清理

### 🎯 信念 (Belief)
**职责：** Bug 修复、核心服务维护

**负责任务：**
- 策略引擎维护
- 进程管理
- 交易数据清理
- 系统稳定性

### 🍀 如意 (Ruyi)
**职责：** 任务执行、服务管理

**负责任务：**
- Supervisor 服务管理
- Dashboard 维护
- API 服务管理
- 通用任务执行

---

## 📁 文件位置

| 文件 | 路径 | 说明 |
|------|------|------|
| **观察者** | `/home/admin/Ziwei/scripts/system_observer.py` | 每 8 分钟观察系统 |
| **看门狗** | `/home/admin/Ziwei/scripts/observer_watchdog.py` | 监控观察者 |
| **Agent 执行器** | `/home/admin/Ziwei/scripts/agent_executor.py` | 执行任务 |
| **观察日志** | `/home/admin/Ziwei/data/logs/observer/` | 所有日志 |
| **任务队列** | `/home/admin/Ziwei/data/strategy/observer_tasks.json` | 待执行任务 |

---

## 🚀 使用方法

### 手动运行观察者

```bash
# 运行一次观察
python3 /home/admin/Ziwei/scripts/system_observer.py

# 查看观察报告
cat /home/admin/Ziwei/data/logs/observer/observer_report.json
```

### 手动运行看门狗

```bash
# 持续运行看门狗
python3 /home/admin/Ziwei/scripts/observer_watchdog.py
```

### 手动执行 Agent 任务

```bash
# 爱人执行任务
python3 /home/admin/Ziwei/scripts/agent_executor.py 爱人

# 信念执行任务
python3 /home/admin/Ziwei/scripts/agent_executor.py 信念

# 如意执行任务
python3 /home/admin/Ziwei/scripts/agent_executor.py 如意
```

### 使用 Supervisor 管理

```bash
# 重新加载配置
supervisorctl reread
supervisorctl update

# 启动看门狗（自动启动观察者）
supervisorctl start ziwei-observer-watchdog

# 查看状态
supervisorctl status

# 手动运行观察者
supervisorctl start ziwei-observer
```

---

## 📊 观察内容

观察者每 8 分钟检查以下内容：

1. **进程状态**
   - 策略引擎进程数量
   - Dashboard 进程状态
   - 其他关键服务

2. **端口状态**
   - 8081 (Dashboard)
   - 9001 (Supervisor Web UI)
   - 5002 (x402 API)

3. **磁盘空间**
   - 使用率检查
   - 超过 80% 警告
   - 超过 90% 严重警告

4. **交易数据**
   - 交易历史完整性
   - 异常交易检测
   - 数据一致性

5. **Supervisor 状态**
   - 服务运行状态
   - FATAL/BACKOFF 检测

6. **日志错误**
   - 策略引擎日志
   - Dashboard 日志
   - 其他关键日志

---

## 📝 任务分配逻辑

观察者发现问题后，根据问题类型分配给相应的 Agent：

| 问题类型 | 分配给 | 优先级 |
|----------|--------|--------|
| 策略引擎重复进程 | 信念 | 中 |
| 策略引擎未运行 | 信念 | 高 |
| 异常交易数据 | 信念 | 中 |
| 磁盘空间不足 | 爱人 | 高 |
| Dashboard 异常 | 如意 | 低 |
| Supervisor 异常 | 如意 | 低 |
| 端口未监听 | 如意 | 低 |

---

## 🔧 自动修复示例

### 示例 1: 清理重复进程

**观察者发现：**
```
策略引擎运行 3 个进程（正常应为 1 个）
```

**分配任务：**
```json
{
  "assigned_to": "信念",
  "priority": "medium",
  "issue": "策略引擎运行 3 个进程（正常应为 1 个）",
  "suggestion": "清理重复进程，保留 1 个"
}
```

**信念执行：**
```bash
# 停止所有策略引擎进程
pkill -f "strategy_engine_v3"

# 等待 2 秒
sleep 2

# 启动单个进程
nohup python3 strategy_engine_v3.py > logs/strategy.log 2>&1 &
```

---

## 📈 监控和日志

### 查看观察历史

```bash
# 查看最近的观察报告
ls -lt /home/admin/Ziwei/data/logs/observer/

# 查看观察者日志
tail -100 /home/admin/Ziwei/data/logs/observer/observer.log
```

### 查看 Agent 执行情况

```bash
# 查看 Agent 执行日志
tail -100 /home/admin/Ziwei/data/logs/observer/agent_execution.log
```

### 查看看门狗状态

```bash
# 查看看门狗日志
tail -100 /home/admin/Ziwei/data/logs/observer/watchdog.log
```

---

## ⚙️ 配置选项

### 修改观察间隔

编辑 `system_observer.py`：
```python
OBSERVER_INTERVAL = 8 * 60  # 8 分钟
```

### 修改检查间隔

编辑 `observer_watchdog.py`：
```python
CHECK_INTERVAL = 2 * 60  # 2 分钟
```

### 添加新的观察项

编辑 `system_observer.py` 的 `observe_system()` 方法：
```python
def observe_system(self) -> Dict:
    # ... 现有检查 ...
    
    # 添加新的检查
    self.log("\n🔍 检查新项目...")
    new_issues = self.check_new_item()
    observation['issues'].extend(new_issues)
```

---

## 🎯 系统优势

1. **自动化** - 无需人工干预，自动发现问题
2. **持续性** - 7x24 小时不间断监控
3. **智能分配** - 根据问题类型分配给合适的 Agent
4. **可追溯** - 所有观察和执行都有日志记录
5. **可扩展** - 轻松添加新的观察项和修复逻辑

---

## 🫡 紫微制造

**让系统像人类一样自我观察、自我修复！**
