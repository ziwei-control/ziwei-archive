# 🔍 x402 API 密钥验证逻辑详解

**最后更新：** 2026-03-06  
**版本：** v2.1.0

---

## 📋 验证流程概览

```
用户点击"验证交易"
    ↓
前端发送请求到 /api/verify
    ↓
后端查询 BaseScan API
    ↓
检查收款地址的交易记录
    ↓
逐条验证交易（5 个检查点）
    ↓
✅ 成功 → 生成 API Key → 保存到数据库 → 返回凭证
❌ 失败 → 返回错误信息
```

---

## 🔐 5 个验证检查点

### 检查点 1：数据库缓存检查 ⚡

**目的：** 避免重复验证，提高响应速度

```python
# 先检查数据库是否已存在
if tx_hash:
    cached = get_api_key(tx_hash)
    if cached:
        return {
            "success": True,
            "message": "验证成功（缓存）",
            "api_base_url": cached["api_base_url"],
            "api_key": cached["api_key"],
            "cached": True
        }
```

**逻辑：**
- 如果该交易哈希已验证过，直接返回缓存的 API Key
- 避免重复生成和查询

---

### 检查点 2：查询 BaseScan API 🔗

**目的：** 获取收款地址的所有交易记录

```python
def query_basescan(address: str) -> dict:
    url = "https://api.basescan.org/api"
    params = {
        "module": "account",
        "action": "tokentx",
        "address": address,  # 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb
        "startblock": 0,
        "endblock": 99999999,
        "sort": "desc"  # 最新的交易在前
    }
    
    response = requests.get(url, params=params, timeout=30)
    return response.json()
```

**返回数据示例：**
```json
{
  "status": "1",
  "message": "OK",
  "result": [
    {
      "hash": "0x1234567890abcdef...",
      "from": "0xUserAddress...",
      "to": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
      "value": "50000",
      "tokenSymbol": "USDC",
      "tokenName": "USD Coin",
      "tokenDecimal": "6",
      "timeStamp": "1709625600"
    },
    ...
  ]
}
```

**失败处理：**
```python
if data.get("status") != "1" or not data.get("result"):
    return {
        "success": False,
        "message": "未查询到交易记录，请确保已发送 USDC"
    }
```

---

### 检查点 3：USDC 代币检查 💰

**目的：** 确保是 USDC 交易，不是其他代币

```python
for tx in results:
    token_symbol = tx.get("tokenSymbol", "")
    token_name = tx.get("tokenName", "")
    
    is_usdc = (token_symbol in ["USDC", "USD Coin"] or 
               "USD Coin" in token_name or
               token_symbol == "USDC.e")
    
    if not is_usdc:
        continue  # 跳过非 USDC 交易
```

**支持的 USDC 类型：**
- `USDC` - Base 链原生 USDC
- `USD Coin` - 完整名称
- `USDC.e` - 桥接 USDC

**拒绝的交易：**
- ETH 转账
- 其他 ERC20 代币
- NFT 转账

---

### 检查点 4：金额容差检查 📊

**目的：** 确保支付金额在可接受范围内

```python
# 容差范围：0.05 ± 0.02 USDC
min_amount = 0.05 - 0.02  # 0.03 USDC
max_amount = 0.05 + 0.02  # 0.07 USDC

# 计算实际金额
decimal = int(tx.get("tokenDecimal", 6))  # USDC 是 6 位小数
value = int(tx.get("value", 0))
amount = value / (10 ** decimal)

# 金额检查
if amount < min_amount or amount > max_amount:
    print(f"⚠️ 金额不符合：{amount} USDC (需要 {min_amount}-{max_amount})")
    continue
```

**有效金额范围：**
- ✅ 0.03 USDC - 最小可接受
- ✅ 0.04 USDC
- ✅ 0.05 USDC - 期望金额
- ✅ 0.06 USDC
- ✅ 0.07 USDC - 最大可接受

**拒绝的金额：**
- ❌ 0.02 USDC - 太少
- ❌ 0.08 USDC - 太多
- ❌ 1.00 USDC - 远超范围

**为什么需要容差？**
- 用户可能手动输入金额
- 避免过于严格导致验证失败
- 允许用户多付（作为小费或未来使用）

---

### 检查点 5：时间窗口检查 ⏰

**目的：** 确保交易是最近发生的，防止重用旧交易

```python
TIME_WINDOW = 300  # 5 分钟（秒）

now = time.time()
tx_time = int(tx.get("timeStamp", 0))

if (now - tx_time) > TIME_WINDOW:
    print(f"⚠️ 交易超时：{tx_time}")
    continue
```

**时间窗口：5 分钟**

**示例：**
```
当前时间：2026-03-06 09:00:00
有效交易时间范围：2026-03-06 08:55:00 - 09:00:00

交易时间戳：2026-03-06 08:56:00 ✅ 有效（4 分钟前）
交易时间戳：2026-03-06 08:54:00 ❌ 无效（6 分钟前，超时）
```

**为什么需要时间窗口？**
- 防止同一笔交易被多次使用
- 确保用户刚刚完成支付
- 保护系统免受重放攻击

---

## 🔑 API Key 生成算法

**所有检查通过后，生成唯一的 API Key：**

```python
def generate_api_key(tx_hash: str, timestamp: int) -> str:
    """
    生成唯一的 API Key
    
    算法：SHA256(tx_hash + timestamp + salt)
    格式：x402_{hash}_{timestamp}
    """
    salt = "x402_secret_salt_2026_production"
    data = f"{tx_hash}{timestamp}{salt}"
    
    hash_obj = hashlib.sha256(data.encode())
    hash_hex = hash_obj.hexdigest()[:16]
    
    return f"x402_{hash_hex}_{timestamp:x}"
```

**生成示例：**
```
输入：
  tx_hash = "0x1234567890abcdef..."
  timestamp = 1709625600

输出：
  API_KEY = "x402_a1b2c3d4e5f67890_65f8a000"
```

**特点：**
- ✅ **唯一性** - 每笔交易生成不同的 Key
- ✅ **确定性** - 相同输入产生相同输出
- ✅ **可追溯** - 可通过 Key 反查交易
- ✅ **安全性** - 使用 SHA256 哈希 + 盐值

---

## 💾 数据库存储

**验证成功后，保存到 SQLite 数据库：**

```python
def save_api_key(api_key, api_base_url, tx_hash, amount, from_address, timestamp):
    conn = sqlite3.connect("api_keys.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT OR REPLACE INTO api_keys 
        (api_key, api_base_url, tx_hash, amount, from_address, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (api_key, api_base_url, tx_hash, amount, from_address, timestamp))
    
    conn.commit()
    conn.close()
```

**数据库表结构：**
```sql
CREATE TABLE api_keys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
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

**为什么要存储？**
- ✅ 支持重复验证（缓存）
- ✅ 审计和追踪
- ✅ 统计分析
- ✅ 禁用恶意 Key

---

## 📤 返回结果

**成功响应：**
```json
{
  "success": true,
  "message": "验证成功",
  "api_base_url": "8.213.149.224",
  "api_key": "x402_a1b2c3d4e5f67890_65f8a000",
  "tx_hash": "0x1234567890abcdef...",
  "amount": 0.05,
  "timestamp": 1709625600,
  "from_address": "0xUserAddress..."
}
```

**失败响应：**
```json
{
  "success": false,
  "message": "未找到符合条件的交易，请发送 0.05 USDC (容差：±0.02) 到指定地址"
}
```

---

## 🔄 完整流程图

```
┌─────────────┐
│  用户点击    │
│ "验证交易"   │
└──────┬──────┘
       │
       ▼
┌─────────────────────────┐
│  前端发送 POST 请求      │
│  /api/verify            │
└──────┬──────────────────┘
       │
       ▼
┌─────────────────────────┐
│  检查数据库缓存          │
│  是否已存在该 tx_hash？  │
└──────┬──────────────────┘
       │
    ┌──┴──┐
    │ 是  │───────────┐
    └─────┘           │
       │              │
       ▼              ▼
    ┌─────┐      ┌─────────────┐
    │ 否  │      │ 返回缓存的   │
    └──┬──┘      │ API Key     │
       │         └─────────────┘
       ▼
┌─────────────────────────┐
│  调用 BaseScan API       │
│  查询收款地址交易记录    │
└──────┬──────────────────┘
       │
       ▼
┌─────────────────────────┐
│  遍历交易记录（最新优先）│
└──────┬──────────────────┘
       │
       ▼
┌─────────────────────────┐
│  检查点 1: USDC 代币？   │──────❌ 跳过
└──────┬──────────────────┘
       │✅
       ▼
┌─────────────────────────┐
│  检查点 2: 金额在范围内？│──────❌ 跳过
│  (0.03 - 0.07 USDC)     │
└──────┬──────────────────┘
       │✅
       ▼
┌─────────────────────────┐
│  检查点 3: 时间在窗口内？│──────❌ 跳过
│  (5 分钟内)             │
└──────┬──────────────────┘
       │✅
       ▼
┌─────────────────────────┐
│  生成 API Key            │
│  SHA256(tx+time+salt)   │
└──────┬──────────────────┘
       │
       ▼
┌─────────────────────────┐
│  保存到数据库            │
│  api_keys.db            │
└──────┬──────────────────┘
       │
       ▼
┌─────────────────────────┐
│  返回 API 凭证给前端      │
│  - API_BASE_URL         │
│  - API_KEY              │
└─────────────────────────┘
```

---

## 🛡️ 安全特性

### 1. 防重放攻击
- ✅ 时间窗口限制（5 分钟）
- ✅ 交易哈希唯一性检查
- ✅ 数据库记录已验证的交易

### 2. 防滥用
- ✅ 频率限制（10 次/分钟）
- ✅ IP 地址记录
- ✅ 访问日志

### 3. 数据完整性
- ✅ SHA256 哈希算法
- ✅ 盐值保护
- ✅ 数据库事务

### 4. 可追溯性
- ✅ 所有验证记录保存
- ✅ 交易哈希关联
- ✅ 发送方地址记录

---

## 📊 常见失败原因

### ❌ "未查询到交易记录"

**原因：**
- 交易尚未确认（等待 15-30 秒）
- 使用了错误的收款地址
- 网络问题导致 BaseScan 查询失败

**解决方案：**
- 等待交易确认
- 检查收款地址是否正确
- 稍后重试

---

### ❌ "金额不符合"

**原因：**
- 发送金额 < 0.03 USDC
- 发送金额 > 0.07 USDC
- 使用了错误的代币（如 ETH）

**解决方案：**
- 发送 0.03-0.07 USDC
- 确保使用 USDC（Base 网络）

---

### ❌ "交易超时"

**原因：**
- 交易时间超过 5 分钟
- 验证太晚

**解决方案：**
- 支付后立即点击验证
- 如超时，重新发送一笔新的 USDC

---

## 🎯 最佳实践

### 用户侧
1. ✅ 支付后等待 15-30 秒（让交易确认）
2. ✅ 在 5 分钟内点击验证
3. ✅ 确保使用 Base 网络 USDC
4. ✅ 金额控制在 0.03-0.07 USDC

### 运营侧
1. ✅ 定期检查数据库记录
2. ✅ 监控异常验证请求
3. ✅ 备份 api_keys.db
4. ✅ 查看访问日志分析

---

## 📈 性能优化

### 当前性能
- BaseScan 查询：~2-5 秒
- 验证逻辑：< 1 秒
- 数据库操作：< 0.1 秒
- **总耗时：3-6 秒**

### 优化建议
1. **缓存 BaseScan 结果** - 减少 API 调用
2. **异步验证** - 提升用户体验
3. **CDN 加速** - 全球用户访问
4. **数据库索引** - 加速查询

---

## 🔗 相关代码

**核心文件：**
- `api_key_server.py` - 验证逻辑实现
- `get-api-key.html` - 前端页面
- `db_manager.py` - 数据库管理

**API 端点：**
- `POST /api/verify` - 验证交易
- `GET /api/status` - 状态检查
- `GET /api/transactions` - 交易记录
- `GET /api/stats` - 统计数据

---

**这就是完整的验证逻辑！** 🎉

如有问题，请提交 GitHub Issue：https://github.com/ziwei-control/ziwei-archive/issues
