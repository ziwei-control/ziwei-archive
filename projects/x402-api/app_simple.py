#!/usr/bin/env python3
# =============================================================================
# 紫微智控 x402 API - 简化版 (不依赖 Flask)
# 功能：提供 HTTP API 接口，集成 x402 支付网关 + 紫微智控 Agent
# =============================================================================

import http.server
import socketserver
import json
import base64
import hashlib
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs
import os

# 配置
PORT = 5000
DATA_DIR = "/home/admin/Ziwei/projects/x402-api/data"

# 确保数据目录存在
os.makedirs(DATA_DIR, exist_ok=True)

# API 价格
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
    """x402 支付网关"""

    def __init__(self):
        self.payment_wallet = "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
        self.payments = {}
        self.load_payments()

    def load_payments(self):
        try:
            with open(os.path.join(DATA_DIR, "payments.json"), "r") as f:
                data = json.load(f)
                self.payments = data.get("payments", {})
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

            # 简化验证（生产环境需要区块链验证）
            tx_hash = proof_data.get("tx_hash", "")
            if not tx_hash:
                return None

            if tx_hash in self.payments:
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
            "today_earnings": total,  # 简化
            "total_transactions": len([p for p in self.payments.values() if p.get("verified")])
        }


# 全局网关实例
gateway = X402Gateway()


class X402APIHandler(http.server.BaseHTTPRequestHandler):
    """API 请求处理器"""

    def send_json_response(self, data, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def send_402_payment_required(self, amount, request_id):
        response = gateway.generate_402_response(amount, request_id)
        self.send_json_response(response, 402)

    def do_GET(self):
        """处理 GET 请求"""
        path = self.path

        if path == '/health':
            self.send_json_response({
                "status": "ok",
                "service": "紫微智控 x402 API",
                "version": "1.0.0"
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
        """处理 POST 请求"""
        path = self.path
        payment_proof = self.headers.get('x-payment-proof')

        # 检查支付证明
        if not payment_proof:
            # 返回 402 支付请求
            request_id = hashlib.sha256(f"{datetime.now().isoformat()}".encode()).hexdigest()[:16]

            if '/api/v1/architect' in path:
                self.send_402_payment_required(0.10, request_id)
            elif '/api/v1/code-gen' in path:
                self.send_402_payment_required(0.08, request_id)
            elif '/api/v1/code-audit' in path:
                self.send_402_payment_required(0.05, request_id)
            elif '/api/v1/logic' in path:
                self.send_402_payment_required(0.06, request_id)
            elif '/api/v1/translate' in path:
                self.send_402_payment_required(0.02, request_id)
            elif '/api/v1/long-text' in path:
                self.send_402_payment_required(0.03, request_id)
            elif '/api/v1/crawl' in path:
                self.send_402_payment_required(0.04, request_id)
            elif '/api/v1/vision' in path:
                self.send_402_payment_required(0.15, request_id)
            else:
                self.send_json_response({"error": "Unknown endpoint"}, 404)

            return

        # 验证支付
        payment_info = gateway.verify_payment(payment_proof)
        if not payment_info:
            self.send_json_response({"error": "Invalid payment proof"}, 402)
            return

        # 模拟 Agent 调用（实际需要调用阿里百炼 API）
        agent_type = path.split('/')[-1]

        # 读取请求体
        content_length = int(self.headers.get('Content-Length', 0))
        request_data = self.rfile.read(content_length)
        try:
            data = json.loads(request_data.decode())
        except:
            data = {}

        # 模拟返回结果
        result = f"[{agent_type}] 这是一个模拟结果。实际部署需要连接阿里百炼 API。"

        self.send_json_response({
            "success": True,
            "result": result,
            "agent": agent_type,
            "cost": API_PRICES.get(agent_type, 0.05),
            "payment": {
                "tx_hash": payment_info["tx_hash"],
                "amount": payment_info["amount"]
            },
            "model": "bailian/qwen3-coder-plus",
            "tokens_used": 500
        }, 200)

    def log_message(self, format, *args):
        """禁用默认日志"""
        pass


def start_server():
    """启动服务器"""
    with socketserver.TCPServer(("", PORT), X402APIHandler) as httpd:
        print("=" * 70)
        print("🚀 紫微智控 x402 API - 启动中")
        print("=" * 70)
        print(f"📍 服务地址: http://localhost:{PORT}")
        print(f"💰 支付方式: x402 (USDC on Base)")
        print(f"📊 统计接口: http://localhost:{PORT}/api/v1/stats")
        print(f"🏥 健康检查: http://localhost:{PORT}/health")
        print("=" * 70)
        print("按 Ctrl+C 停止服务器")
        print("=" * 70)

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 服务器已停止")


if __name__ == '__main__':
    start_server()