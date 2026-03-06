# 🚀 x402 API 官方链接汇总

**最后更新：** 2026-03-06  
**版本：** v2.2.0

---

## 🌐 服务架构说明

### 端口分配

| 端口 | 服务 | 用途 | 状态 |
|------|------|------|------|
| **8090** | API 密钥发放服务 | 用户获取 API 密钥 + 验证交易 API | ✅ 运行中 |
| **8091** | Dashboard 监控面板 | 实时查看发放统计和记录 | ✅ 运行中 |
| **5002** | API 服务器 | 实际 AI API 调用端点 | - |

**说明：**
- **8090 端口** 是 API 密钥发放系统的核心服务，提供前端页面和后端 API
- **8091 端口** 是独立的监控面板，用于查看统计数据
- **5002 端口** 是实际的 AI API 服务（私有部署）

---

## 🔗 官方访问地址

### 用户入口（8090 端口）

**API 密钥获取页面：**
```
http://8.213.149.224:8090/get-api-key.html
```
**用途：** 用户支付 USDC 后自动获取 API 访问凭证

**API 端点（8090 端口）：**
```
POST http://8.213.149.224:8090/api/verify     # 验证交易
GET  http://8.213.149.224:8090/api/status     # 状态检查
GET  http://8.213.149.224:8090/api/transactions # 交易记录
GET  http://8.213.149.224:8090/api/stats      # 统计数据
```

### 监控面板（8091 端口）

**Dashboard 监控面板：**
```
http://8.213.149.224:8091
```
**用途：** 实时查看系统状态、收入统计、交易记录

### API 服务器（5002 端口）

**API 调用端点：**
```
http://8.213.149.224:5002
```
**用途：** 实际 AI API 调用（合作后开放）

---

## 📚 官方文档

### GitHub 仓库
```
https://github.com/ziwei-control/ziwei-archive
```

### Gitee 镜像（国内访问更快）
```
https://gitee.com/pandac0/ziwei-archive
```

### 文档索引
- [README.md](https://github.com/ziwei-control/ziwei-archive/blob/main/projects/x402-api/README.md) - 项目总览
- [QUICK_START.md](https://github.com/ziwei-control/ziwei-archive/blob/main/projects/x402-api/QUICK_START.md) - 快速开始
- [CUSTOMER_API_GUIDE.md](https://github.com/ziwei-control/ziwei-archive/blob/main/projects/x402-api/CUSTOMER_API_GUIDE.md) - 客户调用指南
- [API_KEY_SYSTEM_README.md](https://github.com/ziwei-control/ziwei-archive/blob/main/projects/x402-api/API_KEY_SYSTEM_README.md) - API 密钥系统说明
- [VERIFICATION_LOGIC.md](https://github.com/ziwei-control/ziwei-archive/blob/main/projects/x402-api/VERIFICATION_LOGIC.md) - 验证逻辑详解

---

## 💰 支付信息

### USDC 收款地址
```
0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb
```

**网络：** Base Chain (ERC-20 USDC)  
**金额：** 0.05 USDC（容差范围：0.03 - 0.07 USDC）  
**确认时间：** 约 15-30 秒  
**验证时限：** 60 分钟内  

**查询交易：** https://basescan.org/address/0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb

---

## 📋 API 价格列表

| API | 价格 | 端点 |
|-----|------|------|
| 翻译服务 | $0.02/次 | `/api/v1/translator` |
| 长文解析 | $0.03/次 | `/api/v1/long-text` |
| 网络爬虫 | $0.04/次 | `/api/v1/crawl` |
| 代码审计 | $0.05/次 | `/api/v1/code-audit` |
| 逻辑推理 | $0.06/次 | `/api/v1/logic` |
| 代码生成 | $0.08/次 | `/api/v1/code-gen` |
| 架构设计 | $0.10/次 | `/api/v1/architect` |
| 视觉解析 | $0.15/次 | `/api/v1/vision` |

---

## 🔗 推广链接（可直接使用）

### 简短推广文案

**Twitter/微博：**
```
🚀 x402 API 正式上线！

让 AI 微付费成为可能：
✅ 按次付费 $0.02 起
✅ 无需订阅
✅ 无需信用卡
✅ 有 USDC 就能用

立即获取 API 密钥：
http://8.213.149.224:8090/get-api-key.html

#AI #Web3 #USDC #API
```

**Telegram/微信群：
```
🚀 x402 API - AI 微付费协议

8 个 AI 能力 API 化，按次付费 $0.02 起

✅ 无需订阅
✅ 无需信用卡  
✅ 有 USDC 就能用

立即获取 API 密钥：
http://8.213.149.224:8090/get-api-key.html

GitHub: github.com/ziwei-control/ziwei-archive
```

**开发者论坛：
```
x402 API - 按次付费的 AI API 服务

价格：$0.02/次起
支付：USDC (Base 链)
文档：github.com/ziwei-control/ziwei-archive
获取密钥：http://8.213.149.224:8090/get-api-key.html
```

---

## 📊 实时数据

### 查看当前收入
```bash
curl http://8.213.149.224:8090/api/stats
```

### 查看 API 状态
```bash
curl http://8.213.149.224:8090/api/status
```

### 查看交易记录
```bash
curl http://8.213.149.224:8090/api/transactions
```

### Dashboard 监控
```bash
curl http://8.213.149.224:8091/api/stats
```

---

## 🛠️ 快速集成示例

### Python
```python
import requests

# 获取 API 密钥后
response = requests.post(
    "http://8.213.149.224:5002/api/v1/translator",
    json={"text": "Hello!", "source": "en", "target": "zh"},
    headers={
        "X-API-Key": "你的 API_KEY",
        "X-Payment-Amount": "20000",
        "X-Payment-Token": "USDC"
    }
)
print(response.json())
```

### JavaScript
```javascript
const response = await fetch("http://8.213.149.224:5002/api/v1/translator", {
    method: "POST",
    headers: {
        "Content-Type": "application/json",
        "X-API-Key": "你的 API_KEY",
        "X-Payment-Amount": "20000",
        "X-Payment-Token": "USDC"
    },
    body: JSON.stringify({
        text: "Hello!",
        source: "en",
        target: "zh"
    })
});
const data = await response.json();
console.log(data);
```

### cURL
```bash
curl -X POST http://8.213.149.224:5002/api/v1/translator \
  -H "Content-Type: application/json" \
  -H "X-API-Key: 你的 API_KEY" \
  -H "X-Payment-Amount: 20000" \
  -H "X-Payment-Token: USDC" \
  -d '{"text":"Hello!","source":"en","target":"zh"}'
```

---

## 📞 联系方式

**技术支持：**
- GitHub Issues: https://github.com/ziwei-control/ziwei-archive/issues
- 工单系统：https://github.com/ziwei-control/ziwei-archive/issues

**商务合作：**
- DM 或邮件联系
- 投资者：提供 BP 和数据室访问

---

## ⚠️ 服务地区

**✅ 服务：** 美国、欧盟、英国、加拿大、澳大利亚、新加坡、日本、韩国、阿联酋  
**❌ 不服务：** 中国大陆、朝鲜、伊朗、叙利亚、其他受限地区

---

## 📈 路线图

**2026 Q2：**
- [x] API 密钥自动发放系统
- [ ] SDK 发布（Python/JS/Go）
- [ ] 视频教程（5 集）

**2026 Q3：**
- [ ] 订阅制套餐
- [ ] 企业 SLA 保障
- [ ] 多区域部署

**2026 Q4：**
- [ ] 1000+ 活跃开发者
- [ ] $1000+ USDC/月收入
- [ ] A 轮融资

---

## 📄 许可证

MIT License - 详见 [LICENSE](https://github.com/ziwei-control/ziwei-archive/blob/main/projects/x402-api/LICENSE)

---

**开始构建你的 AI 应用吧！** 🚀

**立即获取 API 密钥：** http://8.213.149.224:8090/get-api-key.html  
**查看监控面板：** http://8.213.149.224:8091
