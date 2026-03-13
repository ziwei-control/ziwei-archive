# 紫微智控 - 电源管理系统

## 概述

电源管理系统提供远程开关机、重启和定时任务功能，集成到 Dashboard 和 Supervisor 统一管理。

## 组件

### 1. 电源管理服务 (system_power_manager.py)

**端口：** 9002  
**Supervisor 进程：** `ziwei-power-manager`

**API 接口：**

| 接口 | 方法 | 说明 |
|------|------|------|
| `/status` | GET | 获取系统状态和运行时间 |
| `/schedule` | GET | 获取计划任务 |
| `/schedule` | POST | 设置计划任务 |
| `/shutdown` | GET | 立即关机 |
| `/reboot` | GET | 立即重启 |
| `/cancel` | GET | 取消计划任务 |

**POST /schedule 请求格式：**
```json
{
  "action": "shutdown",
  "time": "2026-03-13T23:00:00"
}
```

或
```json
{
  "action": "reboot",
  "time": "06:00"
}
```

### 2. Dashboard 集成

**访问地址：** http://localhost:8081

电源管理卡片提供：
- 🟢 服务状态指示
- ⏱️ 系统运行时间
- ⏰ 计划任务显示
- 🔴 关机按钮
- 🔄 重启按钮
- ⏰ 定时任务按钮

### 3. Supervisor Web UI

**访问地址：** http://localhost:9001  
**账号：** `admin`  
**密码：** `Ziwei2026`

可以监控和管理所有进程，包括电源管理服务。

## 使用方法

### 立即关机

**Dashboard：** 点击电源管理卡片上的"🔴 关机"按钮  
**API：** `curl http://localhost:9002/shutdown`  
**命令行：** `poweroff`

### 立即重启

**Dashboard：** 点击电源管理卡片上的"🔄 重启"按钮  
**API：** `curl http://localhost:9002/reboot`  
**命令行：** `reboot`

### 定时任务

**Dashboard：** 点击"⏰ 定时"按钮，输入时间和操作类型  
**API：**
```bash
curl -X POST http://localhost:9002/schedule \
  -H "Content-Type: application/json" \
  -d '{"action":"shutdown","time":"23:00"}'
```

### 取消定时任务

**API：** `curl http://localhost:9002/cancel`

## 日志

**电源操作日志：** `/home/admin/Ziwei/data/logs/power/power_actions.log`

**Supervisor 日志：**
- 电源管理服务：`/home/admin/Ziwei/data/logs/supervisor/power-manager.out.log`
- 电源管理服务错误：`/home/admin/Ziwei/data/logs/supervisor/power-manager.err.log`

## 配置文件

**Supervisor 配置：** `/etc/supervisor/conf.d/ziwei_power.conf`

## 管理命令

```bash
# 查看状态
supervisorctl status ziwei-power-manager

# 重启服务
supervisorctl restart ziwei-power-manager

# 查看日志
tail -f /home/admin/Ziwei/data/logs/supervisor/power-manager.out.log
```

## 安全提示

⚠️ **谨慎操作！** 关机/重启会影响所有运行中的服务。

- 确保所有重要数据已保存
- 确保没有进行中的关键任务
- 定时任务设置后记得确认
- 生产环境操作前请三思

## 故障排除

### 电源管理服务未启动

```bash
supervisorctl start ziwei-power-manager
```

### 端口 9002 被占用

```bash
# 查找占用端口的进程
lsof -i :9002

# 杀死进程
kill <PID>

# 重启服务
supervisorctl restart ziwei-power-manager
```

### Dashboard 电源卡片不显示

1. 检查电源管理服务是否运行：`supervisorctl status ziwei-power-manager`
2. 重启 Dashboard：`supervisorctl restart ziwei-dashboard`
3. 清除浏览器缓存并刷新页面

---

**最后更新：** 2026-03-13  
**版本：** v1.0
