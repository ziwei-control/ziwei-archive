# x402 API 项目 - 可用资源清单

**更新日期：** 2026-03-07  
**更新人：** 信念 × 如意 × 爱人

---

## 🔑 API 密钥（已配置）

### 1. 阿里百炼 API（AI 模型）✅

**状态：** 已配置  
**位置：** `app_production.py`  
**用途：** 调用 8 个 AI Agent 端点

---

### 2. 邮件服务（163 邮箱）✅

**状态：** 已配置  
**位置：** `email_alert.py`  
**用途：** 发送安全告警邮件

---

### 3. GitHub Token ✅

**状态：** 已配置  
**位置：** `.env`  
**用途：** 自动推送代码

---

### 4. Gitee Token ✅

**状态：** 已配置  
**位置：** `.env`  
**用途：** 自动推送到 Gitee 镜像

---

### 5. 币安 API（交易机器人）✅

**状态：** 已配置（测试模式）  
**位置：** `x402-trading-bot/.env`  
**⚠️ 注意：** 测试模式开启，不真实交易

---

### 6. BaseScan API（区块链验证）⏳

**状态：** 未配置（使用公开 API）  
**建议：** 可免费注册 https://basescan.org/myapikey

---

## 💰 钱包地址（公开）

### USDC 收款钱包（Base 链）

```
地址：0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb
区块链：Base (L2)
代币：USDC (ERC-20)
查询：https://basescan.org/address/0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb
```

---

## 🌐 公网访问

### 服务器 IP

```
公网 IP: 8.213.149.224
位置：阿里云（新加坡）
```

**开放端口：**
- 80 → Nginx 反向代理
- 5002 → x402 API
- 8081 → 主 Dashboard
- 8090 → API 密钥发放
- 8091 → 用户登录验证
- 22 → SSH

**访问地址：**
- Dashboard: http://8.213.149.224/dashboard
- API: http://8.213.149.224:5002
- API Key: http://8.213.149.224:8090/get-api-key.html
- 后台：http://8.213.149.224:8091/admin-dashboard.html

---

## 🗄️ 数据库

### SQLite 数据库

```
路径：/home/admin/Ziwei/projects/x402-api/api_keys.db
用途：存储 API Key、用户信息、交易记录
状态：✅ 已创建
```

---

## 🚀 可调用的服务

### 1. 邮件发送 ✅

```bash
cd /home/admin/Ziwei/projects/x402-api
python3 -c "from email_alert import email_alerter; print('邮件服务可用')"
```

### 2. GitHub 推送 ✅

```bash
git push github main
git push github main --tags
```

### 3. Gitee 推送 ✅

```bash
git push gitee main
git push gitee main --tags
```

### 4. 区块链查询 ✅

```bash
# Base 链 RPC 可用
curl https://base-mainnet.public.blastapi.io
```

### 5. AI 模型调用 ✅

```bash
# 已在 app_production.py 中集成
curl http://localhost:5002/health
```

---

## ✅ 可用性检查

| 资源 | 状态 | 最后检查 |
|------|------|---------|
| 阿里百炼 API | ✅ 可用 | 2026-03-07 |
| 163 邮箱 SMTP | ✅ 可用 | 2026-03-07 |
| GitHub Token | ✅ 可用 | 2026-03-07 |
| Gitee Token | ✅ 可用 | 2026-03-07 |
| 币安 API | ✅ 可用（测试模式） | 2026-03-07 |
| Base 链 RPC | ✅ 可用 | 2026-03-07 |
| USDC 钱包 | ✅ 可用 | 2026-03-07 |
| 公网 IP | ✅ 可用 | 2026-03-07 |
| Nginx | ✅ 运行中 | 2026-03-07 |
| 所有服务 | ✅ 运行中 | 2026-03-07 |

---

## 📋 运行命令

### 启动所有服务

```bash
# 1. x402 API
cd /home/admin/Ziwei/projects/x402-api && nohup python3 app_production.py > api.log 2>&1 &

# 2. API 密钥发放
cd /home/admin/Ziwei/projects/x402-api && nohup python3 api_key_server.py > api_key_server.log 2>&1 &

# 3. 用户后台
cd /home/admin/Ziwei/projects/x402-api && nohup python3 x402_dashboard.py > x402_dashboard.log 2>&1 &

# 4. 主 Dashboard
cd /home/admin/Ziwei/projects && nohup python3 dashboard_v4_0_1.py > dashboard.log 2>&1 &

# 5. 交易机器人（测试模式）
cd /home/admin/Ziwei/projects/x402-trading-bot && nohup python3 start_test.py > trading.log 2>&1 &
```

### 检查服务状态

```bash
ps aux | grep -E "app_production|api_key_server|x402_dashboard|dashboard_v4" | grep -v grep
netstat -tlnp | grep -E "5002|8090|8091|8081|80"
```

---

## 🔒 安全提示

1. **密钥已添加到 `.gitignore`** - 不会泄露
2. **敏感配置在本地 `.env`** - 不提交到 Git
3. **定期轮换密钥** - 建议每 3 个月更换
4. **监控日志** - 检查异常调用

---

**清单完成时间：** 2026-03-07 09:50  
**责任人：** 信念 × 如意 × 爱人  
**状态：** ✅ 所有资源可用
