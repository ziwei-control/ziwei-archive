# Dashboard 版本说明

## ✅ 当前版本：v4.0.1（正式版）

**启用时间：** 2026-03-05 10:30  
**状态：** ✅ 正式运行中

---

## 📊 版本对比

| 版本 | 文件 | 状态 | 说明 |
|------|------|------|------|
| **v4.0.1** | dashboard_v4_0_1.py | ✅ **当前使用** | 融合版（真实收入 + 监控面板 + 终端） |
| v2.0.1 | dashboard_old_v2.py.bak | ❌ 已停用 | 旧版本 |
| v4.0 | dashboard_old_v4.py.bak | ❌ 已停用 | 极简版 |
| v3.0 | dashboard_old_v3.py.bak | ❌ 已停用 | Framer 风格版 |

---

## 🚀 启动方式

### 方式 1：使用启动脚本
```bash
/home/admin/Ziwei/projects/start-dashboard.sh
```

### 方式 2：手动启动
```bash
cd /home/admin/Ziwei/projects
python3 dashboard_v4_0_1.py
```

### 方式 3：systemd 服务
```bash
systemctl start ziwei-dashboard
systemctl enable ziwei-dashboard  # 开机自启
```

---

## 🌐 访问地址

**内网：**
```
http://localhost:8081
```

**公网：**
```
http://panda66.duckdns.org/
http://panda66.duckdns.org/dashboard
```

---

## 📈 v4.0.1 主要功能

### 真实收入显示
- ✅ x402 API 收入（真实 USDC）
- ✅ Binance 钱包余额（真实 USD）
- ✅ 交易机器人（模拟交易，明确标注）

### 监控面板（8 个）
1. 💻 系统状态
2. 🔧 服务状态
3. 📈 交易机器人（监控前 100 加密货币）
4. 🛡️ 安全监控
5. 💰 收入统计
6. ⚡ x402 API
7. 💰 加密货币实时价格
8. 🌍 全球战情室
9. 📊 项目进度
10. 🔍 系统代码映射

### 终端功能
- 💻 简单命令终端
- 🖥️ 完整交互式终端（点击展开）

---

## 🔄 版本更新记录

**v4.0.1 (2026-03-05)**
- ✅ 融合 v3.0 美观设计和 v4.0 实用功能
- ✅ 添加真实收入显示（x402 API + Binance）
- ✅ 添加加密货币实时价格面板
- ✅ 添加全球战情室面板
- ✅ 明确标注模拟交易
- ✅ 修复 JavaScript 大括号转义问题

**v4.0 (2026-03-04)**
- 极简风格
- 集成 ttyd 终端

**v3.0 (2026-03-03)**
- Framer 深色主题
- 流畅动画效果

**v2.0 (2026-03-02)**
- 基础监控功能

---

## 📋 配置文件

**主文件：**
```
/home/admin/Ziwei/projects/dashboard_v4_0_1.py
```

**备份文件：**
```
/home/admin/Ziwei/projects/dashboard_old_v2.py.bak
/home/admin/Ziwei/projects/dashboard_old_v4.py.bak
/home/admin/Ziwei/projects/dashboard_old_v3.py.bak
```

**日志文件：**
```
/tmp/dashboard_v4.log
```

---

## ⚠️ 重要提示

### 旧版本处理
- ✅ 已备份并添加 `.bak` 后缀
- ✅ 不再运行旧版本
- ✅ 保留备份以便需要时恢复

### 新版本特性
- ✅ 所有收入数据真实显示
- ✅ 模拟交易明确标注
- ✅ 每 20 分钟自动刷新
- ✅ 支持公网访问

---

**文档版本：** v1.0  
**最后更新：** 2026-03-05 10:30  
**维护者：** 紫微智控 AI Assistant
