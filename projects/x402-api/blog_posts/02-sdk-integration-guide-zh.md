# x402 API SDK 集成指南

> 3 种语言，5 行代码，10 分钟集成 AI 支付能力

**发布时间：** 2026-03-05  
**作者：** 紫微智控团队  
**难度：** ⭐⭐ 初级  
**阅读时间：** 10 分钟

---

## 🎯 为什么需要 SDK

直接调用 API 需要处理：
- ❌ 支付签名生成
- ❌ 错误重试逻辑
- ❌ 余额检查
- ❌ 汇率转换

使用 SDK，只需：
```python
from x402 import Client

client = Client(wallet_key)
result = client.translate("Hello", "en", "zh")
print(f"花费：{result.cost} USDC")
```

---

## 📦 Python SDK

### 安装

```bash
pip install x402-sdk
```

### 快速开始

```python
from x402 import Client, Wallet

# 1. 创建钱包（或导入现有）
wallet = Wallet.create()  # 新钱包
# wallet = Wallet.import_key("your_private_key")  # 导入现有

# 2. 初始化客户端
client = Client(
    wallet=wallet,
    base_url="http://8.213.149.224:5002"
)

# 3. 检查余额
balance = client.get_balance()
print(f"余额：{balance} USDC")

# 4. 调用 API
result = client.translator.translate(
    text="Hello, world!",
    source="en",
    target="zh"
)

print(f"翻译：{result.data.translated_text}")
print(f"花费：{result.cost} USDC")
```

### 完整示例：批量翻译

```python
from x402 import Client, Wallet

wallet = Wallet.import_key("your_private_key")
client = Client(wallet=wallet)

texts = ["Hello", "Good morning", "Thank you", "Goodbye"]

for text in texts:
    result = client.translator.translate(
        text=text,
        source="en",
        target="zh"
    )
    print(f"{text} → {result.data.translated_text} (${result.cost})")

# 统计总花费
total = sum(r.cost for r in results)
print(f"总花费：{total} USDC")
```

### 错误处理

```python
from x402 import Client, InsufficientBalanceError, RateLimitError

client = Client(wallet=wallet)

try:
    result = client.translator.translate("Hello", "en", "zh")
except InsufficientBalanceError as e:
    print(f"余额不足：{e}")
    # 自动充值逻辑
except RateLimitError as e:
    print(f"频率限制：{e}")
    # 等待后重试
except Exception as e:
    print(f"其他错误：{e}")
```

---

## 🟨 JavaScript/Node.js SDK

### 安装

```bash
npm install @x402/sdk
# 或
yarn add @x402/sdk
```

### 快速开始

```javascript
const { Client, Wallet } = require('@x402/sdk');

// 1. 创建钱包
const wallet = Wallet.create();
// const wallet = Wallet.importKey('your_private_key');

// 2. 初始化客户端
const client = new Client({
  wallet: wallet,
  baseUrl: 'http://8.213.149.224:5002'
});

// 3. 检查余额
const balance = await client.getBalance();
console.log(`余额：${balance} USDC`);

// 4. 调用 API
const result = await client.translator.translate({
  text: 'Hello, world!',
  source: 'en',
  target: 'zh'
});

console.log(`翻译：${result.data.translated_text}`);
console.log(`花费：${result.cost} USDC`);
```

### React 集成示例

```jsx
import { useState } from 'react';
import { Client, Wallet } from '@x402/sdk';

function Translator() {
  const [input, setInput] = useState('');
  const [output, setOutput] = useState('');
  const [cost, setCost] = useState(0);

  const client = new Client({
    wallet: Wallet.importKey(process.env.WALLET_KEY)
  });

  const handleTranslate = async () => {
    try {
      const result = await client.translator.translate({
        text: input,
        source: 'en',
        target: 'zh'
      });
      
      setOutput(result.data.translated_text);
      setCost(result.cost);
    } catch (error) {
      console.error('翻译失败:', error);
    }
  };

  return (
    <div>
      <textarea value={input} onChange={e => setInput(e.target.value)} />
      <button onClick={handleTranslate}>翻译 (${cost})</button>
      <div>{output}</div>
    </div>
  );
}
```

---

## 🐹 Go SDK

### 安装

```bash
go get github.com/x402/sdk-go
```

### 快速开始

```go
package main

import (
    "fmt"
    "log"
    "github.com/x402/sdk-go"
)

func main() {
    // 1. 创建钱包
    wallet, err := x402.CreateWallet()
    if err != nil {
        log.Fatal(err)
    }
    // 或导入现有钱包
    // wallet, err := x402.ImportWallet("your_private_key")

    // 2. 初始化客户端
    client := x402.NewClient(x402.Config{
        Wallet:  wallet,
        BaseURL: "http://8.213.149.224:5002",
    })

    // 3. 检查余额
    balance, err := client.GetBalance()
    if err != nil {
        log.Fatal(err)
    }
    fmt.Printf("余额：%v USDC\n", balance)

    // 4. 调用 API
    result, err := client.Translator.Translate(x402.TranslateRequest{
        Text:   "Hello, world!",
        Source: "en",
        Target: "zh",
    })
    if err != nil {
        log.Fatal(err)
    }

    fmt.Printf("翻译：%s\n", result.Data.TranslatedText)
    fmt.Printf("花费：%v USDC\n", result.Cost)
}
```

### 并发调用示例

```go
package main

import (
    "fmt"
    "sync"
    "github.com/x402/sdk-go"
)

func main() {
    client := x402.NewClient(config)
    
    texts := []string{"Hello", "Good morning", "Thank you"}
    var wg sync.WaitGroup
    
    for _, text := range texts {
        wg.Add(1)
        go func(t string) {
            defer wg.Done()
            
            result, err := client.Translator.Translate(x402.TranslateRequest{
                Text:   t,
                Source: "en",
                Target: "zh",
            })
            if err != nil {
                fmt.Printf("错误：%v\n", err)
                return
            }
            
            fmt.Printf("%s → %s ($%v)\n", t, result.Data.TranslatedText, result.Cost)
        }(text)
    }
    
    wg.Wait()
}
```

---

## 🔧 SDK 高级功能

### 1. 自动重试

```python
from x402 import Client, RetryConfig

client = Client(
    wallet=wallet,
    retry=RetryConfig(
        max_attempts=3,
        backoff_factor=2,  # 指数退避
        retry_on=[500, 502, 503, 504]  # 重试这些状态码
    )
)
```

### 2. 请求缓存

```python
from x402 import Client, CacheConfig

client = Client(
    wallet=wallet,
    cache=CacheConfig(
        enabled=True,
        ttl=3600,  # 缓存 1 小时
        max_size=1000  # 最多 1000 条
    )
)

# 相同请求会直接返回缓存结果
result1 = client.translator.translate("Hello", "en", "zh")
result2 = client.translator.translate("Hello", "en", "zh")  # 缓存命中
```

### 3. 批量调用

```python
from x402 import Client

client = Client(wallet=wallet)

# 批量翻译，享受折扣
batch = [
    {"text": "Hello", "source": "en", "target": "zh"},
    {"text": "World", "source": "en", "target": "zh"},
    {"text": "Test", "source": "en", "target": "zh"},
]

results = client.translator.translate_batch(batch)
print(f"总花费：{results.total_cost} USDC (省了 {results.discount}%)")
```

### 4. 使用量监控

```python
from x402 import Client, UsageTracker

client = Client(
    wallet=wallet,
    tracker=UsageTracker(
        daily_limit=10.0,  # 每日限额 10 USDC
        alert_threshold=0.8,  # 80% 时告警
        callback=lambda: print("快要用超了！")
    )
)
```

---

## 📊 SDK 对比

| 功能 | Python | JavaScript | Go |
|------|--------|------------|-----|
| 安装 | `pip install` | `npm install` | `go get` |
| 异步支持 | ✅ asyncio | ✅ Promise | ✅ goroutine |
| 类型提示 | ✅ Type hints | ✅ TypeScript | ✅ Structs |
| 缓存 | ✅ | ✅ | ✅ |
| 重试 | ✅ | ✅ | ✅ |
| 批量 | ✅ | ✅ | ✅ |
| 监控 | ✅ | ✅ | ✅ |

---

## 🐛 常见问题

### Q: SDK 报错 "Invalid signature"

**A:** 检查私钥格式是否正确，确保没有多余空格。

```python
# ❌ 错误
wallet = Wallet.import_key(" 0x123... ")

# ✅ 正确
wallet = Wallet.import_key("0x123...")
```

### Q: 如何检查剩余余额？

```python
balance = client.get_balance()
print(f"剩余：{balance} USDC")

# 设置低余额告警
if balance < 1.0:
    print("⚠️ 余额不足 1 USDC，请充值")
```

### Q: 可以在浏览器中使用吗？

**A:** JavaScript SDK 支持浏览器环境，但需要注意：

```javascript
// ⚠️ 不要在前端代码中暴露私钥！
// ✅ 正确做法：通过后端代理

// 后端（Node.js）
app.post('/translate', async (req, res) => {
  const result = await client.translator.translate(req.body);
  res.json(result);
});

// 前端
fetch('/translate', {
  method: 'POST',
  body: JSON.stringify({ text: 'Hello' })
});
```

---

## 📚 下一步

- [ ] 查看 [API 参考文档](#)
- [ ] 阅读 [最佳实践](#)
- [ ] 加入 [Discord 社区](#)
- [ ] 查看 [示例项目](#)

---

**开始构建吧！🚀**

*SDK 源码：github.com/x402/sdk-python | sdk-js | sdk-go*
