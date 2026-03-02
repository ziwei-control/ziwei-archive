# 🚀 快速开始指南 - x402 Python SDK

## 安装

```bash
pip install x402-sdk
```

或从源码安装：

```bash
git clone https://github.com/ziwei/x402-python-sdk.git
cd x402-python-sdk
pip install -r requirements.txt
```

---

## 第一个调用

```python
from x402 import X402Client

# 创建客户端（本地测试）
client = X402Client(
    api_base_url="http://localhost:5002",
    wallet_address="0x..."
)

# 调用 API（自动处理支付）
result = client.request_with_payment(
    endpoint="/api/v1/translate",
    json_data={
        "text": "Hello, world!",
        "source_lang": "English",
        "target_lang": "Chinese"
    }
)

print(result['result'])
```

---

## 工作流程

1. **发送请求** → 服务器返回 402 支付请求
2. **支付 USDC** → 使用钱包完成支付
3. **重发请求 + 支付证明** → 服务器验证
4. **获取结果** → API 返回 AI 生成的响应

---

## API 端点

| 端点 | 功能 | 价格 |
|------|------|------|
| POST /api/v1/architect | 架构设计 | $0.10 |
| POST /api/v1/code-audit | 代码审计 | $0.05 |
| POST /api/v1/translate | 翻译 | $0.02 |

完整端点列表: [API Reference](docs/API_REFERENCE.md)

---

## 常见问题

### Q: 如何获取 API Key？

A: API Key 需要从 x402 API 提供商获取。联系 Martin 获取 API Key。

### Q: 如何测试？

A: 查看 [examples/basic_usage.py](examples/basic_usage.py) 和 [examples/advanced_usage.py](examples/examples/advanced_usage.py)

### Q: 支持哪些交易所？

A: SDK 不直接连接交易所，它只处理 x402 支付协议。交易所集成需要其他工具。

---

## 下一步

- 阅读 [完整文档](docs/API_REFERENCE.md)
- 查看 [高级示例](examples/advanced_usage.py)
- 查看 [故障排查](docs/troubleshooting.md)

---

**开始使用 x402 SDK！**