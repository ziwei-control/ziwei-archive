#!/usr/bin/env python3
"""
x402 API 密钥自动发放 Web 服务

功能：
1. 提供前端页面供用户支付获取密钥
2. 自动验证 Base 链上 USDC 交易
3. 生成并返回 API 凭证

启动方式：
python3 api_key_server.py

访问：
http://localhost:8080
"""

from flask import Flask, render_template, jsonify, request
import hashlib
import time
import requests
from datetime import datetime

app = Flask(__name__)

# ============ 配置 ============
CONFIG = {
    "PAYMENT_ADDRESS": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
    "EXPECTED_AMOUNT": 0.05,  # USDC
    "TOLERANCE": 0.02,  # 容差
    "REAL_API_URL": "8.213.149.224",
    "BASESCAN_API_KEY": "",  # TODO: 替换为你的 BaseScan API Key
    "TIME_WINDOW": 300,  # 5 分钟内交易有效
}

# ============ API Key 生成器 ============
def generate_api_key(tx_hash: str, timestamp: int) -> str:
    """生成唯一的 API Key"""
    salt = "x402_secret_salt_2026"
    data = f"{tx_hash}{timestamp}{salt}"
    hash_obj = hashlib.sha256(data.encode())
    hash_hex = hash_obj.hexdigest()[:16]
    return f"x402_{hash_hex}_{timestamp:x}"

# ============ BaseScan 查询 ============
def query_basescan(address: str) -> dict:
    """查询 BaseScan 获取交易记录"""
    api_key = CONFIG["BASESCAN_API_KEY"] or "YourBaseScanApiKey"
    url = "https://api.basescan.org/api"
    
    params = {
        "module": "account",
        "action": "tokentx",
        "address": address,
        "startblock": 0,
        "endblock": 99999999,
        "sort": "desc",
        "apikey": api_key
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"status": "0", "message": str(e), "result": []}

# ============ 交易验证 ============
def verify_payment(tx_hash: str = "") -> dict:
    """
    验证支付交易
    
    Returns:
        {
            "success": bool,
            "message": str,
            "api_base_url": str (if success),
            "api_key": str (if success),
            "tx_hash": str (if success),
            "amount": float (if success)
        }
    """
    # 查询交易记录
    data = query_basescan(CONFIG["PAYMENT_ADDRESS"])
    
    if data.get("status") != "1" or not data.get("result"):
        return {
            "success": False,
            "message": "未查询到交易记录"
        }
    
    # 查找最近的合格交易
    now = time.time()
    results = data.get("result", [])
    
    for tx in results:
        # 检查是否是 USDC
        token_symbol = tx.get("tokenSymbol", "")
        token_name = tx.get("tokenName", "")
        
        if token_symbol not in ["USDC", "USD Coin"] and "USD Coin" not in token_name:
            continue
        
        # 如果指定了 tx_hash，检查是否匹配
        if tx_hash and tx.get("hash", "").lower() != tx_hash.lower():
            continue
        
        try:
            # 检查金额
            decimal = int(tx.get("tokenDecimal", 6))
            value = int(tx.get("value", 0))
            amount = value / (10 ** decimal)
            
            if abs(amount - CONFIG["EXPECTED_AMOUNT"]) > CONFIG["TOLERANCE"]:
                continue
            
            # 检查时间
            tx_time = int(tx.get("timeStamp", 0))
            if (now - tx_time) > CONFIG["TIME_WINDOW"]:
                continue
            
            # 验证成功，生成 API Key
            api_key = generate_api_key(tx.get("hash"), tx_time)
            
            return {
                "success": True,
                "message": "验证成功",
                "api_base_url": CONFIG["REAL_API_URL"],
                "api_key": api_key,
                "tx_hash": tx.get("hash"),
                "amount": amount,
                "timestamp": tx_time,
                "from_address": tx.get("from")
            }
            
        except Exception as e:
            continue
    
    return {
        "success": False,
        "message": "未找到符合条件的交易，请确保发送 0.05 USDC (±0.02) 到指定地址"
    }

# ============ 路由 ============
@app.route("/")
def index():
    """首页 - API 密钥获取页面"""
    return render_template("api-key-generator.html")

@app.route("/api/verify", methods=["POST"])
def api_verify():
    """API 验证端点"""
    data = request.get_json() or {}
    tx_hash = data.get("tx_hash", "")
    
    result = verify_payment(tx_hash)
    return jsonify(result)

@app.route("/api/status", methods=["GET"])
def api_status():
    """API 状态检查"""
    return jsonify({
        "status": "ok",
        "payment_address": CONFIG["PAYMENT_ADDRESS"],
        "expected_amount": CONFIG["EXPECTED_AMOUNT"],
        "tolerance": CONFIG["TOLERANCE"],
        "time_window": CONFIG["TIME_WINDOW"]
    })

@app.route("/api/transactions", methods=["GET"])
def api_transactions():
    """获取最近的交易记录（用于监控）"""
    data = query_basescan(CONFIG["PAYMENT_ADDRESS"])
    
    if data.get("status") != "1":
        return jsonify({"status": "error", "message": data.get("message", "Unknown error")})
    
    # 过滤 USDC 交易
    usdc_txs = []
    for tx in data.get("result", [])[:20]:  # 最近 20 条
        token_symbol = tx.get("tokenSymbol", "")
        token_name = tx.get("tokenName", "")
        
        if token_symbol in ["USDC", "USD Coin"] or "USD Coin" in token_name:
            try:
                decimal = int(tx.get("tokenDecimal", 6))
                value = int(tx.get("value", 0))
                amount = value / (10 ** decimal)
                
                usdc_txs.append({
                    "hash": tx.get("hash"),
                    "from": tx.get("from"),
                    "to": tx.get("to"),
                    "amount": amount,
                    "timestamp": tx.get("timeStamp"),
                    "time": datetime.fromtimestamp(int(tx.get("timeStamp", 0))).isoformat()
                })
            except:
                continue
    
    return jsonify({
        "status": "1",
        "result": usdc_txs
    })

# ============ 错误处理 ============
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not Found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal Server Error"}), 500

# ============ 主程序 ============
if __name__ == "__main__":
    print("=" * 60)
    print("x402 API 密钥自动发放服务")
    print("=" * 60)
    print(f"收款地址：{CONFIG['PAYMENT_ADDRESS']}")
    print(f"期望金额：{CONFIG['EXPECTED_AMOUNT']} USDC (容差：±{CONFIG['TOLERANCE']})")
    print(f"真实 API 地址：{CONFIG['REAL_API_URL']}")
    print("=" * 60)
    print("\n启动 Web 服务...")
    print("访问地址：http://localhost:8080")
    print("=" * 60)
    
    # 创建 templates 目录
    import os
    os.makedirs("templates", exist_ok=True)
    
    # 启动服务
    app.run(host="0.0.0.0", port=8080, debug=False)
