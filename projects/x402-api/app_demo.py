#!/usr/bin/env python3
# =============================================================================
# x402 API - 模拟模式（不调用真实 API，仅演示流程）
# =============================================================================

import http.server
import socketserver
import json
import base64
import hashlib
from datetime import datetime
import os

PORT = 5001
DATA_DIR = "/home/admin/Ziwei/projects/x402-api/data"
os.makedirs(DATA_DIR, exist_ok=True)

API_PRICES = {
    "architect": 0.10,
    "code-gen": 0.08,
    "code-audit": 0.05,
    "logic": 0.06,
    "translate": 0.02,
    "long-text": 0.03,
    "crawl": 0.04,
    "vision": 0.15
}


class X402Gateway:
    def __init__(self):
        self.payment_wallet = "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
        self.payments = {}
        self.load_payments()

    def load_payments(self):
        try:
            with open(os.path.join(DATA_DIR, "payments.json"), "r") as f:
                self.payments = json.load(f).get("payments", {})
        except:
            self.payments = {}

    def save_payments(self):
        with open(os.path.join(DATA_DIR, "payments.json"), "w") as f:
            json.dump({"payments": self.payments}, f, indent=2)

    def generate_402_response(self, amount_usdc, request_id):
        return {
            "x402": {
                "amount": str(amount_usdc),
                "currency": "USDC",
                "wallet": self.payment_wallet,
                "network": "base"
            },
            "request_id": request_id,
            "timestamp": datetime.now().isoformat()
        }

    def verify_payment(self, payment_proof):
        try:
            proof_data = json.loads(base64.b64decode(payment_proof).decode())
            tx_hash = proof_data.get("tx_hash", "")
            if not tx_hash or tx_hash in self.payments:
                return None
            payment_info = {
                "tx_hash": tx_hash,
                "amount": float(proof_data.get("amount", 0)),
                "sender": proof_data.get("sender", ""),
                "timestamp": datetime.now().isoformat(),
                "verified": True
            }
            self.payments[tx_hash] = payment_info
            self.save_payments()
            return payment_info
        except:
            return None

    def get_stats(self):
        total = sum(p["amount"] for p in self.payments.values() if p.get("verified"))
        return {
            "total_earnings": total,
            "today_earnings": total,
            "total_transactions": len([p for p in self.payments.values() if p.get("verified")])
        }


gateway = X402Gateway()


# 模拟 Agent 响应
MOCK_RESPONSES = {
    "architect": "## 系统架构设计\n\n### 技术栈\n- 后端: Python + Flask\n- 数据库: PostgreSQL\n- 前端: Vue.js\n- 部署: Docker + Kubernetes\n\n### 架构图\n```\n客户端 → 负载均衡 → API 服务 → 数据库\n```\n\n[模拟响应 - 需要配置有效的阿里百炼 API Key]",
    "code-gen": "```python\ndef fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)\n```\n\n[模拟响应 - 需要配置有效的阿里百炼 API Key]",
    "code-audit": """## 代码审计报告\n\n### 发现的问题：\n1. ⚠️ 函数缺少输入验证\n2. ⚠️ 没有错误处理\n3. ⚠️ 函数名不规范\n\n### 建议修复：\n- 添加参数类型检查\n- 添加异常处理\n- 遵循 PEP 8 规范\n\n[模拟响应 - 需要配置有效的阿里百炼 API Key]""",
    "logic": "## 逻辑分析\n\n### 推理过程：\n1. 分析问题的前提条件\n2. 识别关键变量\n3. 应用逻辑规则\n4. 得出结论\n\n### 结论：\n基于已知条件，结论是合理的。\n\n[模拟响应 - 需要配置有效的阿里百炼 API Key]",
    "translate": "翻译结果：Hello, world!\n\n[模拟响应 - 需要配置有效的阿里百炼 API Key]",
    "long-text": "## 文本摘要\n\n[模拟响应 - 需要配置有效的阿里百炼 API Key]",
    "crawl": "```python\nimport requests\nfrom bs4 import BeautifulSoup\n\ndef scrape_url(url):\n    response = requests.get(url)\n    soup = BeautifulSoup(response.text, 'html.parser')\n    return soup.get_text()\n```\n\n[模拟响应 - 需要配置有效的阿里百炼 API Key]",
    "vision": "## 图片分析\n\n这是一张[描述图片内容]的图片。\n\n[模拟响应 - 需要配置有效的阿里百炼 API Key]"
}


class X402APIHandler(http.server.BaseHTTPRequestHandler):
    def send_json_response(self, data, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())

    def send_402_payment_required(self, amount, request_id):
        response = gateway.generate_402_response(amount, request_id)
        self.send_json_response(response, 402)

    def do_GET(self):
        path = self.path
        if path == '/health':
            self.send_json_response({
                "status": "ok",
                "service": "紫微智控 x402 API",
                "version": "1.0.0",
                "mode": "simulation",
                "note": "模拟模式 - 需要配置有效的阿里百炼 API Key 才能调用真实 AI 模型"
            })
        elif path == '/api/v1/stats':
            stats = gateway.get_stats()
            self.send_json_response({
                "success": True,
                "stats": stats,
                "prices": API_PRICES
            })
        else:
            self.send_json_response({"error": "Not found"}, 404)

    def do_POST(self):
        path = self.path
        payment_proof = self.headers.get('x-payment-proof')

        if not payment_proof:
            request_id = hashlib.sha256(f"{datetime.now().isoformat()}".encode()).hexdigest()[:16]

            price = 0.05
            if '/api/v1/architect' in path: price = 0.10
            elif '/api/v1/code-gen' in path: price = 0.08
            elif '/api/v1/code-audit' in path: price = 0.05
            elif '/api/v1/logic' in path: price = 0.06
            elif '/api/v1/translate' in path: price = 0.02
            elif '/api/v1/long-text' in path: price = 0.03
            elif '/api/v1/crawl' in path: price = 0.04
            elif '/api/v1/vision' in path: price = 0.15

            self.send_402_payment_required(price, request_id)
            return

        payment_info = gateway.verify_payment(payment_proof)
        if not payment_info:
            self.send_json_response({"error": "Invalid payment proof"}, 402)
            return

        agent_type = path.split('/')[-1]
        if agent_type not in MOCK_RESPONSES:
            self.send_json_response({"error": f"Unknown agent: {agent_type}"}, 400)
            return

        # 返回模拟响应
        result = MOCK_RESPONSES[agent_type]

        self.send_json_response({
            "success": True,
            "result": result,
            "agent": agent_type,
            "cost": API_PRICES.get(agent_type, 0.05),
            "payment": {
                "tx_hash": payment_info["tx_hash"],
                "amount": payment_info["amount"]
            },
            "model": "simulation",
            "tokens_used": 500
        }, 200)

    def log_message(self, format, *args):
        pass


def start_server():
    with socketserver.TCPServer(("", PORT), X402APIHandler) as httpd:
        print("=" * 70)
        print("🚀 紫微智控 x402 API - 模拟模式")
        print("=" * 70)
        print(f"📍 服务地址: http://localhost:{PORT}")
        print(f"💰 支付方式: x402 (USDC on Base)")
        print(f"📊 统计接口: http://localhost:{PORT}/api/v1/stats")
        print(f"🏥 健康检查: http://localhost:{PORT}/health")
        print()
        print("⚠️ 当前为模拟模式，返回预设的模拟响应")
        print("⚠️ 要使用真实 AI 模型，需要配置有效的阿里百炼 API Key")
        print("=" * 70)

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 服务器已停止")


if __name__ == '__main__':
    start_server()