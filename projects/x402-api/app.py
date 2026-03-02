#!/usr/bin/env python3
# =============================================================================
# 紫微智控 x402 API - Flask 主应用
# 功能：提供 HTTP API 接口，集成 x402 支付网关 + 紫微智控 Agent
# =============================================================================

from flask import Flask, request, jsonify
from x402_gateway import gateway
from ziwei_agents import AgentFactory
import os

app = Flask(__name__)

# API 配置
API_PRICES = {
    "architect": 0.10,    # T-01 架构设计
    "code-gen": 0.08,     # T-02 代码生成
    "code-audit": 0.05,   # T-03 代码审计
    "logic": 0.06,        # T-04 逻辑推理
    "translate": 0.02,    # T-05 翻译
    "long-text": 0.03,    # T-06 长文解析
    "crawl": 0.04,        # T-07 网络爬虫
    "vision": 0.15        # V-01 视觉解析
}


@app.route('/health', methods=['GET'])
def health():
    """健康检查"""
    return jsonify({
        "status": "ok",
        "service": "紫微智控 x402 API",
        "version": "1.0.0"
    })


@app.route('/api/v1/stats', methods=['GET'])
def stats():
    """获取收入统计"""
    stats = gateway.get_payment_stats()
    return jsonify({
        "success": True,
        "stats": stats,
        "prices": API_PRICES
    })


@app.route('/api/v1/architect', methods=['POST'])
def architect():
    """T-01 架构设计 - $0.10"""
    return handle_agent_request("architect", lambda agent, data: agent.design(data.get("requirements", "")))


@app.route('/api/v1/code-gen', methods=['POST'])
def code_gen():
    """T-02 代码生成 - $0.08"""
    return handle_agent_request("code-gen", lambda agent, data: agent.generate(
        data.get("language", "Python"),
        data.get("description", "")
    ))


@app.route('/api/v1/code-audit', methods=['POST'])
def code_audit():
    """T-03 代码审计 - $0.05"""
    return handle_agent_request("code-audit", lambda agent, data: agent.audit(
        data.get("code", ""),
        data.get("language", "Python")
    ))


@app.route('/api/v1/logic', methods=['POST'])
def logic():
    """T-04 逻辑推理 - $0.06"""
    return handle_agent_request("logic", lambda agent, data: agent.reason(data.get("problem", "")))


@app.route('/api/v1/translate', methods=['POST'])
def translate():
    """T-05 翻译 - $0.02"""
    return handle_agent_request("translate", lambda agent, data: agent.translate(
        data.get("text", ""),
        data.get("source_lang", "English"),
        data.get("target_lang", "Chinese")
    ))


@app.route('/api/v1/long-text', methods=['POST'])
def long_text():
    """T-06 长文解析 - $0.03"""
    return handle_agent_request("long-text", lambda agent, data: agent.analyze(
        data.get("text", ""),
        data.get("task", "summary")
    ))


@app.route('/api/v1/crawl', methods=['POST'])
def crawl():
    """T-07 网络爬虫 - $0.04"""
    return handle_agent_request("crawl", lambda agent, data: agent.crawl(
        data.get("url", ""),
        data.get("task", "extract")
    ))


@app.route('/api/v1/vision', methods=['POST'])
def vision():
    """V-01 视觉解析 - $0.15"""
    return handle_agent_request("vision", lambda agent, data: agent.analyze(
        data.get("image_url", ""),
        data.get("task", "describe")
    ))


def handle_agent_request(agent_type: str, call_func):
    """通用 Agent 请求处理"""

    # 1. 检查支付证明
    payment_proof = request.headers.get("x-payment-proof")

    if not payment_proof:
        # 2. 无支付证明 → 返回 402 支付请求
        request_id = gateway.generate_request_id()
        price = API_PRICES.get(agent_type, 0.05)

        response_402 = gateway.generate_402_response(price, request_id)

        return jsonify(response_402), 402

    # 3. 有支付证明 → 验证支付
    payment_info = gateway.verify_payment(payment_proof)

    if not payment_info:
        return jsonify({
            "error": "Invalid or expired payment proof"
        }), 402

    # 4. 支付验证通过 → 调用 Agent
    agent = AgentFactory.get_agent(agent_type)

    if not agent:
        return jsonify({
            "error": f"Agent type '{agent_type}' not found"
        }), 400

    data = request.get_json()
    result = call_func(agent, data)

    if result and "error" in result:
        return jsonify({
            "success": False,
            "error": result["error"]
        }), 500

    # 5. 返回结果
    return jsonify({
        "success": True,
        "result": result.get("result", ""),
        "agent": agent_type,
        "cost": API_PRICES.get(agent_type, 0.05),
        "payment": {
            "tx_hash": payment_info["tx_hash"],
            "amount": payment_info["amount"]
        },
        "model": result.get("model", ""),
        "tokens_used": result.get("tokens_used", 0) if result else 0
    }), 200


@app.errorhandler(404)
def not_found(e):
    """404 错误处理"""
    return jsonify({
        "error": "Endpoint not found"
    }), 404


@app.errorhandler(500)
def internal_error(e):
    """500 错误处理"""
    return jsonify({
        "error": "Internal server error"
    }), 500


if __name__ == '__main__':
    # 确保数据目录存在
    os.makedirs("/home/admin/Ziwei/projects/x402-api/data", exist_ok=True)

    # 启动服务
    print("=" * 70)
    print("🚀 紫微智控 x402 API - 启动中")
    print("=" * 70)
    print("📍 服务地址: http://localhost:5000")
    print("💰 支付方式: x402 (USDC on Base)")
    print("📊 统计接口: http://localhost:5000/api/v1/stats")
    print("=" * 70)

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )