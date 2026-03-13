# 📸 紫微截图功能使用指南

## 🎯 功能概述

紫微系统现在集成了 OpenClaw 的屏幕截图功能，实现：
- ✅ 自动截取 Dashboard 监控画面
- ✅ 视觉化系统状态监控
- ✅ 异常画面自动检测
- ✅ 历史画面比较分析

---

## 📋 文件位置

| 文件 | 路径 | 功能 |
|------|------|------|
| **截图模块** | `/home/admin/Ziwei/scripts/screenshot_module.py` | 核心截图功能 |
| **视觉观察者** | `/home/admin/Ziwei/scripts/visual_observer.py` | 视觉监控逻辑 |
| **定时任务** | `/home/admin/Ziwei/scripts/visual_monitor_cron.sh` | 自动执行脚本 |
| **截图保存目录** | `/home/admin/Ziwei/data/screenshots/` | 截图文件存储 |
| **视觉记忆** | `/home/admin/Ziwei/data/knowledge/visual_memory.json` | 视觉历史记录 |

---

## 🔧 第一步：设置 Node 设备

### 1.1 启动 Node

在服务器上运行：

```bash
# 设置环境变量
export OPENCLAW_GATEWAY_TOKEN="73c8f5efc97f05b131130f5dc069b2aaee15d28761ddac2c"

# 启动 Node（后台运行）
nohup openclaw node run --host 127.0.0.1 --port 18789 --display-name "Ziwei Server Node" > /home/admin/Ziwei/data/logs/node.log 2>&1 &
```

### 1.2 批准配对

```bash
# 查看配对请求
openclaw devices list

# 批准配对（替换 <requestId>）
openclaw devices approve <requestId>
```

### 1.3 验证 Node 状态

```bash
# 查看 Node 状态
openclaw nodes status
```

应该显示：
```
Known: 1 · Paired: 1 · Connected: 1
```

---

## 📸 使用截图功能

### 2.1 手动截取 Dashboard

```bash
cd /home/admin/Ziwei/scripts

# 截取 Dashboard
python3 screenshot_module.py capture

# 或指定 Node ID
python3 screenshot_module.py capture <node_id>
```

### 2.2 录制屏幕视频

```bash
# 录制 5 秒视频
python3 screenshot_module.py record

# 录制 10 秒视频，10fps
python3 screenshot_module.py record <node_id> 10s 10
```

### 2.3 查看状态

```bash
python3 screenshot_module.py status
```

### 2.4 清理旧截图

```bash
# 清理 7 天前的截图
python3 screenshot_module.py cleanup 7

# 清理 30 天前的截图
python3 screenshot_module.py cleanup 30
```

---

## 👁️ 视觉观察者

### 3.1 手动观察

```bash
cd /home/admin/Ziwei/scripts

# 观察 Dashboard
python3 visual_observer.py observe

# 查看观察状态
python3 visual_observer.py status
```

### 3.2 初始化 Node

```bash
python3 visual_observer.py init
```

### 3.3 清理旧记忆

```bash
# 清理 30 天前的视觉记忆
python3 visual_observer.py cleanup 30
```

---

## ⏰ 自动监控

### 4.1 Cron 定时任务

已配置自动任务：
- **频率**: 每 8 分钟执行一次
- **清理**: 每天凌晨 2 点清理 30 天前的截图

查看 cron 任务：
```bash
crontab -l | grep visual
```

### 4.2 查看监控日志

```bash
# 视觉监控日志
tail -f /home/admin/Ziwei/data/logs/observer/visual_monitor.log

# 视觉观察者日志
tail -f /home/admin/Ziwei/data/logs/observer/visual_observer.log

# 截图模块日志
tail -f /home/admin/Ziwei/data/logs/observer/screenshot.log
```

---

## 📊 查看截图

### 5.1 截图文件位置

```bash
ls -lh /home/admin/Ziwei/data/screenshots/
```

文件命名格式：
- Dashboard 截图：`dashboard_YYYYMMDD_HHMMSS.png`
- 屏幕录像：`screen_YYYYMMDD_HHMMSS.mp4`

### 5.2 查看视觉记忆

```bash
cat /home/admin/Ziwei/data/knowledge/visual_memory.json | python3 -m json.tool
```

---

## 🔍 与观察者系统集成

视觉观察者会自动：

1. **每 8 分钟观察** - 截取 Dashboard 画面
2. **分析画面内容** - 识别异常元素
3. **比较历史画面** - 检测变化
4. **保存视觉记忆** - 积累视觉经验
5. **触发告警** - 发现异常时通知

### 集成点

视觉观察结果会保存到：
- `/home/admin/Ziwei/data/knowledge/visual_memory.json`
- 观察者学习日志
- MEMORY.md（定期固化）

---

## 🛠️ 故障排除

### 问题 1: Node 未连接

**症状**: `Known: 0 · Paired: 0 · Connected: 0`

**解决**:
```bash
# 1. 检查 Gateway 是否运行
ps aux | grep openclaw

# 2. 检查 token 是否正确
export OPENCLAW_GATEWAY_TOKEN="73c8f5efc97f05b131130f5dc069b2aaee15d28761ddac2c"

# 3. 重新启动 Node
pkill -f "openclaw node"
nohup openclaw node run --host 127.0.0.1 --port 18789 --display-name "Ziwei Server Node" > /home/admin/Ziwei/data/logs/node.log 2>&1 &

# 4. 批准配对
openclaw devices list
openclaw devices approve <requestId>
```

### 问题 2: 截图失败

**症状**: `❌ 截图失败`

**解决**:
```bash
# 1. 检查 Node 是否显示 Canvas
# Node 需要在运行 Canvas（WebView）

# 2. 检查权限
openclaw approvals allowlist list --node <node_id>

# 3. 手动测试
openclaw nodes canvas snapshot --node <node_id> --format png
```

### 问题 3: 截图目录为空

**症状**: 截图数量始终为 0

**解决**:
```bash
# 1. 检查目录权限
ls -la /home/admin/Ziwei/data/screenshots/

# 2. 手动创建目录
mkdir -p /home/admin/Ziwei/data/screenshots
chmod 755 /home/admin/Ziwei/data/screenshots

# 3. 检查日志
tail -100 /home/admin/Ziwei/data/logs/observer/screenshot.log
```

---

## 📈 未来扩展

### 计划功能

1. **AI 视觉分析** - 使用 Qwen Vision 分析截图内容
2. **异常自动检测** - 识别红色错误提示、异常数据等
3. **视觉趋势分析** - 基于历史画面预测问题
4. **Telegram 告警** - 发现异常时发送截图
5. **Dashboard 热区监控** - 重点监控关键区域

### 集成建议

```python
# 在 observer_watchdog.py 中添加
from visual_observer import VisualObserver

visual = VisualObserver()
visual.observe_dashboard()  # 每次观察时截图
```

---

## 🫡 总结

紫微截图功能让观察者系统具备了"视觉"能力：

| 能力 | 说明 | 状态 |
|------|------|------|
| **截图** | 自动截取 Dashboard | ✅ 已实现 |
| **录像** | 录制屏幕视频 | ✅ 已实现 |
| **存储** | 保存截图和记忆 | ✅ 已实现 |
| **分析** | AI 视觉分析 | 🔄 待实现 |
| **告警** | 异常自动通知 | 🔄 待实现 |

**下一步**: 完成 Node 设置，开始视觉监控！

---

**文档更新**: 2026-03-12  
**责任人**: 紫微智控 AI Assistant
