# 🤖 x402 API 技术架构说明

**最后更新：** 2026-03-06  
**版本：** v2.0.0

---

## 🎯 技术架构总览

```
用户
  ↓
8090 端口 - API 密钥获取页面
  ↓ 支付 USDC
  ↓ 验证交易
  ↓ 获得 API Key
8091 端口 - 用户登录验证
  ↓ 输入地址+hash
  ↓ 验证通过
  ↓ 显示 API Key
5002 端口 - AI API 服务
  ↓ 使用 API Key 调用
  ↓ OpenClaw 云模型
  ↓ 返回 AI 结果
```

---

## 🔧 核心组件

### 1. API 密钥发放系统（8090 端口）

**功能：**
- ✅ USDC 支付验证
- ✅ BaseScan 区块链查询
- ✅ API Key 生成（SHA256+Salt）
- ✅ 数据库存储（SQLite）

**技术栈：**
- Flask Web 服务
- SQLite 数据库
- BaseScan API（公开）
- 加密算法：SHA256

**文件：**
- `api_key_server.py` - 主服务
- `get-api-key.html` - 前端页面

---

### 2. 用户登录验证系统（8091 端口）

**功能：**
- ✅ 用户登录（地址+hash 验证）
- ✅ 管理员登录（加密密码）
- ✅ 仪表板显示
- ✅ 统计数据

**技术栈：**
- Flask Web 服务
- SQLite 数据库
- BaseScan API 验证
- bcrypt 密码加密

**文件：**
- `x402_dashboard.py` - 主服务

---

### 3. AI API 服务（5002 端口）

**功能：**
- ✅ 8 个 AI API 端点
- ✅ API Key 验证
- ✅ 支付验证
- ✅ OpenClaw 云模型集成
- ✅ 调用日志记录

**技术栈：**
- Flask Web 服务
- OpenClaw 云模型
- SQLite 日志存储
- RESTful API

**文件：**
- `x402_api_server.py` - 主服务

---

## 🤖 OpenClaw 云模型集成

### 模型映射表

| x402 API 端点 | OpenClaw 模型 | 说明 | 价格 |
|--------------|--------------|------|------|
| `/api/v1/translator` | `t5-translator` | 通义千问翻译模型 | $0.02 |
| `/api/v1/code-gen` | `t2-coder` | 通义千问代码模型 | $0.08 |
| `/api/v1/code-audit` | `t3-auditor` | 通义千问审计模型 | $0.05 |
| `/api/v1/architect` | `t1-architect` | 通义千问架构模型 | $0.10 |
| `/api/v1/logic` | `t4-logic` | 通义千问逻辑模型 | $0.06 |
| `/api/v1/long-text` | `t6-reader` | 通义千问阅读模型 | $0.03 |
| `/api/v1/crawl` | `t4-logic` + web_fetch | 爬虫 + 解析 | $0.04 |
| `/api/v1/vision` | 视觉模型（待集成） | 图像分析 | $0.15 |

### OpenClaw 模型别名

```python
MODEL_ALIASES = {
    'qwen': 'qwen-portal/coder-model',
    't1-architect': 'bailian/qwen3-max',
    't2-coder': 'bailian/qwen3-coder-plus',
    't3-auditor': 'bailian/qwen3-coder-next',
    't4-logic': 'bailian/qwen3.5-plus',
    't5-translator': 'bailian/glm-4.7',
    't6-reader': 'bailian/kimi-k2.5'
}
```

### 调用流程

```python
# 1. 用户请求
POST /api/v1/translator
Headers:
  X-API-Key: x402_xxxxx
  X-Payment-Amount: 20000
  X-Payment-Token: USDC
Body:
  {
    "text": "Hello",
    "source": "en",
    "target": "zh"
  }

# 2. 验证 API Key
verify_api_key(api_key) → 查询数据库

# 3. 验证支付金额
check_payment(amount) → 对比价格表

# 4. 调用 OpenClaw
prompt = "Translate from en to zh: Hello"
result = call_openclaw_model('t5-translator', prompt)

# 5. 返回结果
{
  "success": true,
  "data": {
    "translated_text": "你好"
  },
  "cost": "0.02 USDC"
}

# 6. 记录日志
log_api_call(api_key, endpoint, cost, success)
```

---

## 💰 计费系统

### 价格表

| API | 价格 | OpenClaw 成本 | 利润率 |
|-----|------|--------------|--------|
| 翻译 | $0.02 | ~$0.005 | ~75% |
| 代码生成 | $0.08 | ~$0.02 | ~75% |
| 代码审计 | $0.05 | ~$0.015 | ~70% |
| 架构设计 | $0.10 | ~$0.025 | ~75% |
| 逻辑推理 | $0.06 | ~$0.015 | ~75% |
| 长文解析 | $0.03 | ~$0.008 | ~73% |
| 网络爬虫 | $0.04 | ~$0.01 | ~75% |
| 视觉解析 | $0.15 | ~$0.04 | ~73% |

**利润率说明：**
- OpenClaw 成本基于 API 调用成本估算
- x402 定价包含运营成本、利润空间
- 平均利润率约 70-75%

### 支付验证

```python
# 用户支付 0.05 USDC 获取 API Key
# 每次调用 API 扣除相应费用

# 示例：用户调用 5 次翻译 API
5 × $0.02 = $0.10 USDC

# 如果用户支付的 0.05 USDC 用完
# 需要重新支付获取新的 API Key
```

---

## 🔐 安全机制

### 1. API Key 生成

```python
# 算法：SHA256(tx_hash + timestamp + salt)
salt = "x402_secret_salt_2026_production"
data = f"{tx_hash}{timestamp}{salt}"
hash_hex = hashlib.sha256(data.encode()).hexdigest()[:16]
api_key = f"x402_{hash_hex}_{timestamp:x}"

# 示例输出：x402_b7a86ee8952951ad_69aa44a4
```

### 2. 密码加密（管理员）

```python
# 算法：SHA256(password + salt)
salt = "x402_admin_salt_2026_production"
password = "0909opop!"
password_hash = hashlib.sha256(f"{password}{salt}".encode()).hexdigest()

# 数据库中存储：password_hash + salt
# 不存储明文密码
```

### 3. 频率限制

```python
# 每个 API Key 每分钟最多调用 60 次
RATE_LIMIT = 60  # calls per minute

# 防止滥用和 DDoS 攻击
```

### 4. 请求验证

```python
# 必须包含的请求头
headers = {
    "X-API-Key": "必填",
    "X-Payment-Amount": "必填",
    "X-Payment-Token": "必填 (仅支持 USDC)",
    "Content-Type": "application/json"
}
```

---

## 📊 数据库结构

### api_keys 表

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

### admins 表

```sql
CREATE TABLE admins (
    id INTEGER PRIMARY KEY,
    address TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    salt TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    is_active INTEGER DEFAULT 1
);
```

### api_logs 表

```sql
CREATE TABLE api_logs (
    id INTEGER PRIMARY KEY,
    api_key TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    cost REAL NOT NULL,
    success INTEGER DEFAULT 1,
    timestamp INTEGER NOT NULL
);
```

---

## 🚀 完整调用示例

### Python 示例

```python
import requests

# 配置
API_BASE_URL = "http://8.213.149.224:5002"
API_KEY = "x402_b7a86ee8952951ad_69aa44a4"  # 从 8090 端口获取

# 调用翻译 API
response = requests.post(
    f"{API_BASE_URL}/api/v1/translator",
    json={
        "text": "Hello, world!",
        "source": "en",
        "target": "zh"
    },
    headers={
        "X-API-Key": API_KEY,
        "X-Payment-Amount": "20000",  # 0.02 USDC
        "X-Payment-Token": "USDC"
    }
)

result = response.json()
print(f"翻译结果：{result['data']['translated_text']}")
print(f"花费：{result['cost']}")
```

### JavaScript 示例

```javascript
const API_BASE_URL = "http://8.213.149.224:5002";
const API_KEY = "x402_b7a86ee8952951ad_69aa44a4";

const response = await fetch(`${API_BASE_URL}/api/v1/code-gen`, {
    method: "POST",
    headers: {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY,
        "X-Payment-Amount": "80000",
        "X-Payment-Token": "USDC"
    },
    body: JSON.stringify({
        prompt: "用 Python 写一个快速排序",
        language: "python"
    })
});

const result = await response.json();
console.log(`生成的代码：${result.data.code}`);
console.log(`花费：${result.cost}`);
```

---

## 📈 监控和统计

### Dashboard 监控（8091 端口）

- 🔑 总发放数量
- 📈 今日发放
- 💰 总收入
- 💵 平均金额
- 📋 最近记录

### API 日志查询

```sql
-- 查询今日 API 调用统计
SELECT endpoint, COUNT(*) as calls, SUM(cost) as revenue
FROM api_logs
WHERE DATE(timestamp) = DATE('now')
GROUP BY endpoint;

-- 查询某个用户的所有调用
SELECT * FROM api_logs
WHERE api_key = 'x402_xxxxx'
ORDER BY timestamp DESC;
```

---

## 🔧 部署配置

### 服务启动脚本

```bash
#!/bin/bash
# start-all-services.sh

# 启动 API 密钥发放服务（8090）
nohup python3 /home/admin/Ziwei/projects/x402-api/api_key_server.py > /tmp/api_key.log 2>&1 &

# 启动用户登录验证（8091）
nohup python3 /home/admin/Ziwei/projects/x402-api/x402_dashboard.py > /tmp/dashboard.log 2>&1 &

# 启动 AI API 服务（5002）
nohup python3 /home/admin/Ziwei/projects/x402-api/x402_api_server.py > /tmp/x402_api.log 2>&1 &

echo "✅ 所有服务已启动"
echo "8090 - API 密钥获取"
echo "8091 - 用户登录验证"
echo "5002 - AI API 服务"
```

### 端口分配

| 端口 | 服务 | 用途 |
|------|------|------|
| 8090 | api_key_server.py | API 密钥发放 |
| 8091 | x402_dashboard.py | 用户登录验证 |
| 5002 | x402_api_server.py | AI API 服务 |

---

## 📚 相关文档

- [API_USAGE_GUIDE.md](API_USAGE_GUIDE.md) - API 使用指南
- [VERIFICATION_LOGIC.md](VERIFICATION_LOGIC.md) - 验证逻辑详解
- [API_KEY_SYSTEM_README.md](API_KEY_SYSTEM_README.md) - 密钥系统说明
- [OFFICIAL_LINKS.md](OFFICIAL_LINKS.md) - 官方链接汇总

---

## 🎯 总结

**x402 API 系统基于 OpenClaw 云模型提供 AI 服务：**

1. ✅ **支付系统** - USDC 区块链支付
2. ✅ **密钥管理** - SHA256 加密生成
3. ✅ **用户验证** - BaseScan 链上验证
4. ✅ **AI 服务** - OpenClaw 云模型支持
5. ✅ **计费系统** - 按次付费，透明计费
6. ✅ **监控系统** - 实时统计和日志

**技术支持：**
- OpenClaw 云模型（通义千问系列）
- Flask Web 框架
- SQLite 数据库
- BaseScan API

**立即开始：**
1. 访问 http://8.213.149.224:8090/get-api-key.html 获取 API Key
2. 使用 API Key 调用 http://8.213.149.224:5002 的 AI API
3. 访问 http://8.213.149.224:8091 查看使用统计

---

**开始构建你的 AI 应用吧！** 🚀
