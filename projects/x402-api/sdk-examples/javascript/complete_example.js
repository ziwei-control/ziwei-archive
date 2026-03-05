/**
 * x402 API - JavaScript SDK 完整示例
 * 
 * 包含:
 * - 基础调用 (Node.js)
 * - 浏览器使用
 * - React 集成
 * - 错误处理
 * - 批量调用
 * - 使用量监控
 */

// ==================== Node.js 基础示例 ====================

const crypto = require('crypto');

class x402Client {
  constructor(walletKey, baseUrl = 'http://localhost:5002') {
    this.walletKey = walletKey;
    this.baseUrl = baseUrl;
    this.balance = 10.0; // 模拟余额
    this.totalSpent = 0.0;
  }

  // 生成支付签名
  generateSignature(amount, endpoint, timestamp) {
    const data = `${amount}:${endpoint}:${timestamp}`;
    return crypto
      .createHmac('sha256', this.walletKey)
      .update(data)
      .digest('hex');
  }

  // 通用 API 调用方法
  async callAPI(endpoint, payload, cost) {
    const timestamp = Date.now();
    const signature = this.generateSignature(cost, endpoint, timestamp);

    if (this.balance < cost) {
      throw new Error(`余额不足：需要 ${cost} USDC，当前 ${this.balance.toFixed(2)} USDC`);
    }

    const response = await fetch(`${this.baseUrl}/api/v1/${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Payment-Amount': (cost * 1000000).toString(), // 6 位小数
        'X-Payment-Token': 'USDC',
        'X-Payment-Signature': signature,
        'X-Payment-Timestamp': timestamp.toString()
      },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      throw new Error(`API 错误：${response.status} ${response.statusText}`);
    }

    const result = await response.json();
    
    this.balance -= cost;
    this.totalSpent += cost;

    return {
      success: true,
      data: result.data,
      cost: cost
    };
  }

  // 翻译 API
  async translate(text, source = 'en', target = 'zh') {
    return await this.callAPI('translator', { text, source, target }, 0.02);
  }

  // 代码生成 API
  async codeGen(prompt, language = 'javascript') {
    return await this.callAPI('code-gen', { prompt, language }, 0.08);
  }

  // 批量翻译（享受折扣）
  async batchTranslate(texts, discount = 0.8) {
    const results = [];
    const costPerCall = 0.02 * discount;

    for (const task of texts) {
      try {
        const result = await this.translate(
          task.text,
          task.source || 'en',
          task.target || 'zh'
        );
        result.cost = costPerCall;
        results.push(result);
      } catch (error) {
        results.push({
          success: false,
          error: error.message,
          cost: 0
        });
      }
    }

    return results;
  }

  // 获取使用统计
  getUsageStats() {
    return {
      initialBalance: 10.0,
      currentBalance: this.balance,
      totalSpent: this.totalSpent,
      usageRate: `${((this.totalSpent / 10.0) * 100).toFixed(1)}%`
    };
  }
}

// ==================== 使用示例 ====================

async function exampleBasicUsage() {
  console.log('='.repeat(50));
  console.log('示例 1: 基础调用');
  console.log('='.repeat(50));

  const client = new x402Client('your_wallet_key');

  const result = await client.translate('Hello, world!', 'en', 'zh');
  
  console.log(`✅ 翻译成功：${result.data.translated_text}`);
  console.log(`💰 花费：${result.cost} USDC\n`);
}

async function exampleErrorHandling() {
  console.log('='.repeat(50));
  console.log('示例 2: 错误处理');
  console.log('='.repeat(50));

  const client = new x402Client('your_wallet_key');
  client.balance = 0.01; // 余额不足

  try {
    await client.translate('Hello', 'en', 'zh');
  } catch (error) {
    console.log(`⚠️ 错误：${error.message}`);
    console.log('💡 建议：检查余额或充值\n');
  }
}

async function exampleBatchProcessing() {
  console.log('='.repeat(50));
  console.log('示例 3: 批量调用（享受折扣）');
  console.log('='.repeat(50));

  const client = new x402Client('your_wallet_key');

  const texts = Array.from({ length: 15 }, (_, i) => ({
    text: `Message ${i}`,
    source: 'en',
    target: 'zh'
  }));

  const results = await client.batchTranslate(texts, 0.8); // 8 折

  const totalCost = results.reduce((sum, r) => sum + r.cost, 0);
  const successful = results.filter(r => r.success).length;

  console.log(`📊 批量翻译 ${successful}/${texts.length} 条`);
  console.log(`💰 总花费：${totalCost.toFixed(4)} USDC`);
  console.log(`🎯 平均每次：${(totalCost / successful).toFixed(4)} USDC`);
  console.log(`💡 节省了：${(0.02 * 15 - totalCost).toFixed(4)} USDC\n`);
}

async function exampleConcurrentCalls() {
  console.log('='.repeat(50));
  console.log('示例 4: 并发调用');
  console.log('='.repeat(50));

  const client = new x402Client('your_wallet_key');

  const tasks = Array.from({ length: 5 }, (_, i) =>
    client.translate(`Text ${i}`, 'en', 'zh')
  );

  const results = await Promise.all(tasks);

  const successful = results.filter(r => r.success).length;
  const totalCost = results.reduce((sum, r) => sum + r.cost, 0);

  console.log(`✅ 成功：${successful}/${results.length}`);
  console.log(`💰 总花费：${totalCost.toFixed(4)} USDC`);
  console.log(`⚡ 并发执行，节省时间\n`);
}

async function exampleUsageMonitoring() {
  console.log('='.repeat(50));
  console.log('示例 5: 使用量监控');
  console.log('='.repeat(50));

  const client = new x402Client('your_wallet_key');

  // 模拟使用
  for (let i = 0; i < 10; i++) {
    await client.translate(`Test ${i}`, 'en', 'zh');
  }

  const stats = client.getUsageStats();

  console.log('📊 使用统计:');
  console.log(`  初始余额：$${stats.initialBalance} USDC`);
  console.log(`  当前余额：$${stats.currentBalance.toFixed(2)} USDC`);
  console.log(`  总花费：$${stats.totalSpent.toFixed(2)} USDC`);
  console.log(`  使用率：${stats.usageRate}`);

  if (stats.currentBalance < 2.0) {
    console.log('\n⚠️ 警告：余额低于 $2 USDC，请充值！');
  }

  console.log();
}

async function exampleRealWorldApp() {
  console.log('='.repeat(50));
  console.log('示例 6: 真实应用 - 多语言客服系统');
  console.log('='.repeat(50));

  const client = new x402Client('your_wallet_key');

  const conversations = [
    { user: 'Hello, I need help', lang: 'en' },
    { user: 'Bonjour, j\'ai un problème', lang: 'fr' },
    { user: 'Hola, necesito ayuda', lang: 'es' }
  ];

  console.log('🎧 客服系统启动...\n');

  for (const conv of conversations) {
    const result = await client.translate(conv.user, conv.lang, 'zh');
    
    if (result.success) {
      console.log(`[${conv.lang}] 用户：${conv.user}`);
      console.log(`[zh] 翻译：${result.data.translated_text}`);
      console.log(`💰 花费：${result.cost} USDC\n`);
    }
  }

  console.log(`💵 总成本：$${client.totalSpent.toFixed(2)} USDC`);
  console.log(`💡 如果自建翻译团队：约 $50/小时`);
  console.log(`🎯 使用 x402 API：$${client.totalSpent.toFixed(2)} USDC`);
  console.log(`✅ 节省了：$${(50 - client.totalSpent).toFixed(2)} USDC\n`);
}

async function main() {
  console.log('\n🚀 x402 API JavaScript SDK 完整示例\n');

  await exampleBasicUsage();
  await exampleErrorHandling();
  await exampleBatchProcessing();
  await exampleConcurrentCalls();
  await exampleUsageMonitoring();
  await exampleRealWorldApp();

  console.log('='.repeat(50));
  console.log('✅ 所有示例运行完成！');
  console.log('='.repeat(50));
}

// 运行示例
main().catch(console.error);

// ==================== React 组件示例 ====================

/**
 * React 翻译组件示例
 * 
 * 使用方法:
 * import Translator from './Translator';
 * 
 * function App() {
 *   return <Translator />;
 * }
 */

/*
import React, { useState } from 'react';
import x402Client from './x402-client';

function Translator() {
  const [input, setInput] = useState('');
  const [output, setOutput] = useState('');
  const [cost, setCost] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const client = new x402Client(process.env.REACT_APP_WALLET_KEY);

  const handleTranslate = async () => {
    if (!input.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const result = await client.translate(input, 'en', 'zh');
      setOutput(result.data.translated_text);
      setCost(result.cost);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="translator">
      <h2>x402 翻译器</h2>
      
      <textarea
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="输入英文..."
        rows={4}
      />
      
      <button onClick={handleTranslate} disabled={loading}>
        {loading ? '翻译中...' : `翻译 ($${cost})`}
      </button>
      
      {error && <div className="error">❌ {error}</div>}
      
      {output && (
        <div className="output">
          <h3>翻译结果:</h3>
          <p>{output}</p>
          <small>花费：${cost} USDC</small>
        </div>
      )}
      
      <style jsx>{`
        .translator {
          max-width: 600px;
          margin: 0 auto;
          padding: 20px;
        }
        textarea {
          width: 100%;
          padding: 10px;
          border: 1px solid #ddd;
          border-radius: 4px;
          font-size: 14px;
        }
        button {
          margin-top: 10px;
          padding: 10px 20px;
          background: #667eea;
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
        }
        button:disabled {
          background: #ccc;
        }
        .error {
          color: #ef4444;
          margin-top: 10px;
        }
        .output {
          margin-top: 20px;
          padding: 15px;
          background: #f5f5f5;
          border-radius: 4px;
        }
      `}</style>
    </div>
  );
}

export default Translator;
*/

// ==================== 导出模块 ====================

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { x402Client };
}
