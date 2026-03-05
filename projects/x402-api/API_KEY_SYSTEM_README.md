# x402 API 密钥自动发放系统

**功能：** 用户支付 USDC 后自动获取 API 访问凭证

---

## 🚀 系统架构

```
用户 → 访问网页 → 支付 USDC → 验证交易 → 生成 API Key → 返回凭证
```

### 核心组件

1. **前端页面** (`api-key-generator.html`)
   - 支付指引界面
   - 交易验证按钮
   - 凭证展示弹窗

2. **后端服务** (`api_key_server.py`)
   - Flask Web 服务
   - BaseScan API 查询
   - API Key 生成算法

3. **命令行工具** (`api_key_generator.py`)
   - 手动验证交易
   - 自动监控模式
   - 批量处理

---

## 📦 安装依赖

```bash
# 安装 Python 依赖
pip3 install flask requests

# 或使用 requirements.txt
pip3 install -r requirements.txt
```

---

## ⚙️ 配置

### 1. 获取 BaseScan API Key

1. 访问 https://basescan.org/myapikey
2. 注册账号（免费）
3. 创建 API Key
4. 复制到配置文件

### 2. 修改配置

**文件：** `api_key_server.py`

```python
CONFIG = {
    "PAYMENT_ADDRESS": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
    "EXPECTED_AMOUNT": 0.05,  # USDC
    "TOLERANCE": 0.02,  # 容差
    "REAL_API_URL": "8.213.149.224",
    "BASESCAN_API_KEY": "YourBaseScanApiKey",  # 替换这里
    "TIME_WINDOW": 300,  # 5 分钟
}
```

---

## 🎯 使用方式

### 方式 1: Web 服务（推荐）

**启动服务：**
```bash
cd /home/admin/Ziwei/projects/x402-api
python3 api_key_server.py
```

**访问页面：**
```
http://localhost:8080
```

**用户流程：**
1. 打开网页
2. 复制支付地址
3. 发送 0.05 USDC 到 `0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb`
4. 点击"验证交易并获取密钥"
5. 等待 10-30 秒
6. 获得 API_BASE_URL 和 API_KEY

### 方式 2: 命令行工具

**验证特定交易：**
```bash
python3 api_key_generator.py --tx-hash 0x1234567890abcdef
```

**查找最近的合格支付：**
```bash
python3 api_key_generator.py
```

**自动监控模式：**
```bash
python3 api_key_generator.py --auto-monitor
```

**输出示例：**
```
============================================================
✅ 验证成功！
============================================================
API_BASE_URL: 8.213.149.224
API_KEY: x402_a1b2c3d4e5f67890_1709625600
交易哈希：0x1234567890abcdef
支付金额：0.05 USDC
============================================================
```

---

## 📋 API 端点

### Web 服务提供的 API

**1. 状态检查**
```bash
curl http://localhost:8080/api/status
```

**响应：**
```json
{
  "status": "ok",
  "payment_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
  "expected_amount": 0.05,
  "tolerance": 0.02,
  "time_window": 300
}
```

**2. 验证交易**
```bash
curl -X POST http://localhost:8080/api/verify \
  -H "Content-Type: application/json" \
  -d '{"tx_hash": "0x1234567890abcdef"}'
```

**响应（成功）：**
```json
{
  "success": true,
  "message": "验证成功",
  "api_base_url": "8.213.149.224",
  "api_key": "x402_a1b2c3d4e5f67890_1709625600",
  "tx_hash": "0x1234567890abcdef",
  "amount": 0.05,
  "timestamp": 1709625600
}
```

**响应（失败）：**
```json
{
  "success": false,
  "message": "未找到符合条件的交易"
}
```

**3. 查询交易记录**
```bash
curl http://localhost:8080/api/transactions
```

---

## 🔐 API Key 生成算法

**算法说明：**
```python
def generate_api_key(tx_hash, timestamp):
    salt = "x402_secret_salt_2026"
    data = f"{tx_hash}{timestamp}{salt}"
    hash_hex = sha256(data)[:16]
    return f"x402_{hash_hex}_{timestamp:x}"
```

**特点：**
- ✅ 唯一性：每个交易生成不同的 Key
- ✅ 可追溯：可通过 Key 反查交易
- ✅ 安全性：使用 SHA256 哈希
- ✅ 确定性：相同输入产生相同输出

---

## 💡 自定义配置

### 修改支付金额

```python
CONFIG["EXPECTED_AMOUNT"] = 0.10  # 改为 0.10 USDC
```

### 修改容差范围

```python
CONFIG["TOLERANCE"] = 0.05  # 改为 ±0.05 USDC
```

### 修改时间窗口

```python
CONFIG["TIME_WINDOW"] = 600  # 改为 10 分钟
```

### 修改收款地址

```python
CONFIG["PAYMENT_ADDRESS"] = "0xYourNewAddress"
```

### 修改真实 API 地址

```python
CONFIG["REAL_API_URL"] = "your-real-api.com"
```

---

## 🛡️ 安全建议

### 生产环境部署

1. **使用 HTTPS**
   ```bash
   # 使用 Nginx 反向代理
   # 或配置 SSL 证书
   ```

2. **限制访问频率**
   ```python
   from flask_limiter import Limiter
   
   limiter = Limiter(app, key_func=lambda: request.remote_addr)
   
   @app.route("/api/verify", methods=["POST"])
   @limiter.limit("5 per minute")
   def api_verify():
       ...
   ```

3. **添加 IP 白名单**
   ```python
   ALLOWED_IPS = ["127.0.0.1", "192.168.1.0/24"]
   ```

4. **日志记录**
   ```python
   import logging
   logging.basicConfig(level=logging.INFO)
   ```

5. **数据库存储**
   - 记录所有发放的 API Key
   - 关联交易哈希
   - 便于审计和追踪

---

## 📊 监控与统计

### 查看交易记录

```bash
curl http://localhost:8080/api/transactions | jq
```

### 统计发放数量

```python
# 添加数据库后
SELECT COUNT(*) FROM api_keys WHERE date = TODAY;
```

### 监控服务状态

```bash
# 健康检查
curl http://localhost:8080/api/status

# 查看日志
tail -f /var/log/api_key_server.log
```

---

## 🐛 故障排查

### 问题 1: 查询不到交易

**可能原因：**
- BaseScan API Key 未配置
- 网络问题
- 交易尚未确认

**解决方案：**
1. 检查 API Key 配置
2. 等待 30-60 秒让交易确认
3. 检查网络连接

### 问题 2: 金额验证失败

**可能原因：**
- 发送金额不在容差范围内
- USDC 小数位错误

**解决方案：**
1. 确保发送 0.03-0.07 USDC
2. 使用 Base 网络 USDC（6 位小数）

### 问题 3: 服务无法启动

**可能原因：**
- 端口被占用
- 依赖未安装

**解决方案：**
```bash
# 检查端口
lsof -i :8080

# 安装依赖
pip3 install flask requests

# 更换端口
python3 api_key_server.py --port 8081
```

---

## 📝 使用示例

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
- 打开钱包
- 发送 0.05 USDC 到 `0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb`
- 等待确认

**4. 用户验证交易**
- 点击"验证交易并获取密钥"按钮
- 等待 10-30 秒

**5. 获得凭证**
```
API_BASE_URL: 8.213.149.224
API_KEY: x402_a1b2c3d4e5f67890_1709625600
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
```

---

## 🎨 前端自定义

### 修改页面样式

编辑 `api-key-generator.html` 中的 CSS 部分

### 修改支付地址显示

```javascript
const PAYMENT_ADDRESS = '0xYourNewAddress';
```

### 添加多语言支持

```javascript
const translations = {
    zh: { title: "x402 API 密钥获取", ... },
    en: { title: "x402 API Key Generator", ... }
};
```

---

## 📄 文件清单

| 文件 | 用途 | 大小 |
|------|------|------|
| `api-key-generator.html` | 前端页面 | ~17KB |
| `api_key_server.py` | Web 服务 | ~7KB |
| `api_key_generator.py` | 命令行工具 | ~10KB |
| `API_KEY_SYSTEM_README.md` | 使用说明 | 本文件 |

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
**版本：** v1.0.0

---

**开始自动发放 API 密钥吧！🚀**
