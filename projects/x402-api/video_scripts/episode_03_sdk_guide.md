# 视频教程第 3 集：SDK 使用详解

**时长：** 20 分钟  
**难度：** ⭐⭐⭐ 中级  
**前置条件：** 观看第 1-2 集

---

## 📝 脚本

### 开场（0:00-1:00）

```
[画面：标题动画]
🎬 SDK 使用详解
第 3 集：Python/JavaScript/Go

[主持人]
欢迎回来！这一集我们深入讲解 x402 SDK 的使用。
我会展示 Python、JavaScript 和 Go 三种语言的完整示例。
```

### Python SDK（1:00-7:00）

```
[屏幕共享：代码演示]
# 安装
pip install x402-sdk

# 基础使用
from x402 import Client, Wallet

wallet = Wallet.import_key('your_private_key')
client = Client(wallet=wallet)

# 翻译
result = client.translator.translate(
    text="Hello",
    source="en",
    target="zh"
)
print(f"翻译：{result.data.translated_text}")
print(f"花费：{result.cost} USDC")

# 批量调用
texts = [{"text": f"Message {i}"} for i in range(10)]
results = client.translator.translate_batch(texts, discount=0.8)
print(f"总花费：{results.total_cost} USDC")

# 错误处理
try:
    result = client.translate("Hello", "en", "zh")
except InsufficientBalanceError:
    print("余额不足，请充值")
except RateLimitError:
    print("频率限制，请稍后重试")

# 使用量监控
stats = client.get_usage_stats()
print(f"已用：{stats['total_spent']} USDC")
print(f"余额：{stats['current_balance']} USDC")
```

### JavaScript SDK（7:00-13:00）

```
[屏幕共享：代码演示]
// 安装
npm install @x402/sdk

// 基础使用
const { Client, Wallet } = require('@x402/sdk');

const wallet = Wallet.importKey('your_private_key');
const client = new Client({ wallet });

// 翻译
const result = await client.translator.translate({
  text: 'Hello',
  source: 'en',
  target: 'zh'
});

console.log(`翻译：${result.data.translated_text}`);
console.log(`花费：${result.cost} USDC`);

// React 集成
function Translator() {
  const [input, setInput] = useState('');
  const [output, setOutput] = useState('');
  
  const handleTranslate = async () => {
    const result = await client.translate(input, 'en', 'zh');
    setOutput(result.data.translated_text);
  };
  
  return (
    <div>
      <input value={input} onChange={e => setInput(e.target.value)} />
      <button onClick={handleTranslate}>翻译</button>
      <div>{output}</div>
    </div>
  );
}
```

### Go SDK（13:00-18:00）

```
[屏幕共享：代码演示]
// 安装
go get github.com/x402/sdk-go

// 基础使用
package main

import (
    "fmt"
    "github.com/x402/sdk-go"
)

func main() {
    wallet, _ := x402.ImportWallet("your_private_key")
    client := x402.NewClient(x402.Config{
        Wallet: wallet,
        BaseURL: "http://8.213.149.224:5002",
    })
    
    result, _ := client.Translator.Translate(x402.TranslateRequest{
        Text: "Hello",
        Source: "en",
        Target: "zh",
    })
    
    fmt.Printf("翻译：%s\n", result.Data.TranslatedText)
    fmt.Printf("花费：%v USDC\n", result.Cost)
}

// 并发调用
var wg sync.WaitGroup
for i := 0; i < 5; i++ {
    wg.Add(1)
    go func(n int) {
        defer wg.Done()
        result, _ := client.Translate(fmt.Sprintf("Text %d", n), "en", "zh")
        fmt.Printf("结果 %d: %s\n", n, result.Data.TranslatedText)
    }(i)
}
wg.Wait()
```

### 总结（18:00-20:00）

```
[画面：对比表格]
| 特性 | Python | JavaScript | Go |
|------|--------|------------|-----|
| 安装 | pip | npm | go get |
| 异步支持 | ✅ | ✅ | ✅ |
| 类型提示 | ✅ | ✅ | ✅ |
| 缓存 | ✅ | ✅ | ✅ |
| 重试 | ✅ | ✅ | ✅ |

[主持人]
三种语言都支持完整功能。
选择你熟悉的语言开始吧！

下一集，我们会用 x402 API 构建一个完整的多语言客服系统。
```

---

## 🎬 拍摄要点

**代码展示：**
- 分屏显示：代码 + 运行结果
- 语法高亮
- 关键部分放大

**节奏控制：**
- 每段代码后暂停
- 解释关键概念
- 提示常见错误

---

**脚本版本：** v1.0  
**创建时间：** 2026-03-05
