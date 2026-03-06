#!/usr/bin/env python3
"""
x402 API - Python SDK 完整示例

包含：
- 基础调用
- 错误处理
- 批量调用
- 异步调用
- 使用量监控
"""

import asyncio
from typing import List, Dict
from dataclasses import dataclass

# 模拟 SDK（实际使用时 pip install x402-sdk）
@dataclass
class APIResponse:
    success: bool
    data: Dict
    cost: float
    error: str = None

class x402Client:
    """x402 API 客户端示例"""
    
    def __init__(self, wallet_key: str, base_url: str = "http://8.213.149.224:5002"):
        self.wallet_key = wallet_key
        self.base_url = base_url
        self.balance = 10.0  # 模拟余额
        self.total_spent = 0.0
    
    async def translate(self, text: str, source: str, target: str) -> APIResponse:
        """翻译 API"""
        cost = 0.02
        
        if self.balance < cost:
            return APIResponse(success=False, data={}, cost=0, error="余额不足")
        
        # 模拟 API 调用
        await asyncio.sleep(0.1)
        
        self.balance -= cost
        self.total_spent += cost
        
        return APIResponse(
            success=True,
            data={"translated_text": f"[{source}→{target}] {text}"},
            cost=cost
        )
    
    async def code_gen(self, prompt: str, language: str = "python") -> APIResponse:
        """代码生成 API"""
        cost = 0.08
        
        if self.balance < cost:
            return APIResponse(success=False, data={}, cost=0, error="余额不足")
        
        await asyncio.sleep(0.2)
        
        self.balance -= cost
        self.total_spent += cost
        
        return APIResponse(
            success=True,
            data={"code": f"# {language} code for: {prompt}\ndef solution():\n    pass"},
            cost=cost
        )
    
    async def batch_translate(self, texts: List[Dict]) -> List[APIResponse]:
        """批量翻译"""
        results = []
        
        # 批量折扣：超过 10 次打 8 折
        discount = 0.8 if len(texts) > 10 else 1.0
        
        for task in texts:
            cost = 0.02 * discount
            result = await self.translate(
                text=task['text'],
                source=task.get('source', 'en'),
                target=task.get('target', 'zh')
            )
            result.cost = cost
            results.append(result)
        
        return results
    
    def get_usage_stats(self) -> Dict:
        """获取使用统计"""
        return {
            "initial_balance": 10.0,
            "current_balance": self.balance,
            "total_spent": self.total_spent,
            "usage_rate": f"{(self.total_spent / 10.0 * 100):.1f}%"
        }


# ==================== 使用示例 ====================

async def example_basic_usage():
    """基础使用示例"""
    print("=" * 50)
    print("示例 1: 基础调用")
    print("=" * 50)
    
    client = x402Client(wallet_key="your_wallet_key")
    
    # 单次调用
    result = await client.translate("Hello, world!", "en", "zh")
    
    if result.success:
        print(f"✅ 翻译成功：{result.data['translated_text']}")
        print(f"💰 花费：{result.cost} USDC")
    else:
        print(f"❌ 失败：{result.error}")
    
    print()


async def example_error_handling():
    """错误处理示例"""
    print("=" * 50)
    print("示例 2: 错误处理")
    print("=" * 50)
    
    client = x402Client(wallet_key="your_wallet_key")
    client.balance = 0.01  # 余额不足
    
    result = await client.translate("Hello", "en", "zh")
    
    if not result.success:
        print(f"⚠️ 错误：{result.error}")
        print("💡 建议：检查余额或充值")
    
    print()


async def example_batch_processing():
    """批量处理示例"""
    print("=" * 50)
    print("示例 3: 批量调用（享受折扣）")
    print("=" * 50)
    
    client = x402Client(wallet_key="your_wallet_key")
    
    texts = [
        {"text": f"Message {i}", "source": "en", "target": "zh"}
        for i in range(15)  # 15 次，享受 8 折
    ]
    
    results = await client.batch_translate(texts)
    
    total_cost = sum(r.cost for r in results)
    print(f"📊 批量翻译 {len(results)} 条")
    print(f"💰 总花费：{total_cost:.4f} USDC")
    print(f"🎯 平均每次：{total_cost/len(results):.4f} USDC")
    print(f"💡 节省了：{(0.02*15 - total_cost):.4f} USDC")
    
    print()


async def example_concurrent_calls():
    """并发调用示例"""
    print("=" * 50)
    print("示例 4: 并发调用")
    print("=" * 50)
    
    client = x402Client(wallet_key="your_wallet_key")
    
    # 并发执行多个任务
    tasks = [
        client.translate(f"Text {i}", "en", "zh")
        for i in range(5)
    ]
    
    results = await asyncio.gather(*tasks)
    
    successful = sum(1 for r in results if r.success)
    total_cost = sum(r.cost for r in results if r.success)
    
    print(f"✅ 成功：{successful}/{len(results)}")
    print(f"💰 总花费：{total_cost:.4f} USDC")
    print(f"⚡ 并发执行，节省时间")
    
    print()


async def example_usage_monitoring():
    """使用量监控示例"""
    print("=" * 50)
    print("示例 5: 使用量监控")
    print("=" * 50)
    
    client = x402Client(wallet_key="your_wallet_key")
    
    # 模拟使用
    for i in range(10):
        await client.translate(f"Test {i}", "en", "zh")
    
    # 查看统计
    stats = client.get_usage_stats()
    
    print(f"📊 使用统计:")
    print(f"  初始余额：${stats['initial_balance']} USDC")
    print(f"  当前余额：${stats['current_balance']:.2f} USDC")
    print(f"  总花费：${stats['total_spent']:.2f} USDC")
    print(f"  使用率：{stats['usage_rate']}")
    
    # 告警
    if stats['current_balance'] < 2.0:
        print(f"\n⚠️ 警告：余额低于 $2 USDC，请充值！")
    
    print()


async def example_real_world_app():
    """真实应用场景：多语言客服系统"""
    print("=" * 50)
    print("示例 6: 真实应用 - 多语言客服系统")
    print("=" * 50)
    
    client = x402Client(wallet_key="your_wallet_key")
    
    # 模拟客服对话
    conversations = [
        {"user": "Hello, I need help", "lang": "en"},
        {"user": "Bonjour, j'ai un problème", "lang": "fr"},
        {"user": "Hola, necesito ayuda", "lang": "es"},
    ]
    
    print("🎧 客服系统启动...\n")
    
    for conv in conversations:
        # 翻译用户消息到中文
        result = await client.translate(
            conv['user'],
            conv['lang'],
            'zh'
        )
        
        if result.success:
            print(f"[{conv['lang']}] 用户：{conv['user']}")
            print(f"[zh] 翻译：{result.data['translated_text']}")
            print(f"💰 花费：{result.cost} USDC\n")
    
    print(f"💵 总成本：${client.total_spent:.2f} USDC")
    print(f"💡 如果自建翻译团队：约 $50/小时")
    print(f"🎯 使用 x402 API：${client.total_spent:.2f} USDC")
    print(f"✅ 节省了：${50 - client.total_spent:.2f} USDC")
    
    print()


async def main():
    """运行所有示例"""
    print("\n🚀 x402 API Python SDK 完整示例\n")
    
    await example_basic_usage()
    await example_error_handling()
    await example_batch_processing()
    await example_concurrent_calls()
    await example_usage_monitoring()
    await example_real_world_app()
    
    print("=" * 50)
    print("✅ 所有示例运行完成！")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
