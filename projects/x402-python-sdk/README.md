# x402 Python SDK

让 Python 开发者轻松集成 x402 协议

## 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/ziwei/x402-python-sdk.git
cd x402-python-sdk

# 安装依赖
pip install -r requirements.txt
```

### 基础使用

```python
from x402 import X402Client

# 创建客户端
client = X402Client(
    api_base_url="http://localhost:5000",
    wallet_address="0x..."
)

# 调用 API（自动处理支付）
result = client.request_with_payment(
    endpoint="/api/v1/code-audit",
    json_data={
        "code": "def hello(): pass",
        "language": "Python"
    }
)

print(result['result'])
```

## 功能

- ✅ 自动处理 HTTP 402 支付请求
- ✅ 支付证明生成和验证
- ✅ 简化的 API 调用
- ✅ 错误处理
- ✅ 统计信息查询

## API 端点

| 端点 | 价格 |
|------|------|
| `/api/v1/architect` | $0.10 |
| `/api/v1/code-gen` | $0.08 |
| `/api/v1/code-audit` | $0.05 |
| `/api/v1/logic` | $0.06 |
| `/api/v1/translate` | $0.02 |
| `/api/v1/long-text` | $0.03 |
| `/api/v1/crawl` | $0.04 |
| `/api/v1/vision` | $0.15 |

## 示例

查看 `examples/` 目录获取更多示例：

- `basic_usage.py` - 基础使用
- `web_integration.py` - Web 应用集成
- `ai_agent_integration.py` - AI 智能体集成

## 文档

完整文档请查看 `docs/` 目录：

- `quick_start.md` - 快速开始
- `api_reference.md` - API 参考
- `advanced_topics.md` - 高级主题

## 许可证

MIT License

## 支持

- GitHub Issues
- Email: Martin (紫微智控)

---

**让 AI 智能体自主付费，开启机器经济时代！**