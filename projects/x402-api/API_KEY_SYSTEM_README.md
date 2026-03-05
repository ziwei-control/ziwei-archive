# x402 API 密钥自动发放系统（生产环境版）

**最后更新：** 2026-03-05  
**版本：** v2.0.0

---

## 🎯 核心功能

**用户流程：**
1. 访问网页 → 看到支付地址
2. 发送 **0.03-0.07 USDC** 到 `0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb`
3. 点击"验证交易"按钮
4. 系统自动查询 BaseScan
5. ✅ 成功 → 弹窗显示：
   - **API_BASE_URL**: `8.213.149.224`
   - **API_KEY**: 自动生成的唯一密钥
6. ❌ 失败 → 提示"未查询到交易"

---

## ✨ v2.0 新特性

### ✅ 已实现

| 功能 | 说明 | 状态 |
|------|------|------|
| **无需 API Key** | 使用 BaseScan 公开 API，无需注册 | ✅ |
| **容差范围检查** | 0.03-0.07 USDC 都有效（0.05 ± 0.02） | ✅ |
| **频率限制** | 10 次/分钟，50 次/小时，200 次/天 | ✅ |
| **数据库存储** | SQLite 存储所有发放记录 | ✅ |
| **访问日志** | 记录所有 API 调用 | ✅ |
| **HTTPS 支持** | 可选启用 HTTPS 加密 | ✅ |
| **统计数据** | 实时查看发放统计 | ✅ |
| **管理工具** | 禁用/启用/导出 API Key | ✅ |

---

## 📦 安装依赖

```bash
# 安装 Python 依赖
pip3 install flask requests flask-limiter

# 或使用 requirements.txt
pip3 install -r requirements.txt
```

---

## 🚀 快速开始

### 方式 1: HTTP 模式（开发/测试）

```bash
cd /home/admin/Ziwei/projects/x402-api
python3 api_key_server.py
```

**访问：** http://localhost:8080

### 方式 2: HTTPS 模式（生产环境）

```bash
# 1. 生成 SSL 证书
./generate-ssl-cert.sh

# 2. 修改配置（api_key_server.py）
CONFIG["HTTPS_ENABLED"] = True

# 3. 启动服务
python3 api_key_server.py
```

**访问：** https://localhost:4433

---

## ⚙️ 配置说明

**文件：** `api_key_server.py`

```python
CONFIG = {
    "PAYMENT_ADDRESS": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
    "EXPECTED_AMOUNT": 0.05,  # 期望金额 USDC
    "TOLERANCE": 0.02,  # 容差范围 ±0.02
    "REAL_API_URL": "8.213.149.224",  # 真实 API 地址
    "BASESCAN_API_KEY": "",  # 留空使用公开 API（无需注册）
    "TIME_WINDOW": 300,  # 5 分钟内交易有效
    "DB_PATH": "api_keys.db",  # 数据库路径
    "HTTPS_ENABLED": False,  # 是否启用 HTTPS
    "SSL_CERT": "cert.pem",
    "SSL_KEY": "key.pem",
}
```

### 🎯 关键配置说明

**1. BASESCAN_API_KEY（可选）**
- **留空**：使用公开 API，无需注册（推荐）
- **填写**：使用自己的 API Key，速率限制更高

**获取 API Key（可选）：**
- 访问 https://basescan.org/myapikey
- 免费注册
- 创建 API Key
- 填入配置

**2. 容差范围**
```python
# 金额检查逻辑
min_amount = EXPECTED_AMOUNT - TOLERANCE  # 0.03 USDC
max_amount = EXPECTED_AMOUNT + TOLERANCE  # 0.07 USDC

# 只要金额在 [0.03, 0.07] 范围内都有效
if amount < min_amount or amount > max_amount:
    # 拒绝
else:
    # 接受
```

**3. 频率限制**
```python
# 默认限制
default_limits=["200 per day", "50 per hour"]

# 验证端点限制
@limiter.limit("10 per minute")  # 每分钟最多 10 次验证
```

---

## 📊 数据库管理

### 查看统计数据

```bash
python3 db_manager.py --stats
```

**输出示例：**
```
============================================================
📊 x402 API Key 统计数据
============================================================
总发放数量：    156
今日发放：      23
禁用数量：      5
总收入：        7.8000 USDC
平均金额：      0.0500 USDC
最大单笔：      0.0700 USDC
============================================================
```

### 列出最近的 API Key

```bash
python3 db_manager.py --list --limit 20
```

### 导出为 CSV

```bash
python3 db_manager.py --export --output my_export.csv
```

### 禁用/启用 API Key

```bash
# 禁用
python3 db_manager.py --disable x402_a1b2c3d4e5f67890_1709625600

# 启用
python3 db_manager.py --enable x402_a1b2c3d4e5f67890_1709625600
```

### 搜索记录

```bash
# 按交易哈希搜索
python3 db_manager.py --search 0x1234567890abcdef

# 按 API Key 搜索
python3 db_manager.py --search x402_a1b2c3
```

---

## 🔐 安全特性

### 1. 频率限制（已实现）

```python
# 全局限制
default_limits=["200 per day", "50 per hour"]

# 端点限制
@app.route("/api/verify", methods=["POST"])
@limiter.limit("10 per minute")  # 每分钟 10 次
def api_verify():
    ...
```

### 2. HTTPS 加密（可选）

**生成证书：**
```bash
./generate-ssl-cert.sh
```

**启用 HTTPS：**
```python
CONFIG["HTTPS_ENABLED"] = True
```

**生产环境建议：**
- 使用 Let's Encrypt 免费证书
- 配置 Nginx 反向代理
- 强制 HTTPS 重定向

### 3. 数据库存储（已实现）

**表结构：**
```sql
CREATE TABLE api_keys (
    id INTEGER PRIMARY KEY,
    api_key TEXT UNIQUE NOT NULL,
    api_base_url TEXT NOT NULL,
    tx_hash TEXT UNIQUE NOT NULL,
    amount REAL NOT NULL,
    from_address TEXT,
    timestamp INTEGER NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    is_active INTEGER DEFAULT 1
);
```

**访问日志：**
```sql
CREATE TABLE access_logs (
    id INTEGER PRIMARY KEY,
    ip_address TEXT,
    endpoint TEXT,
    status TEXT,
    message TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

### 4. 生产环境建议

**添加 IP 白名单：**
```python
ALLOWED_IPS = ["127.0.0.1", "192.168.1.0/24"]

@app.before_request
def check_ip():
    if request.remote_addr not in ALLOWED_IPS:
        return jsonify({"error": "Access denied"}), 403
```

**添加请求签名：**
```python
import hmac

def verify_signature(payload, signature, secret):
    expected = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)
```

**使用环境变量：**
```python
import os

CONFIG = {
    "PAYMENT_ADDRESS": os.getenv("PAYMENT_ADDRESS"),
    "BASESCAN_API_KEY": os.getenv("BASESCAN_API_KEY"),
    "SECRET_SALT": os.getenv("SECRET_SALT"),
}
```

---

## 📋 API 端点

| 端点 | 方法 | 限制 | 说明 |
|------|------|------|------|
| `/` | GET | 100/天 | 前端页面 |
| `/api/verify` | POST | 10/分钟 | 验证交易 |
| `/api/status` | GET | 60/分钟 | 状态检查 |
| `/api/transactions` | GET | 30/分钟 | 交易记录 |
| `/api/stats` | GET | 30/分钟 | 统计数据 |

---

## 💡 使用示例

### 完整用户流程

**1. 启动服务**
```bash
cd /home/admin/Ziwei/projects/x402-api
python3 api_key_server.py
```

**2. 用户访问网页**
```
http://8.213.149.224:8080
```

**3. 用户支付 USDC**
- 打开钱包（MetaMask 等）
- 发送 **0.03-0.07 USDC** 到 `0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb`
- 使用 Base 网络（ERC-20 USDC）
- 等待 15-30 秒确认

**4. 用户验证交易**
- 点击"验证交易并获取密钥"按钮
- 等待 10-30 秒

**5. 获得凭证**
```
✅ 验证成功！

API_BASE_URL: 8.213.149.224
API_KEY: x402_a1b2c3d4e5f67890_1709625600

交易哈希：0x1234567890abcdef
支付金额：0.05 USDC
```

**6. 开始调用 API**
```python
import requests

response = requests.post(
    "http://8.213.149.224/api/v1/translator",
    json={"text": "Hello!", "source": "en", "target": "zh"},
    headers={
        "X-API-Key": "x402_a1b2c3d4e5f67890_1709625600",
        "X-Payment-Amount": "20000",
        "X-Payment-Token": "USDC"
    }
)
print(response.json())
```

---

## 🔍 故障排查

### 问题 1: 查询不到交易

**可能原因：**
- 交易尚未确认（等待 30-60 秒）
- 金额不在容差范围内（需要 0.03-0.07 USDC）
- 使用了错误的网络（必须用 Base 网络）

**解决方案：**
1. 等待交易确认
2. 检查发送金额
3. 确认使用 Base 网络 USDC

### 问题 2: 达到频率限制

**错误信息：**
```json
{
  "error": "Rate Limit Exceeded",
  "message": "请求过于频繁，请稍后重试"
}
```

**解决方案：**
- 等待 1 分钟后重试
- 或修改配置提高限制

### 问题 3: 数据库锁定

**错误信息：**
```
sqlite3.OperationalError: database is locked
```

**解决方案：**
```bash
# 重启服务
pkill -f api_key_server.py
python3 api_key_server.py
```

---

## 📄 文件清单

| 文件 | 用途 | 大小 |
|------|------|------|
| `api-key-generator.html` | 前端页面 | ~17KB |
| `api_key_server.py` | Web 服务（主程序） | ~16KB |
| `api_key_generator.py` | 命令行工具 | ~10KB |
| `db_manager.py` | 数据库管理 | ~7KB |
| `generate-ssl-cert.sh` | SSL 证书生成 | ~1KB |
| `start-api-key-server.sh` | 快速启动脚本 | ~1KB |
| `API_KEY_SYSTEM_README.md` | 完整文档 | 本文件 |
| `api_keys.db` | SQLite 数据库 | 运行时生成 |

---

## 🎨 自定义配置

### 修改支付金额范围

```python
CONFIG["EXPECTED_AMOUNT"] = 0.10  # 改为 0.10 USDC
CONFIG["TOLERANCE"] = 0.03  # 容差 ±0.03
# 有效范围：0.07 - 0.13 USDC
```

### 修改时间窗口

```python
CONFIG["TIME_WINDOW"] = 600  # 改为 10 分钟
```

### 修改频率限制

```python
# 在 api_key_server.py 中修改
@limiter.limit("20 per minute")  # 改为每分钟 20 次
```

### 修改数据库路径

```python
CONFIG["DB_PATH"] = "/var/lib/x402/api_keys.db"
```

---

## 📊 监控与告警

### 查看实时日志

```bash
tail -f /var/log/x402_api_server.log
```

### 监控服务状态

```bash
# 健康检查
curl http://localhost:8080/api/status

# 查看统计
curl http://localhost:8080/api/stats
```

### 设置告警（示例）

```python
# 添加告警逻辑
if today_keys > 100:
    send_alert("今日发放超过 100 个！")

if total_revenue > 10:
    send_alert("总收入超过 10 USDC！")
```

---

## 🔗 相关文档

- [QUICK_START.md](QUICK_START.md) - 快速开始指南
- [CUSTOMER_API_GUIDE.md](CUSTOMER_API_GUIDE.md) - 客户调用指南
- [README.md](README.md) - 项目总览

---

## 💬 技术支持

**问题反馈：**
- GitHub Issues: https://github.com/ziwei-control/ziwei-archive/issues
- 邮箱：contact@x402.network

**文档更新：** 2026-03-05  
**版本：** v2.0.0

---

**开始自动发放 API 密钥吧！🚀**
