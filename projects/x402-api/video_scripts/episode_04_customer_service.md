# 视频教程第 4 集：实战 - 多语言客服系统

**时长：** 25 分钟  
**难度：** ⭐⭐⭐⭐ 中高级  
**项目类型：** 完整实战

---

## 📝 脚本

### 开场（0:00-2:00）

```
[画面：项目演示]
🎬 实战项目：多语言客服系统

[主持人]
欢迎回来！这一集我们会用 x402 API 构建一个完整的多语言客服系统。

[演示成品]
这是一个客服系统，可以自动翻译不同语言的客户消息。
客户用英文提问，客服看到中文，回复中文，客户看到英文。

整个系统使用 x402 API，每次翻译成本仅 $0.02。
```

### 项目架构（2:00-5:00）

```
[画面：架构图]
系统架构：

客户 → Telegram/Website → 翻译服务 → 客服
                                ↓
客户 ← Telegram/Website ← 翻译服务 ← 客服

技术栈：
- 前端：React + Tailwind CSS
- 后端：Node.js + Express
- 数据库：SQLite
- 翻译：x402 API
- 部署：Docker
```

### 后端实现（5:00-15:00）

```
[屏幕共享：代码演示]
// server.js
const express = require('express');
const { Client, Wallet } = require('@x402/sdk');

const app = express();
const client = new Client({ wallet });

// 接收客户消息
app.post('/api/message', async (req, res) => {
  const { text, fromLang, toLang } = req.body;
  
  try {
    // 调用 x402 翻译 API
    const result = await client.translate(text, fromLang, toLang);
    
    // 保存到数据库
    await db.messages.create({
      original: text,
      translated: result.data.translated_text,
      cost: result.cost,
      timestamp: new Date()
    });
    
    res.json({ success: true, translated: result.data.translated_text });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// 统计面板
app.get('/api/stats', async (req, res) => {
  const stats = await db.messages.aggregate([
    { $sum: '$cost' },  // 总成本
    { $count: 'total' } // 总消息数
  ]);
  res.json(stats);
});

app.listen(3000, () => {
  console.log('客服系统运行在 http://localhost:3000');
});
```

### 前端实现（15:00-20:00）

```
[屏幕共享：代码演示]
// ChatWindow.jsx
function ChatWindow() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  
  const sendMessage = async () => {
    const response = await fetch('/api/message', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text: input,
        fromLang: 'en',
        toLang: 'zh'
      })
    });
    
    const data = await response.json();
    setMessages([...messages, { text: input, translated: data.translated }]);
    setInput('');
  };
  
  return (
    <div className="chat-window">
      {messages.map((msg, i) => (
        <div key={i} className="message">
          <div className="original">{msg.text}</div>
          <div className="translation">{msg.translated}</div>
        </div>
      ))}
      <input value={input} onChange={e => setInput(e.target.value)} />
      <button onClick={sendMessage}>发送</button>
    </div>
  );
}
```

### 成本分析（20:00-23:00）

```
[画面：成本对比]
传统客服系统 vs x402 客服系统

传统方案：
- 雇佣翻译：$50/小时
- 每月成本：$8,000+
- 响应时间：分钟级

x402 方案：
- API 调用：$0.02/次
- 每月成本：$60（1000 次对话）
- 响应时间：秒级

节省：99% 成本！
```

### 部署上线（23:00-25:00）

```
[屏幕共享：Docker]
# Dockerfile
FROM node:18
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 3000
CMD ["node", "server.js"]

# 部署
docker build -t customer-service .
docker run -p 3000:3000 customer-service

[主持人]
好了！系统已经上线。
你可以在任何地方访问它。
```

---

## 🎬 拍摄要点

**实战重点：**
- 完整代码展示
- 实时运行演示
- 成本对比分析

**互动环节：**
- 观众提问
- 现场调试
- 展示真实对话

---

**脚本版本：** v1.0  
**创建时间：** 2026-03-05
