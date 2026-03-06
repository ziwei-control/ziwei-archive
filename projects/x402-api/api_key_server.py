#!/usr/bin/env python3
"""
x402 API 密钥自动发放 Web 服务（生产环境版）

功能：
1. 提供前端页面供用户支付获取密钥
2. 自动验证 Base 链上 USDC 交易（无需 API Key）
3. 生成并返回 API 凭证
4. 频率限制、HTTPS 支持、数据库存储

启动方式：
python3 api_key_server.py

访问：
http://8.213.149.224:8080 或 https://localhost:4433
"""

from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import hashlib
import time
import requests
import sqlite3
import json
import os
from datetime import datetime
from functools import wraps

app = Flask(__name__, static_folder='.', static_url_path='')

# ============ CORS 支持 ============
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

# ============ 配置 ============
CONFIG = {
    "PAYMENT_ADDRESS": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
    "EXPECTED_AMOUNT": 0.05,  # USDC
    "TOLERANCE": 0.02,  # 容差范围
    "REAL_API_URL": "8.213.149.224",  # 真实 API 服务器地址
    "BASESCAN_API_KEY": "",  # 留空使用公开 API（无需注册）
    "TIME_WINDOW": 3600,  # 60 分钟内交易有效
    "DB_PATH": "api_keys.db",
    "HTTPS_ENABLED": False,  # 生产环境建议开启
    "SSL_CERT": "cert.pem",
    "SSL_KEY": "key.pem",
}

# ============ 数据库初始化 ============
def init_db():
    """初始化数据库"""
    conn = sqlite3.connect(CONFIG["DB_PATH"])
    cursor = conn.cursor()
    
    # 创建 API Key 表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS api_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            api_key TEXT UNIQUE NOT NULL,
            api_base_url TEXT NOT NULL,
            tx_hash TEXT UNIQUE NOT NULL,
            amount REAL NOT NULL,
            from_address TEXT,
            timestamp INTEGER NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            is_active INTEGER DEFAULT 1
        )
    """)
    
    # 创建访问日志表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS access_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip_address TEXT,
            endpoint TEXT,
            status TEXT,
            message TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 创建索引
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_api_key ON api_keys(api_key)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tx_hash ON api_keys(tx_hash)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON api_keys(created_at)")
    
    conn.commit()
    conn.close()
    print("✅ 数据库初始化完成")

# ============ 数据库操作 ============
def save_api_key(api_key, api_base_url, tx_hash, amount, from_address, timestamp):
    """保存 API Key 到数据库"""
    conn = sqlite3.connect(CONFIG["DB_PATH"])
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT OR REPLACE INTO api_keys 
            (api_key, api_base_url, tx_hash, amount, from_address, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (api_key, api_base_url, tx_hash, amount, from_address, timestamp))
        conn.commit()
        return True
    except Exception as e:
        print(f"❌ 保存失败：{e}")
        return False
    finally:
        conn.close()

def get_api_key(tx_hash):
    """从数据库查询 API Key"""
    conn = sqlite3.connect(CONFIG["DB_PATH"])
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT api_key, api_base_url, amount, timestamp 
        FROM api_keys 
        WHERE tx_hash = ? AND is_active = 1
    """, (tx_hash,))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            "api_key": result[0],
            "api_base_url": result[1],
            "amount": result[2],
            "timestamp": result[3]
        }
    return None

def log_access(ip_address, endpoint, status, message):
    """记录访问日志"""
    conn = sqlite3.connect(CONFIG["DB_PATH"])
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO access_logs (ip_address, endpoint, status, message)
        VALUES (?, ?, ?, ?)
    """, (ip_address, endpoint, status, message))
    
    conn.commit()
    conn.close()

# ============ 频率限制装饰器 ============
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"  # 使用内存存储（简化配置）
)

# ============ API Key 生成器 ============
def generate_api_key(tx_hash: str, timestamp: int) -> str:
    """
    生成唯一的 API Key
    
    算法：SHA256(tx_hash + timestamp + salt)
    格式：x402_{hash}_{timestamp}
    """
    salt = "x402_secret_salt_2026_production"
    data = f"{tx_hash}{timestamp}{salt}"
    hash_obj = hashlib.sha256(data.encode())
    hash_hex = hash_obj.hexdigest()[:16]
    return f"x402_{hash_hex}_{timestamp:x}"

# ============ BaseScan 查询（无需 API Key） ============
def query_basescan(address: str) -> dict:
    """
    查询 BaseScan 获取交易记录
    
    使用公开 API，无需 API Key
    限制：每秒 1 次请求
    """
    # 优先使用公开 API（无需 Key）
    url = "https://api.basescan.org/api"
    
    params = {
        "module": "account",
        "action": "tokentx",
        "address": address,
        "startblock": 0,
        "endblock": 99999999,
        "sort": "desc"
    }
    
    # 如果有 API Key 则添加
    if CONFIG["BASESCAN_API_KEY"]:
        params["apikey"] = CONFIG["BASESCAN_API_KEY"]
    
    try:
        # 添加重试逻辑
        for attempt in range(3):
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "1":
                    return data
                elif data.get("message") == "Max rate limit reached":
                    # 达到速率限制，等待后重试
                    time.sleep(2 ** attempt)
                    continue
                else:
                    return {"status": "0", "message": data.get("message", "Unknown error"), "result": []}
            else:
                time.sleep(2 ** attempt)
        
        return {"status": "0", "message": "请求失败，请稍后重试", "result": []}
        
    except Exception as e:
        return {"status": "0", "message": str(e), "result": []}

# ============ 交易验证 ============
def verify_payment(tx_hash: str = "", from_address: str = "") -> dict:
    """
    验证支付交易
    
    验证逻辑：
    1. 查询 BaseScan 获取交易记录
    2. 检查是否是 USDC 交易
    3. 检查金额是否在容差范围内（0.05 ± 0.02 USDC）
    4. 检查时间是否在时间窗口内（60 分钟）
    5. 生成并保存 API Key
    
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
    # 先检查数据库是否已存在
    if tx_hash:
        cached = get_api_key(tx_hash)
        if cached:
            return {
                "success": True,
                "message": "验证成功（缓存）",
                "api_base_url": cached["api_base_url"],
                "api_key": cached["api_key"],
                "tx_hash": tx_hash,
                "amount": cached["amount"],
                "cached": True
            }
    
    # 查询交易记录
    data = query_basescan(CONFIG["PAYMENT_ADDRESS"])
    
    if data.get("status") != "1" or not data.get("result"):
        return {
            "success": False,
            "message": "未查询到交易记录，请确保已发送 USDC"
        }
    
    # 查找最近的合格交易
    now = time.time()
    results = data.get("result", [])
    
    # 容差检查：金额在 [EXPECTED_AMOUNT - TOLERANCE, EXPECTED_AMOUNT + TOLERANCE] 范围内
    min_amount = CONFIG["EXPECTED_AMOUNT"] - CONFIG["TOLERANCE"]  # 0.03 USDC
    max_amount = CONFIG["EXPECTED_AMOUNT"] + CONFIG["TOLERANCE"]  # 0.07 USDC
    
    # 时间窗口：60 分钟
    time_window = CONFIG["TIME_WINDOW"]  # 3600 秒
    
    for tx in results:
        # 检查是否是 USDC 交易
        token_symbol = tx.get("tokenSymbol", "")
        token_name = tx.get("tokenName", "")
        
        is_usdc = (token_symbol in ["USDC", "USD Coin"] or 
                   "USD Coin" in token_name or
                   token_symbol == "USDC.e")
        
        if not is_usdc:
            continue
        
        # 如果指定了 tx_hash，检查是否匹配
        if tx_hash and tx.get("hash", "").lower() != tx_hash.lower():
            continue
        
        # 如果指定了 from_address，检查发送方是否匹配
        if from_address and tx.get("from", "").lower() != from_address.lower():
            continue
        
        try:
            # 检查金额（容差范围检查）
            decimal = int(tx.get("tokenDecimal", 6))
            value = int(tx.get("value", 0))
            amount = value / (10 ** decimal)
            
            # 金额必须在 [0.03, 0.07] USDC 范围内
            if amount < min_amount or amount > max_amount:
                print(f"⚠️ 金额不符合：{amount} USDC (需要 {min_amount}-{max_amount})")
                continue
            
            # 检查时间（60 分钟内）
            tx_time = int(tx.get("timeStamp", 0))
            if (now - tx_time) > time_window:
                print(f"⚠️ 交易超时：{tx_time}（超过 60 分钟）")
                continue
            
            # 验证成功，生成 API Key
            api_key = generate_api_key(tx.get("hash"), tx_time)
            
            # 保存到数据库
            saved = save_api_key(
                api_key=api_key,
                api_base_url=CONFIG["REAL_API_URL"],
                tx_hash=tx.get("hash"),
                amount=amount,
                from_address=tx.get("from"),
                timestamp=tx_time
            )
            
            if saved:
                print(f"✅ 验证成功：{tx.get('hash')} - {amount} USDC - API Key: {api_key}")
                
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
            else:
                return {
                    "success": False,
                    "message": "保存 API Key 失败，请稍后重试"
                }
            
        except Exception as e:
            print(f"⚠️ 解析交易失败：{e}")
            continue
    
    return {
        "success": False,
        "message": f"未找到符合条件的交易，请发送 {CONFIG['EXPECTED_AMOUNT']} USDC (容差：±{CONFIG['TOLERANCE']}) 到指定地址"
    }

# ============ 路由 ============
@app.route("/")
@limiter.limit("100 per day")
def index():
    """首页 - 重定向到 API 密钥获取页面"""
    return send_from_directory('.', 'get-api-key.html')

@app.route("/get-api-key.html")
@limiter.limit("100 per day")
def get_api_key_page():
    """API 密钥获取页面"""
    return send_from_directory('.', 'get-api-key.html')

@app.route("/api-key-generator.html")
@limiter.limit("100 per day")
def api_key_generator_page():
    """旧的 API 密钥生成页面（兼容）"""
    return send_from_directory('.', 'api-key-generator.html')

@app.route("/api/verify", methods=["POST"])
@limiter.limit("10 per minute")  # 每分钟最多 10 次验证
def api_verify():
    """API 验证端点"""
    ip = request.remote_addr
    data = request.get_json() or {}
    
    # 支持两种输入：发送地址或交易 hash
    from_address = data.get("from_address", "").strip()
    tx_hash = data.get("tx_hash", "").strip()
    
    # 验证输入
    if not from_address and not tx_hash:
        return jsonify({
            "success": False,
            "message": "请提供发送地址或交易 hash"
        })
    
    try:
        result = verify_payment(tx_hash)
        
        # 记录日志
        log_access(
            ip_address=ip,
            endpoint="/api/verify",
            status="success" if result["success"] else "failed",
            message=result["message"]
        )
        
        return jsonify(result)
        
    except Exception as e:
        log_access(ip, "/api/verify", "error", str(e))
        return jsonify({"success": False, "message": f"服务器错误：{str(e)}"}), 500

@app.route("/api/status", methods=["GET"])
@limiter.limit("60 per minute")
def api_status():
    """API 状态检查"""
    return jsonify({
        "status": "ok",
        "payment_address": CONFIG["PAYMENT_ADDRESS"],
        "expected_amount": CONFIG["EXPECTED_AMOUNT"],
        "tolerance": CONFIG["TOLERANCE"],
        "time_window": CONFIG["TIME_WINDOW"],
        "min_amount": CONFIG["EXPECTED_AMOUNT"] - CONFIG["TOLERANCE"],
        "max_amount": CONFIG["EXPECTED_AMOUNT"] + CONFIG["TOLERANCE"],
        "database": "initialized" if os.path.exists(CONFIG["DB_PATH"]) else "not_initialized"
    })

@app.route("/api/transactions", methods=["GET"])
@limiter.limit("30 per minute")
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
        
        is_usdc = (token_symbol in ["USDC", "USD Coin"] or 
                   "USD Coin" in token_name or
                   token_symbol == "USDC.e")
        
        if is_usdc:
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

@app.route("/api/stats", methods=["GET"])
@limiter.limit("30 per minute")
def api_stats():
    """获取统计数据"""
    conn = sqlite3.connect(CONFIG["DB_PATH"])
    cursor = conn.cursor()
    
    # 总发放数量
    cursor.execute("SELECT COUNT(*) FROM api_keys WHERE is_active = 1")
    total_keys = cursor.fetchone()[0]
    
    # 今日发放数量
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("""
        SELECT COUNT(*) FROM api_keys 
        WHERE is_active = 1 AND DATE(created_at) = ?
    """, (today,))
    today_keys = cursor.fetchone()[0]
    
    # 总收入
    cursor.execute("SELECT SUM(amount) FROM api_keys WHERE is_active = 1")
    total_revenue = cursor.fetchone()[0] or 0
    
    # 最近 10 条记录
    cursor.execute("""
        SELECT api_key, tx_hash, amount, from_address, created_at 
        FROM api_keys 
        WHERE is_active = 1 
        ORDER BY created_at DESC 
        LIMIT 10
    """)
    recent_keys = cursor.fetchall()
    
    conn.close()
    
    return jsonify({
        "total_keys": total_keys,
        "today_keys": today_keys,
        "total_revenue": f"{total_revenue:.4f} USDC",
        "recent_keys": [
            {
                "api_key": row[0],
                "tx_hash": row[1],
                "amount": row[2],
                "from_address": row[3],
                "created_at": row[4]
            }
            for row in recent_keys
        ]
    })

# ============ 错误处理 ============
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not Found"}), 404

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({
        "error": "Rate Limit Exceeded",
        "message": "请求过于频繁，请稍后重试"
    }), 429

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal Server Error"}), 500

# ============ 主程序 ============
if __name__ == "__main__":
    print("=" * 60)
    print("x402 API 密钥自动发放服务（生产环境版）")
    print("=" * 60)
    print(f"收款地址：{CONFIG['PAYMENT_ADDRESS']}")
    print(f"期望金额：{CONFIG['EXPECTED_AMOUNT']} USDC")
    print(f"容差范围：±{CONFIG['TOLERANCE']} USDC ({CONFIG['EXPECTED_AMOUNT'] - CONFIG['TOLERANCE']} - {CONFIG['EXPECTED_AMOUNT'] + CONFIG['TOLERANCE']})")
    print(f"真实 API 地址：{CONFIG['REAL_API_URL']}")
    print(f"时间窗口：{CONFIG['TIME_WINDOW']} 秒")
    print(f"BaseScan API Key: {'已配置' if CONFIG['BASESCAN_API_KEY'] else '未配置（使用公开 API）'}")
    print("=" * 60)
    
    # 初始化数据库
    init_db()
    
    print("\n启动 Web 服务...")
    
    # 根据配置选择 HTTP 或 HTTPS
    if CONFIG["HTTPS_ENABLED"]:
        print("访问地址：https://localhost:4433")
        print("⚠️ HTTPS 已启用，请确保 SSL 证书文件存在")
        app.run(
            host="0.0.0.0",
            port=4433,
            ssl_context=(CONFIG["SSL_CERT"], CONFIG["SSL_KEY"]),
            debug=False
        )
    else:
        print("访问地址：http://8.213.149.224:8080")
        print("⚠️ 生产环境建议启用 HTTPS")
        app.run(host="0.0.0.0", port=8090, debug=False)
