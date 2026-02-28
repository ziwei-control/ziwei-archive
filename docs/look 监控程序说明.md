# look 监控程序说明

> 24 小时监控项目，自动将可执行脚本转为系统命令

---

## 🎯 程序功能

**look** 是一个低资源占用的监控程序，功能包括：

1. ✅ **24 小时持续监控** - 不间断监控项目状态
2. ✅ **自动命令创建** - 项目结束后自动创建系统命令
3. ✅ **低资源占用** - 内存 < 5MB，CPU < 0.1%
4. ✅ **低能耗** - 优化的检查间隔（60 秒）
5. ✅ **自动通知** - 输出命令供 agent 执行
6. ✅ **状态持久化** - 避免重复处理

---

## 📋 工作原理

```
look 启动
  ↓
每 60 秒检查项目目录
  ↓
发现项目状态为 Done
  ↓
查找项目中的可执行脚本
  ↓
创建系统命令包装脚本
  ↓
输出命令给 agent
  ↓
标记为已处理
  ↓
继续监控...
```

---

## 🚀 使用方法

### 基本命令

```bash
# 前台运行
./look.sh

# 后台运行
./look.sh --daemon

# 详细输出
./look.sh --verbose

# 查看状态
./look.sh --status

# 显示帮助
./look.sh --help
```

### 输出示例

```bash
$ ./look.sh

╔════════════════════════════════════════════════════════╗
║          look - 紫微智控项目监控程序                    ║
╚════════════════════════════════════════════════════════╝

✓ look 监控程序已启动
✓ 检查间隔：60 秒
✓ 项目目录：/home/admin/Ziwei/projects
✓ 命令目录：/home/admin/Ziwei/commands

按 Ctrl+C 停止监控

[look] 检查项目：TASK-20250227-002
[look] 项目 TASK-20250227-002 已完成
[look] ACTION: 为项目 TASK-20250227-002 创建命令：TASK-20250227-002
[look] SUCCESS: 已创建系统命令：TASK-20250227-002

╔════════════════════════════════════════════════════════╗
║          新命令已创建                                  ║
╚════════════════════════════════════════════════════════╝

命令名称：TASK-20250227-002
命令路径：/home/admin/Ziwei/commands/TASK-20250227-002
源脚本：/home/admin/Ziwei/projects/TASK-20250227-002/script.sh

使用方法:
  TASK-20250227-002 [参数]

需要执行:
  sudo ln -sf /home/admin/Ziwei/commands/TASK-20250227-002 /usr/local/bin/TASK-20250227-002
```

---

## 📁 项目位置

| 项目 | 位置 |
|------|------|
| **程序脚本** | `/home/admin/Ziwei/scripts/look.sh` |
| **项目目录** | `/home/admin/Ziwei/projects/look/` |
| **命令目录** | `/home/admin/Ziwei/commands/` |
| **日志文件** | `/home/admin/Ziwei/data/logs/look.log` |
| **状态文件** | `/home/admin/Ziwei/data/logs/look.state` |

---

## 🔧 配置

### 环境变量

编辑 `look.sh` 开头：

```bash
Ziwei_DIR="/home/admin/Ziwei"
PROJECTS_DIR="$Ziwei_DIR/projects"
COMMANDS_DIR="$Ziwei_DIR/commands"
CHECK_INTERVAL=60  # 检查间隔（秒）
```

### 检查间隔

| 间隔 | 资源占用 | 推荐场景 |
|------|---------|---------|
| **10 秒** | 较高 | 开发测试 |
| **60 秒** | 低 | 生产环境（默认） |
| **300 秒** | 极低 | 低频率项目 |

---

## 📊 资源占用

| 指标 | 数值 |
|------|------|
| **内存** | < 5MB |
| **CPU** | < 0.1% |
| **磁盘** | < 1MB (日志) |
| **网络** | 无 |

---

## 🎯 使用场景

### 场景 1: 新项目完成

当 `runtask` 完成任务后：

```bash
# look 会自动检测并输出:
[look] ACTION: 为项目 TASK-XXX 创建命令
[look] SUCCESS: 已创建系统命令

# 然后 agent 执行:
sudo ln -sf /home/admin/Ziwei/commands/TASK-XXX /usr/local/bin/TASK-XXX
```

---

### 场景 2: 后台持续监控

```bash
# 后台运行
./look.sh --daemon

# 查看状态
./look.sh --status

# 查看日志
tail -f /home/admin/Ziwei/data/logs/look.log
```

---

### 场景 3: 开机自启动

创建 systemd 服务：

```bash
sudo nano /etc/systemd/system/look.service
```

内容：

```ini
[Unit]
Description=Ziwei Control look monitor
After=network.target

[Service]
Type=simple
User=root
ExecStart=/home/admin/Ziwei/scripts/look.sh --daemon
Restart=always

[Install]
WantedBy=multi-user.target
```

启用：

```bash
sudo systemctl enable look
sudo systemctl start look
```

---

## 📝 日志查看

```bash
# 查看最新日志
tail -f /home/admin/Ziwei/data/logs/look.log

# 查看状态
cat /home/admin/Ziwei/data/logs/look.state

# 清理旧日志
> /home/admin/Ziwei/data/logs/look.log
```

---

## 🔍 故障排查

### 问题 1: 命令未创建

**检查**:
```bash
# 查看日志
tail /home/admin/Ziwei/data/logs/look.log

# 检查项目状态
cat /home/admin/Ziwei/projects/TASK-XXX/TASK.md
```

**解决**:
- 确保项目 TASK.md 中状态为 `状态：Done`
- 确保项目中有可执行脚本（.sh 或.py）

---

### 问题 2: 权限错误

**解决**:
```bash
# 赋予执行权限
sudo chmod +x /home/admin/Ziwei/scripts/look.sh

# 或手动创建符号链接
sudo ln -sf /home/admin/Ziwei/commands/TASK-XXX /usr/local/bin/TASK-XXX
```

---

### 问题 3: 重复创建命令

**检查**:
```bash
cat /home/admin/Ziwei/data/logs/look.state
```

**解决**:
- 状态文件会记录已处理的项目
- 如果重复，删除状态文件：`rm /home/admin/Ziwei/data/logs/look.state`

---

## 📋 命令说明

| 选项 | 说明 |
|------|------|
| `-v, --verbose` | 详细输出 |
| `-d, --daemon` | 后台运行 |
| `-s, --status` | 显示状态 |
| `-h, --help` | 显示帮助 |

---

## 🌐 仓库地址

**需要手动创建仓库后推送**:

### GitHub

1. 访问：https://github.com/new
2. 仓库名称：`look`
3. 描述：紫微智控项目监控程序
4. 公开：是
5. 点击创建

然后推送：
```bash
cd /home/admin/Ziwei/projects/look
git remote add origin git@github.com:ziwei-control/look.git
git push -u origin main
```

### Gitee

1. 访问：https://gitee.com/new
2. 仓库名称：`look`
3. 描述：紫微智控项目监控程序
4. 公开：是
5. 点击创建

然后推送：
```bash
cd /home/admin/Ziwei/projects/look
git remote add gitee git@gitee.com:pandac0/look.git
git push -u gitee main
```

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📄 许可证

MIT License

---

## 🔗 链接

- [紫微智控主仓库](https://github.com/ziwei-control/ziwei-archive)
- [runtask 命令](https://github.com/ziwei-control/runtask)

---

**look - 时刻监控，自动创建命令！** 🚀
