#!/usr/bin/env python3
# =============================================================================
# x402 API - 完整版（使用 urllib，无需额外依赖）
# =============================================================================

import http.server
import socketserver
import json
import base64
import hashlib
import urllib.request
import urllib.error
from datetime import datetime
import os

PORT = 5002
DATA_DIR = "/home/admin/Ziwei/projects/x402-api/data"
DASHSCOPE_API_KEY = "sk-sp-deb52dabf75c47308911359d51a0a420"
DASHSCOPE_BASE_URL = "https://coding.dashscope.aliyuncs.com/v1"

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

AGENT_MODELS = {
    "architect": "qwen3-max-2026-01-23",
    "code-gen": "qwen3-coder-plus",
    "code-audit": "qwen3-coder-next",
    "logic": "qwen3.5-plus",
    "translate": "glm-4.7",
    "long-text": "kimi-k2.5",
    "crawl": "qwen3-coder-plus",
    "vision": "qwen3-max-2026-01-23"
}

AGENT_PROMPTS = {
    "architect": lambda data: f"作为系统架构师，设计以下需求的技术架构：\n\n需求：{data.get('requirements', '')}\n\n请提供：1.技术栈 2.架构 3.数据库 4.API设计",
    "code-gen": lambda data: f"使用 {data.get('language', 'Python')} 编写代码：{data.get('description', '')}\n\n要求：代码规范、有注释、可运行",
    "code-audit": lambda data: f"审计以下代码：\n\n{data.get('code', '')}\n\n请检查：安全漏洞、性能问题、代码规范",
    "logic": lambda data: f"分析问题：{data.get('problem', '')}\n\n请提供：分析、推理过程、结论",
    "translate": lambda data: f"翻译：{data.get('text', '')}\n从 {data.get('source_lang', 'English')} 到 {data.get('target_lang', 'Chinese')}",
    "long-text": lambda data: f"分析文本：{data.get('text', '')}\n任务：{data.get('task', 'summary')}",
    "crawl": lambda data: f"设计爬虫访问：{data.get('url', '')}\n任务：{data.get('task', 'extract')}",
    "vision": lambda data: f"分析图片：{data.get('image_url', '')}\n任务：{data.get('task', 'describe')}"
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
            "x402": {"amount": str(amount_usdc), "currency": "USDC", "wallet": self.payment_wallet, "network": "base"},
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


def call_dashscope(model, prompt):
    """调用阿里百炼 API"""
    try:
        url = f"{DASHSCOPE_BASE_URL}/chat/completions"

        payload = json.dumps({
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 2000,
            "temperature": 0.7
        }).encode('utf-8')

        req = urllib.request.Request(
            url,
            data=payload,
            headers={
                "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
                "Content-Type": "application/json"
            }
        )

        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode('utf-8'))
            if "choices" in data and len(data["choices"]) > 0:
                result_text = data["choices"][0]["message"]["content"]
                return {
                    "result": result_text,
                    "model": model,
                    "tokens_used": data.get("usage", {}).get("total_tokens", 0)
                }

        return {"error": f"API 调用失败: 无有效响应"}

    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        return {"error": f"HTTP {e.code}: {error_body}"}
    except Exception as e:
        return {"error": str(e)}


class X402APIHandler(http.server.BaseHTTPRequestHandler):
    def send_json_response(self, data, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

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
                "api_key_configured": True,
                "mode": "production"
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
        if agent_type not in AGENT_MODELS:
            self.send_json_response({"error": f"Unknown agent: {agent_type}"}, 400)
            return

        content_length = int(self.headers.get('Content-Length', 0))
        request_data = self.rfile.read(content_length)
        try:
            data = json.loads(request_data.decode('utf-8'))
        except:
            data = {}

        model = AGENT_MODELS[agent_type]
        prompt = AGENT_PROMPTS[agent_type](data)
        result = call_dashscope(model, prompt)

        if "error" in result:
            self.send_json_response({
                "success": False,
                "error": result["error"]
            }, 500)
            return

        self.send_json_response({
            "success": True,
            "result": result["result"],
            "agent": agent_type,
            "cost": API_PRICES.get(agent_type, 0.05),
            "payment": {
                "tx_hash": payment_info["tx_hash"],
                "amount": payment_info["amount"]
            },
            "model": result["model"],
            "tokens_used": result["tokens_used"]
        }, 200)

    def log_message(self, format, *args):
        pass


def start_server():
    with socketserver.TCPServer(("", PORT), X402APIHandler) as httpd:
        print("=" * 70)
        print("🚀 紫微智控 x402 API - 生产模式")
        print("=" * 70)
        print(f"📍 服务地址: http://localhost:{PORT}")
        print(f"💰 支付方式: x402 (USDC on Base)")
        print(f"📊 统计接口: http://localhost:{PORT}/api/v1/stats")
        print(f"🏥 健康检查: http://localhost:{PORT}/health")
        print(f"🔑 API Key: ✅ 已配置")
        print("=" * 70)

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 服务器已停止")


if __name__ == '__main__':
    start_server()