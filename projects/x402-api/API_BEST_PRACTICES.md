# x402 API 最佳实践指南

## 📋 目录
- [安全集成](#安全集成)
- [错误处理](#错误处理)
- [性能优化](#性能优化)
- [成本控制](#成本控制)
- [调试技巧](#调试技巧)

## 🔒 安全集成

### 1. 私钥保护
```python
# ❌ 错误：硬编码私钥
WALLET_KEY = "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"

# ✅ 正确：环境变量或配置文件
import os
WALLET_KEY = os.getenv('X402_WALLET_KEY')
```

### 2. 请求验证
始终验证 API 响应中的 x402 头信息：
```python
response = requests.post(api_url, json=payload)
x402_info = response.headers.get('x-x402')
if not x402_info:
    raise Exception("Invalid x402 response")
```

## 🚨 错误处理

### 常见错误码
| 状态码 | 含义 | 处理建议 |
|--------|------|----------|
| 402 | 付款要求 | 检查钱包余额和网络 |
| 429 | 请求频率过高 | 实现指数退避重试 |
| 500 | 服务器错误 | 等待后重试 |

### 重试策略
```python
import time
import random

def call_with_retry(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            # 指数退避 + 随机抖动
            delay = (2 ** attempt) + random.uniform(0, 1)
            time.sleep(delay)
```

## ⚡ 性能优化

### 1. 批量处理
对于多个相似请求，考虑批量处理以减少调用次数：
```python
# ❌ 低效：多次调用
results = []
for item in items:
    result = call_api(item)
    results.append(result)

# ✅ 高效：单次调用处理多个项目
results = call_api_batch(items)
```

### 2. 缓存策略
对不经常变化的结果实施缓存：
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_cached_analysis(text_hash):
    return call_api({"text": text_hash})
```

## 💰 成本控制

### 1. 预算监控
设置每日/每月预算限制：
```python
DAILY_BUDGET = 10.0  # USDC
daily_spent = get_daily_spending()
if daily_spent >= DAILY_BUDGET:
    disable_non_essential_calls()
```

### 2. 选择合适的端点
根据需求选择性价比最高的端点：
- `translator` ($0.02): 简单翻译
- `long-text` ($0.03): 文档分析  
- `logic` ($0.06): 复杂推理
- `architect` ($0.10): 架构设计

## 🐞 调试技巧

### 1. 日志记录
记录关键请求和响应用于调试：
```python
import logging

logger = logging.getLogger(__name__)
logger.info(f"API Request: {payload}")
logger.info(f"API Response: {response.json()}")
```

### 2. 测试模式
在开发阶段使用测试模式：
```bash
# 设置测试环境变量
export X402_TEST_MODE=true
```

## 📊 监控指标

### 关键指标
- **成功率**: 目标 > 99%
- **响应时间**: 目标 < 2s  
- **成本效率**: 每 USDC 的处理量
- **错误率**: 目标 < 1%

### 报告生成
使用我们的自动收入报告脚本：
```bash
python3 /home/admin/Ziwei/scripts/x402-daily-revenue.py
```

---

**最后更新**: 2026-03-05  
**版本**: v1.0  
**维护者**: 紫微智控 AI Assistant