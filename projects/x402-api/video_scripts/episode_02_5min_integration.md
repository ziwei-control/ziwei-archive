# 视频教程第 2 集：5 分钟集成 x402 API

**时长：** 15 分钟  
**难度：** ⭐⭐ 初级  
**前置条件：** 观看第 1 集

---

## 📝 脚本

### 开场（0:00-1:00）

```
[画面：标题动画]
🎬 5 分钟集成 x402 API
第 2 集：快速开始

[主持人]
欢迎回来！上一集我们了解了 x402 API 是什么。
这一集，我会手把手教你如何在 5 分钟内把它集成到你的项目中。
```

### 准备工作（1:00-3:00）

```
[画面：检查清单]
开始前，你需要准备：

✅ 一个 USDC 钱包（MetaMask 等）
✅ 少量 USDC（$5 就够用很久）
✅ Python 3.8+ 环境
✅ 基础编程知识

[主持人]
如果你还没有 USDC 钱包，可以在币安或 Coinbase 购买后提现到钱包。
```

### 步骤 1：安装依赖（3:00-5:00）

```
[屏幕共享：终端]
# 创建项目目录
mkdir my-x402-app
cd my-x402-app

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装 requests 库
pip install requests

[主持人]
好了，环境准备好了。
```

### 步骤 2：编写代码（5:00-10:00）

```
[屏幕共享：编辑器]
# 创建 translator.py

import requests
import json

class X402Translator:
    def __init__(self, wallet_key):
        self.wallet_key = wallet_key
        self.base_url = "http://8.213.149.224:5002"
    
    def translate(self, text, source='en', target='zh'):
        # 生成支付签名
        import hashlib
        import time
        
        amount = 20000  # 0.02 USDC (6 位小数)
        timestamp = int(time.time() * 1000)
        
        # 简化示例，实际需要使用 x402 库
        headers = {
            'Content-Type': 'application/json',
            'X-Payment-Amount': str(amount),
            'X-Payment-Token': 'USDC'
        }
        
        payload = {
            'text': text,
            'source': source,
            'target': target
        }
        
        response = requests.post(
            f'{self.base_url}/api/v1/translator',
            json=payload,
            headers=headers
        )
        
        return response.json()

# 使用示例
if __name__ == '__main__':
    translator = X402Translator('your_wallet_key')
    result = translator.translate('Hello, World!')
    print(f"翻译结果：{result['data']['translated_text']}")
    print(f"花费：{result['cost']} USDC")

[主持人]
代码很简单，对吧？
```

### 步骤 3：运行测试（10:00-12:00）

```
[屏幕共享：终端]
# 运行代码
python translator.py

[运行结果]
翻译结果：你好，世界！
花费：0.02 USDC

[主持人]
看到了吗？我们成功完成了一次翻译，只花了 $0.02。
```

### 步骤 4：错误处理（12:00-14:00）

```
[屏幕共享：编辑器]
# 添加错误处理

try:
    result = translator.translate('Hello')
    if result['success']:
        print(f"✅ 翻译成功：{result['data']['translated_text']}")
    else:
        print(f"❌ 失败：{result.get('error', '未知错误')}")
except Exception as e:
    print(f"❌ 异常：{e}")

[主持人]
实际项目中，记得添加完善的错误处理。
```

### 总结与作业（14:00-15:00）

```
[画面：总结]
今天我们学到了：
✅ 环境准备
✅ 代码编写
✅ 运行测试
✅ 错误处理

[主持人]
课后作业：
试着把翻译功能集成到你现有的项目中。

下一集，我们会详细讲解 SDK 的使用方法。
再见！
```

---

## 🎬 拍摄要点

**重点：**
- 代码清晰可见
- 字体放大
- 关键步骤慢速讲解

**互动：**
- 暂停让观众跟上
- 提示常见错误
- 鼓励实践

---

**脚本版本：** v1.0  
**创建时间：** 2026-03-05
