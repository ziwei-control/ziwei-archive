# x402 Python SDK - 完整文档索引

## 📚 文档导航

| 文档 | 说明 |
|------|------|
| [README.md](README.md) | 项目介绍和快速开始 |
| [CHANGELOG.md](CHANGELOG.md) | 版本更新日志 |
| [LICENSE](LICENSE) | 许可证信息 |
| [examples/basic_usage.py](examples/basic_usage.py) | 基础使用示例 |
| [examples/advanced_usage.py](examples/advanced_usage.py) | 高级用法示例 |
| [tests/test_sdk.py](tests/test_sdk.py) | SDK 测试脚本 |

---

## 🔧 API 端点完整列表

| 端点 | 功能 | 价格 | 请求限制 |
|------|------|------|---------|
| POST /api/v1/architect | 架构设计 | $0.10 | 100/分钟 |
| POST /api/v1/code-gen | 代码生成 | $0.08 | 200/分钟 |
| POST /api/v1/code-audit | 代码审计 | $0.05 | 300/分钟 |
| POST /api/v1/logic | 逻辑推理 | $0.06 | 200/分钟 |
| POST /api/v1/translate | 翻译 | $0.02 | 500/分钟 |
| POST /api/v1/long-text | 长文解析 | $0.03 | 400/分钟 |
| POST /api/v1/crawl | 网络爬虫 | $0.04 | 300/分钟 |
| POST /api/v1/vision | 视觉解析 | $0.15 | 10/分钟 |

---

## 📦 项目文件结构

```
x402-python-sdk/
├── x402/
│   ├── __init__.py              # SDK 入口
│   ├── client.py                # 客户端类
│   ├── payment.py             # 支付处理
│   └── exceptions.py           # 异常定义
├── examples/
│   ├── basic_usage.py           # 基础使用示例
│   └── advanced_usage.py        # 高级用法示例
├── tests/
│   └── test_sdk.py              # 测试脚本
├── docs/
│   ├── api_reference.md         # API 完整参考
│   ├── quick_start.md           # 快速开始
│   ├── troubleshooting.md      # 故障排查
│   └── deployment.md          # 部署指南
├── README.md                   # 项目介绍
├── LICENSE                     # Apache 2.0 许可证
├── CHANGELOG.md                  # 版本更新日志
└── setup.py                     # 安装脚本
```

---

## 🛠️ 开发指南

### 贡献指南

1. Fork 仓库
2. 创建特性分支 (`git checkout -b feature/xxx`)
3. 提交改动
4. 创建 Pull Request

### 代码规范

- 遵循 PEP 8
- 添加类型注解
- 编写单元测试
- 更新文档

---

## 📞 联系支持

- **GitHub**: https://github.com/ziwei/x402-python-sdk/issues
- **Email**: pandac00@163.com

---

**让 AI 智能体自主付费，开启机器经济时代！**