# 🚀 紫微智控 (Ziwei Control & Intelligence)

**AI 驱动的一人公司系统 - 让 AI 智能体自主付费，开启机器经济时代！**

[![Status](https://img.shields.io/badge/status-online-green)](http://8.213.149.224/dashboard)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![Payment](https://img.shields.io/badge/payment-USDC-yellow)](https://basescan.org/address/0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb)

---

## 📋 项目概述

紫微智控是一个**AI 驱动的一人公司系统**，集成了 AI 服务 API、自动交易、市场监控、安全防护等功能，支持 x402 支付协议实现自动收款。

### 核心特性

- ✅ **8 个 AI Agent 端点** - 代码审计、翻译、架构设计等
- ✅ **x402 支付协议** - USDC 自动支付，无需人工干预
- ✅ **Base 链集成** - 低 Gas 费，快速确认
- ✅ **企业级安全防护** - DDoS 防护、攻击检测、邮件告警
- ✅ **系统监控 Dashboard** - 实时监控所有服务状态
- ✅ **自动化交易** - 监控 x402 生态代币，自动交易
- ✅ **全球市场监控** - 加密货币 + 股票市场 24 小时监控

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                    紫微智控系统架构                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ x402 API    │  │  Dashboard  │  │ 全球战情室  │        │
│  │ (端口 5002)  │  │  (端口 8081) │  │             │        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
│         │                │                │                │
│         └────────────────┴────────────────┘                │
│                           │                                │
│                  ┌────────▼────────┐                       │
│                  │   Nginx 反向代理  │                       │
│                  │   (端口 80)      │                       │
│                  └────────┬────────┘                       │
│                           │                                │
│         ┌─────────────────┼─────────────────┐             │
│         │                 │                 │             │
│  ┌──────▼──────┐  ┌──────▼──────┐  ┌──────▼──────┐       │
│  │ 公网访问    │  │ 内网访问    │  │ 安全系统    │       │
│  │ 8.213.149.224│  │ localhost   │  │ 邮件告警    │       │
│  └─────────────┘  └─────────────┘  └─────────────┘       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 项目组成

### 1. x402 API 服务

**端口**: 5002  
**状态**: ✅ 运行中  
**功能**: 提供 8 个 AI Agent 端点

| 端点 | 功能 | 价格 (USDC) |
|------|------|------------|
| `/api/v1/code-audit` | 代码审计 | 0.05 |
| `/api/v1/code-gen` | 代码生成 | 0.08 |
| `/api/v1/architect` | 架构设计 | 0.10 |
| `/api/v1/translate` | 翻译 | 0.02 |
| `/api/v1/logic` | 逻辑推理 | 0.06 |
| `/api/v1/long-text` | 长文解析 | 0.03 |
| `/api/v1/crawl` | 网络爬虫 | 0.04 |
| `/api/v1/vision` | 视觉解析 | 0.15 |

**技术栈**: Python + HTTP Server + 阿里百炼 API

---

### 2. 系统监控 Dashboard

**端口**: 8081  
**状态**: ✅ 运行中  
**访问**: http://8.213.149.224/dashboard

**监控模块**:
- 💻 系统状态 (CPU/内存/磁盘)
- 🔧 服务状态 (5 个 systemd 服务)
- 🛡️ 安全监控 (攻击日志/黑名单)
- 💰 收入统计 (USDC 支付)
- 📡 API 端点 (8 个端点)
- 📊 项目进度 (6 个项目)

**特性**:
- 响应式设计
- 自动刷新 (30 秒)
- 实时进度条
- 状态徽章

---

### 3. 全球战情室

**状态**: ✅ 运行中  
**功能**: 24 小时市场监控

**监控范围**:
- 加密货币市场 (前 100 名代币)
- A 股/港股/美股全市场
- 社交媒体热点

**警报条件**:
- 加密货币：30%+ 涨跌
- 股票：10%+ 短期机会
- 社交媒体：5000+ 提及

---

### 4. x402 交易机器人

**状态**: ✅ 运行中 (测试模式)  
**功能**: 自动交易 x402 生态代币

**监控代币**:
- VIRTUAL (Binance)
- PAYAI (Phemex)
- PING (Phemex)
- HEU (Gate.io)

**交易策略**:
- 网格交易
- 趋势跟踪
- 套利交易

**风险控制**:
- 最大仓位：20%
- 止损：-10%
- 止盈：+5%

---

### 5. 安全防护系统

**状态**: ✅ 已启用  
**功能**: 企业级安全防护

**防护功能**:
- 🛡️ DDoS 防护 (100 请求/秒阈值)
- 🛡️ 频率限制 (60 次/分钟)
- 🛡️ IP 黑名单 (自动 + 手动)
- 🛡️ SQL 注入检测
- 🛡️ XSS 攻击检测
- 🛡️ 路径遍历检测
- 🛡️ 命令注入检测

**告警系统**:
- 邮件告警 (pandac00@163.com)
- 攻击日志记录
- 实时安全监控

---

### 6. 日志修剪服务

**状态**: ✅ 运行中  
**功能**: 自动清理日志文件

**配置**:
- 监控间隔：60 秒
- 自动修剪：超过阈值的日志
- 日志保留：30 天

---

### 7. 自动同步监控

**状态**: ✅ 运行中 (6 实例)  
**功能**: 监控文件同步状态

**特性**:
- 多实例冗余 (6 个实例)
- 自动修复
- 日志记录

---

## 🌐 网络配置

### 公网访问

| 服务 | 地址 | 端口 |
|------|------|------|
| Dashboard | http://8.213.149.224/dashboard | 80 |
| x402 API | http://8.213.149.224/api/ | 80 |
| 健康检查 | http://8.213.149.224/health | 80 |

### 内网访问

| 服务 | 地址 | 端口 |
|------|------|------|
| x402 API | http://localhost:5002 | 5002 |
| Dashboard | http://localhost:8081 | 8081 |
| searxng | http://localhost:8080 | 8080 |
| OpenClaw | http://localhost:18789 | 18789 |

---

## 💰 支付系统

### x402 支付协议

**钱包地址**: `0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb`  
**网络**: Base (L2)  
**代币**: USDC (ERC-20)

**支付流程**:
1. 用户调用 API (无支付)
2. API 返回 HTTP 402 + 支付信息
3. 用户支付 USDC (Base 链)
4. 用户重发请求 + 支付证明
5. API 验证支付
6. 返回 API 结果

**查看收入**:
- 区块链浏览器：https://basescan.org/address/0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb
- Dashboard: http://8.213.149.224/dashboard

---

## 🔧 技术栈

### 后端

- **Python 3.6+** - 主要编程语言
- **HTTP Server** - Web 服务
- **阿里百炼 API** - AI 模型调用
- **psutil** - 系统监控

### 前端

- **纯 HTML/CSS/JS** - Dashboard 界面
- **响应式设计** - 多设备适配

### 基础设施

- **Nginx** - 反向代理
- **systemd** - 服务管理
- **Docker** - 容器运行时 (可选)

### 区块链

- **Base 链** - L2 网络
- **USDC** - 稳定币
- **x402 协议** - 支付协议

---

## 📊 系统资源

### 内存使用

```
openclaw-gateway:    455 MB (23.3%)
node (OpenClaw):     176 MB (9.0%)
systemd-journald:    154 MB (7.9%)
searxng worker:      132 MB (6.8%)
x402-trading-bot:     60 MB (3.0%)
x402-api:             19 MB (1.0%)
dashboard:            21 MB (1.1%)
```

### 磁盘使用

```
紫微智控项目：34.68 MB
日志文件：动态增长
安全数据：动态增长
```

---

## 🛠️ 管理命令

### 服务管理

```bash
# 查看所有服务状态
systemctl list-units --type=service --state=running

# 查看紫微智控服务
systemctl status ziwei-*

# 重启所有服务
systemctl restart ziwei-*
```

### 单个服务管理

```bash
# x402 API
systemctl start|stop|restart|status ziwei-x402-api

# Dashboard
systemctl start|stop|restart|status ziwei-dashboard

# 全球战情室
systemctl start|stop|restart|status ziwei-warroom

# 交易机器人
systemctl start|stop|restart|status ziwei-trading-bot

# 日志修剪
systemctl start|stop|restart|status ziwei-log-trim
```

### 日志查看

```bash
# Dashboard 日志
journalctl -u ziwei-dashboard -f

# x402 API 日志
journalctl -u ziwei-x402-api -f

# 所有紫微智控日志
journalctl -u ziwei-* -f

# 安全日志
tail -f /home/admin/Ziwei/data/logs/security/security_$(date +%Y%m%d).log
```

### 进程查看

```bash
# 查看所有进程
ps aux --sort=-%mem | head -30

# 查看紫微智控进程
ps aux | grep -E "Ziwei|dashboard|x402" | grep -v grep

# 查看监听端口
netstat -tlnp | grep LISTEN
```

---

## 📁 目录结构

```
/home/admin/Ziwei/
├── projects/
│   ├── x402-api/              # x402 API 服务
│   │   ├── app_production.py  # 主程序
│   │   ├── security.py        # 安全模块
│   │   ├── email_alert.py     # 邮件告警
│   │   └── ...
│   ├── x402-python-sdk/       # Python SDK
│   ├── x402-trading-bot/      # 交易机器人
│   ├── global-warroom/        # 全球战情室
│   ├── dashboard.py           # 监控 Dashboard
│   └── ...
├── scripts/                   # 工具脚本
├── data/
│   ├── security/              # 安全数据
│   ├── logs/                  # 日志文件
│   └── tasks/                 # 任务数据
└── docs/                      # 文档
```

---

## 🎯 项目进度

| 项目 | 进度 | 状态 |
|------|------|------|
| x402 API | 100% | ✅ 已完成 |
| x402 Python SDK | 100% | ✅ 已完成 |
| x402 交易机器人 | 90% | ✅ 测试中 |
| 全球战情室 | 100% | ✅ 已完成 |
| 安全防护系统 | 100% | ✅ 已完成 |
| 邮件告警系统 | 100% | ✅ 已完成 |
| Dashboard | 100% | ✅ 已完成 |

---

## 📈 预期收益

### x402 API

```
月收入：$1,500
年收入：$18,000
利润率：60-80%
```

### x402 Python SDK

```
月收入：$1,300 - $3,250
年收入：$15,600 - $39,000
利润率：45-70% (CodeCanyon 抽成后)
```

### 交易机器人

```
月收入：$0 - $500 (测试阶段)
年收入：$0 - $6,000
风险等级：高
```

**总计预期年收入**: $33,600 - $63,000

---

## 📞 支持与联系

### 文档

- [完整文档](https://github.com/ziwei-control/ziwei-archive)
- [API 参考](projects/x402-api/docs/api-reference.md)
- [安全指南](projects/x402-api/SECURITY_GUIDE.md)
- [支付指南](projects/x402-api/X402_PAYMENT_GUIDE.md)

### 联系方式

- **Email**: pandac00@163.com
- **GitHub**: https://github.com/ziwei-control/ziwei-archive
- **Gitee**: https://gitee.com/pandac0/ziwei-archive

### 问题反馈

- GitHub Issues: https://github.com/ziwei-control/ziwei-archive/issues
- Gitee Issues: https://gitee.com/pandac0/ziwei-archive/issues

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

## 🌟 统计

![Stars](https://img.shields.io/github/stars/ziwei-control/ziwei-archive?style=social)
![Forks](https://img.shields.io/github/forks/ziwei-control/ziwei-archive?style=social)
![Issues](https://img.shields.io/github/issues/ziwei-control/ziwei-archive)

---

## 🎉 总结

**紫微智控**是一个完整的 AI 驱动的一人公司系统，集成了：

- ✅ AI 服务 API (8 个端点)
- ✅ x402 支付协议 (自动收款)
- ✅ 系统监控 Dashboard (实时监控)
- ✅ 企业级安全防护 (DDoS/攻击检测)
- ✅ 自动化交易 (x402 生态代币)
- ✅ 全球市场监控 (加密货币 + 股票)

**所有服务已部署完成，可以开始运营！** 🚀

**访问 Dashboard 查看系统状态**: http://8.213.149.224/dashboard 📊

---

**最后更新**: 2026-03-03  
**版本**: 1.0.0  
**作者**: 紫微智控团队
