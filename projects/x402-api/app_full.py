#!/usr/bin/env python3
# =============================================================================
# 紫微智控 x402 API - 完整版（集成阿里百炼）
# =============================================================================

import http.server
import socketserver
import json
import base64
import hashlib
import requests
from datetime import datetime
import os

# 配置
PORT = 5000
DATA_DIR = "/home/admin/Ziwei/projects/x402-api/data"
ENV_FILE = "/home/admin/Ziwei/projects/x402-api/.env"

# 加载环境变量
def load_env():
    env = {}
    try:
        with open(ENV_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    env[key.strip()] = value.strip()
    except:
        pass
    return env

ENV = load_env()
DASHSCOPE_API_KEY = ENV.get("DASHSCOPE_API_KEY", "sk-sp-deb52dabf75c47308911359d51a0a420")
DASHSCOPE_BASE_URL = "https://coding.dashscope.aliyuncs.com/v1"

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

# Agent 模型映射
AGENT_MODELS = {
    "architect": "bailian/qwen3-max-2026-01-23",
    "code-gen": "bailian/qwen3-coder-plus",
    "code-audit": "bailian/qwen3-coder-next",
    "logic": "bailian/qwen3.5-plus",
    "translate": "bailian/glm-4.7",
    "long-text": "bailian/kimi-k2.5",
    "crawl": "qwen-portal/coder-model",
    "vision": "qwen-portal/vision-model"
}

# Agent 提示词模板
AGENT_PROMPTS = {
    "architect": lambda data: f"""作为系统架构师，请设计以下需求的技术架构：

需求：{data.get('requirements', '')}

请提供：
1. 技术栈选择
2. 系统架构设计
3. 数据库设计
4. API 设计
5. 部署方案

要求：详细、专业、可落地。""",

    "code-gen": lambda data: f"""使用 {data.get('language', 'Python')} 编写代码实现以下功能：

功能描述：{data.get('description', '')}

要求：
1. 代码规范，有注释
2. 包含错误处理
3. 提供完整可运行的代码
4. 如果需要依赖，说明安装方法。""",

    "code-audit": lambda data: f"""作为安全审计专家，审计以下代码：

代码：
```
{data.get('code', '')}
```

语言：{data.get('language', 'Python')}

请检查：
1. 安全漏洞
2. 性能问题
3. 代码规范
4. 最佳实践
5. 修复建议""",

    "logic": lambda data: f"""使用逻辑推理分析以下问题：

问题：{data.get('problem', '')}

请提供：
1. 问题分析
2. 逻辑推理过程
3. 结论
4. 假设和局限性""",

    "translate": lambda data: f"""将以下文本翻译：

原文：{data.get('text', '')}
源语言：{data.get('source_lang', 'English')}
目标语言：{data.get('target_lang', 'Chinese')}

要求：准确翻译，保持原文语气。""",

    "long-text": lambda data: f"""分析以下长文本：

文本：{data.get('text', '')}
任务：{data.get('task', 'summary')}

请提供详细的分析结果。""",

    "crawl": lambda data: f"""设计网络爬虫访问以下 URL：

URL: {data.get('url', '')}
任务：{data.get('task', 'extract')}

请提供：
1. 爬虫策略
2. Python 代码
3. 数据提取方案

注意：遵守 robots.txt。""",

    "vision": lambda data: f"""分析以下图片：

图片 URL: {data.get('image_url', '')}
任务：{data.get('task', 'describe')}

请提供详细的图片分析。"""
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
    """调用阿里百炼 API (OpenAI 兼容格式)"""
    try:
        url = f"{DASHSCOPE_BASE_URL}/chat/completions"

        headers = {
            "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 2000,
            "temperature": 0.7
        }

        response = requests.post(url, json=payload, headers=headers, timeout=30)

        if response.status_code == 200:
            data = response.json()
            if "choices" in data and len(data["choices"]) > 0:
                result_text = data["choices"][0]["message"]["content"]
                return {
                    "result": result_text,
                    "model": model,
                    "tokens_used": data.get("usage", {}).get("total_tokens", 0)
                }

        return {"error": f"API 调用失败: {response.status_code} - {response.text}"}

    except Exception as e:
        return {"error": str(e)}


class X402APIHandler(http.server.BaseHTTPRequestHandler):
    """API 请求处理器"""

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
                "api_key_configured": bool(DASHSCOPE_API_KEY)
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

        payment_info = gateway.verify_payment(payment_proof)
        if not payment_info:
            self.send_json_response({"error": "Invalid payment proof"}, 402)
            return

        # 获取 Agent 类型
        agent_type = path.split('/')[-1]
        if agent_type not in AGENT_MODELS:
            self.send_json_response({"error": f"Unknown agent: {agent_type}"}, 400)
            return

        # 读取请求体
        content_length = int(self.headers.get('Content-Length', 0))
        request_data = self.rfile.read(content_length)
        try:
            data = json.loads(request_data.decode())
        except:
            data = {}

        # 检查 API Key
        if not DASHSCOPE_API_KEY:
            self.send_json_response({
                "success": False,
                "error": "API Key 未配置，请检查 .env 文件"
            }, 500)
            return

        # 调用阿里百炼 API
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
        print("🚀 紫微智控 x402 API - 启动中")
        print("=" * 70)
        print(f"📍 服务地址: http://localhost:{PORT}")
        print(f"💰 支付方式: x402 (USDC on Base)")
        print(f"📊 统计接口: http://localhost:{PORT}/api/v1/stats")
        print(f"🏥 健康检查: http://localhost:{PORT}/health")
        print(f"🔑 API Key: {'✅ 已配置' if DASHSCOPE_API_KEY else '❌ 未配置'}")
        print("=" * 70)

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 服务器已停止")


if __name__ == '__main__':
    start_server()