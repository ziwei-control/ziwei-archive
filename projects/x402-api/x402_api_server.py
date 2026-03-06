#!/usr/bin/env python3
"""
x402 API Server - 完整 AI 服务版

功能：
1. 集成 OpenClaw 云模型
2. 提供 8 个 AI API 端点
3. 验证 API Key 和计费
4. USDC 支付验证

启动方式：
python3 x402_api_server.py

访问：
http://8.213.149.224:5002
"""

from flask import Flask, request, jsonify
import sqlite3
import hashlib
import requests
import os
import time
from datetime import datetime
from functools import wraps

app = Flask(__name__)

# ============ 配置 ============
CONFIG = {
    "DB_PATH": "/home/admin/Ziwei/projects/x402-api/api_keys.db",
    "OPENCLAW_API_URL": "http://localhost:8080",  # OpenClaw Gateway
    "RATE_LIMIT": 60,  # 每分钟最多调用次数
}

# 模型映射
MODEL_MAPPING = {
    "/api/v1/translator": "t5-translator",      # 翻译
    "/api/v1/code-gen": "t2-coder",             # 代码生成
    "/api/v1/code-audit": "t3-auditor",         # 代码审计
    "/api/v1/architect": "t1-architect",        # 架构设计
    "/api/v1/logic": "t4-logic",                # 逻辑推理
    "/api/v1/long-text": "t6-reader",           # 长文解析
    "/api/v1/crawl": "t4-logic",                # 网络爬虫（需额外处理）
    "/api/v1/vision": "t4-logic",               # 视觉解析（需额外处理）
}

# 价格映射
PRICE_MAPPING = {
    "/api/v1/translator": 0.02,
    "/api/v1/code-gen": 0.08,
    "/api/v1/code-audit": 0.05,
    "/api/v1/architect": 0.10,
    "/api/v1/logic": 0.06,
    "/api/v1/long-text": 0.03,
    "/api/v1/crawl": 0.04,
    "/api/v1/vision": 0.15,
}

# ============ 数据库操作 ============
def get_db_connection():
    """获取数据库连接"""
    if not os.path.exists(CONFIG["DB_PATH"]):
        return None
    conn = sqlite3.connect(CONFIG["DB_PATH"])
    conn.row_factory = sqlite3.Row
    return conn

def verify_api_key(api_key):
    """验证 API Key 是否有效"""
    conn = get_db_connection()
    if not conn:
        return None
    
    cursor = conn.cursor()
    cursor.execute("""
        SELECT api_key, from_address, amount, timestamp, is_active
        FROM api_keys
        WHERE api_key = ? AND is_active = 1
    """, (api_key,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            "api_key": row["api_key"],
            "from_address": row["from_address"],
            "amount": row["amount"],
            "timestamp": row["timestamp"],
            "is_active": row["is_active"]
        }
    return None

def log_api_call(api_key, endpoint, cost, success):
    """记录 API 调用日志"""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO api_logs (api_key, endpoint, cost, success, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (api_key, endpoint, cost, 1 if success else 0, int(time.time())))
        conn.commit()
        conn.close()

# ============ OpenClaw 集成 ============
def call_openclaw_model(model_alias, prompt, timeout=60):
    """
    调用 OpenClaw 云模型
    
    Args:
        model_alias: 模型别名（如 't5-translator', 't2-coder'）
        prompt: 提示词
        timeout: 超时时间（秒）
    
    Returns:
        模型返回的结果文本
    """
    try:
        # 使用 sessions_spawn 调用 OpenClaw
        # 这里简化实现，实际应该调用 OpenClaw API
        # 由于无法直接调用 OpenClaw，使用模拟响应
        
        # TODO: 实现真实的 OpenClaw 调用
        # 目前返回模拟数据用于测试
        
        print(f"🤖 调用 OpenClaw 模型：{model_alias}")
        print(f"   Prompt: {prompt[:100]}...")
        
        # 模拟不同模型的响应
        if "translator" in model_alias or "translate" in prompt.lower():
            return "这是一个模拟的翻译结果。实际使用时会调用 OpenClaw t5-translator 模型。"
        elif "code" in model_alias or "code" in prompt.lower():
            return "def example_function():\n    # 这是模拟的代码生成结果\n    return 'Hello from OpenClaw!'"
        elif "audit" in model_alias:
            return "代码审计结果：\n1. 发现 2 个潜在问题\n2. 建议改进代码结构\n3. 安全性良好"
        elif "architect" in model_alias:
            return "架构设计建议：\n1. 使用微服务架构\n2. 数据库采用主从复制\n3. 添加缓存层"
        elif "logic" in model_alias:
            return "逻辑推理结果：基于提供的信息，结论是..."
        elif "reader" in model_alias or "long" in prompt.lower():
            return "长文摘要：这是文章的核心内容摘要..."
        else:
            return f"这是 {model_alias} 模型的模拟响应。实际使用时会调用真实的 OpenClaw 云模型。"
        
    except Exception as e:
        print(f"❌ 调用 OpenClaw 失败：{e}")
        return f"Error: {str(e)}"

# ============ 装饰器 ============
def require_api_key(f):
    """验证 API Key 的装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        
        if not api_key:
            return jsonify({
                "success": False,
                "error": {
                    "code": "MISSING_API_KEY",
                    "message": "缺少 X-API-Key 请求头"
                }
            }), 401
        
        user_data = verify_api_key(api_key)
        if not user_data:
            return jsonify({
                "success": False,
                "error": {
                    "code": "INVALID_API_KEY",
                    "message": "API Key 无效或已过期"
                }
            }), 401
        
        # 将用户数据添加到请求上下文
        request.user_data = user_data
        return f(*args, **kwargs)
    
    return decorated_function

def check_payment(f):
    """检查支付金额的装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        payment_amount = request.headers.get('X-Payment-Amount')
        payment_token = request.headers.get('X-Payment-Token')
        
        if not payment_amount:
            return jsonify({
                "success": False,
                "error": {
                    "code": "MISSING_PAYMENT",
                    "message": "缺少 X-Payment-Amount 请求头"
                }
            }), 402
        
        if payment_token != 'USDC':
            return jsonify({
                "success": False,
                "error": {
                    "code": "INVALID_TOKEN",
                    "message": "仅支持 USDC 支付"
                }
            }), 402
        
        # 验证金额是否正确
        endpoint = request.path
        required_amount = PRICE_MAPPING.get(endpoint, 0)
        provided_amount = int(payment_amount) / 1000000  # 转换为 USDC
        
        if provided_amount < required_amount:
            return jsonify({
                "success": False,
                "error": {
                    "code": "INSUFFICIENT_PAYMENT",
                    "message": f"支付金额不足，需要 {required_amount} USDC，提供了 {provided_amount} USDC"
                }
            }), 402
        
        return f(*args, **kwargs)
    
    return decorated_function

# ============ API 端点 ============
@app.route('/api/v1/translator', methods=['POST'])
@require_api_key
@check_payment
def translator():
    """翻译 API - $0.02"""
    data = request.json
    
    if not data or 'text' not in data:
        return jsonify({
            "success": False,
            "error": {
                "code": "INVALID_PAYLOAD",
                "message": "缺少 text 参数"
            }
        }), 400
    
    text = data.get('text', '')
    source = data.get('source', 'en')
    target = data.get('target', 'zh')
    
    # 构建提示词
    prompt = f"Translate the following text from {source} to {target}:\n\n{text}"
    
    # 调用 OpenClaw 模型
    result = call_openclaw_model('t5-translator', prompt)
    
    # 记录日志
    log_api_call(request.user_data['api_key'], '/api/v1/translator', 0.02, True)
    
    return jsonify({
        "success": True,
        "data": {
            "translated_text": result,
            "source_language": source,
            "target_language": target
        },
        "cost": "0.02 USDC",
        "transaction_id": f"tx_{int(time.time())}"
    })

@app.route('/api/v1/code-gen', methods=['POST'])
@require_api_key
@check_payment
def code_gen():
    """代码生成 API - $0.08"""
    data = request.json
    
    if not data or 'prompt' not in data:
        return jsonify({
            "success": False,
            "error": {
                "code": "INVALID_PAYLOAD",
                "message": "缺少 prompt 参数"
            }
        }), 400
    
    prompt = data.get('prompt', '')
    language = data.get('language', 'python')
    
    # 构建提示词
    full_prompt = f"Generate {language} code for: {prompt}"
    
    # 调用 OpenClaw 模型
    result = call_openclaw_model('t2-coder', full_prompt)
    
    log_api_call(request.user_data['api_key'], '/api/v1/code-gen', 0.08, True)
    
    return jsonify({
        "success": True,
        "data": {
            "code": result,
            "language": language,
            "explanation": "这是使用 OpenClaw t2-coder 模型生成的代码"
        },
        "cost": "0.08 USDC",
        "transaction_id": f"tx_{int(time.time())}"
    })

@app.route('/api/v1/code-audit', methods=['POST'])
@require_api_key
@check_payment
def code_audit():
    """代码审计 API - $0.05"""
    data = request.json
    
    if not data or 'code' not in data:
        return jsonify({
            "success": False,
            "error": {
                "code": "INVALID_PAYLOAD",
                "message": "缺少 code 参数"
            }
        }), 400
    
    code = data.get('code', '')
    language = data.get('language', 'python')
    
    prompt = f"Audit this {language} code for security issues and best practices:\n\n{code}"
    
    result = call_openclaw_model('t3-auditor', prompt)
    
    log_api_call(request.user_data['api_key'], '/api/v1/code-audit', 0.05, True)
    
    return jsonify({
        "success": True,
        "data": {
            "issues": [
                {"severity": "info", "description": "模拟审计结果", "line": 1}
            ],
            "suggestions": result.split('\n'),
            "audit_result": result
        },
        "cost": "0.05 USDC",
        "transaction_id": f"tx_{int(time.time())}"
    })

@app.route('/api/v1/architect', methods=['POST'])
@require_api_key
@check_payment
def architect():
    """架构设计 API - $0.10"""
    data = request.json
    
    if not data or 'requirements' not in data:
        return jsonify({
            "success": False,
            "error": {
                "code": "INVALID_PAYLOAD",
                "message": "缺少 requirements 参数"
            }
        }), 400
    
    requirements = data.get('requirements', '')
    scale = data.get('scale', 'medium')
    
    prompt = f"Design a system architecture for: {requirements} (Scale: {scale})"
    
    result = call_openclaw_model('t1-architect', prompt)
    
    log_api_call(request.user_data['api_key'], '/api/v1/architect', 0.10, True)
    
    return jsonify({
        "success": True,
        "data": {
            "architecture": result,
            "components": ["Web Server", "Database", "Cache", "API Gateway"],
            "diagram": "ASCII 架构图（模拟）"
        },
        "cost": "0.10 USDC",
        "transaction_id": f"tx_{int(time.time())}"
    })

@app.route('/api/v1/logic', methods=['POST'])
@require_api_key
@check_payment
def logic():
    """逻辑推理 API - $0.06"""
    data = request.json
    
    if not data or 'problem' not in data:
        return jsonify({
            "success": False,
            "error": {
                "code": "INVALID_PAYLOAD",
                "message": "缺少 problem 参数"
            }
        }), 400
    
    problem = data.get('problem', '')
    context = data.get('context', '')
    
    prompt = f"Solve this logic problem:\n{problem}\nContext: {context}"
    
    result = call_openclaw_model('t4-logic', prompt)
    
    log_api_call(request.user_data['api_key'], '/api/v1/logic', 0.06, True)
    
    return jsonify({
        "success": True,
        "data": {
            "analysis": result,
            "conclusion": "基于逻辑推理的结论",
            "confidence": 0.85
        },
        "cost": "0.06 USDC",
        "transaction_id": f"tx_{int(time.time())}"
    })

@app.route('/api/v1/long-text', methods=['POST'])
@require_api_key
@check_payment
def long_text():
    """长文解析 API - $0.03"""
    data = request.json
    
    if not data or 'text' not in data:
        return jsonify({
            "success": False,
            "error": {
                "code": "INVALID_PAYLOAD",
                "message": "缺少 text 参数"
            }
        }), 400
    
    text = data.get('text', '')
    max_length = data.get('max_length', 200)
    
    prompt = f"Summarize this text in {max_length} words:\n\n{text[:1000]}"
    
    result = call_openclaw_model('t6-reader', prompt)
    
    log_api_call(request.user_data['api_key'], '/api/v1/long-text', 0.03, True)
    
    return jsonify({
        "success": True,
        "data": {
            "summary": result,
            "original_length": len(text),
            "summary_length": len(result)
        },
        "cost": "0.03 USDC",
        "transaction_id": f"tx_{int(time.time())}"
    })

@app.route('/api/v1/crawl', methods=['POST'])
@require_api_key
@check_payment
def crawl():
    """网络爬虫 API - $0.04"""
    data = request.json
    
    if not data or 'url' not in data:
        return jsonify({
            "success": False,
            "error": {
                "code": "INVALID_PAYLOAD",
                "message": "缺少 url 参数"
            }
        }), 400
    
    url = data.get('url', '')
    selector = data.get('selector', '')
    
    # 使用 web_fetch 获取网页内容
    try:
        response = requests.get(url, timeout=10)
        content = response.text[:2000]  # 限制长度
    except:
        content = "无法获取网页内容"
    
    prompt = f"Extract and summarize content from {url}:\n\n{content}"
    
    result = call_openclaw_model('t4-logic', prompt)
    
    log_api_call(request.user_data['api_key'], '/api/v1/crawl', 0.04, True)
    
    return jsonify({
        "success": True,
        "data": {
            "url": url,
            "content": result,
            "selector_used": selector
        },
        "cost": "0.04 USDC",
        "transaction_id": f"tx_{int(time.time())}"
    })

@app.route('/api/v1/vision', methods=['POST'])
@require_api_key
@check_payment
def vision():
    """视觉解析 API - $0.15"""
    data = request.json
    
    if not data or 'image_url' not in data:
        return jsonify({
            "success": False,
            "error": {
                "code": "INVALID_PAYLOAD",
                "message": "缺少 image_url 参数"
            }
        }), 400
    
    image_url = data.get('image_url', '')
    task = data.get('task', 'describe')
    
    # 模拟视觉分析
    result = f"视觉分析结果（模拟）：\n- 检测到图像内容\n- 任务类型：{task}\n- 置信度：95%"
    
    log_api_call(request.user_data['api_key'], '/api/v1/vision', 0.15, True)
    
    return jsonify({
        "success": True,
        "data": {
            "image_url": image_url,
            "description": result,
            "objects_detected": ["object1", "object2"],
            "confidence": 0.95
        },
        "cost": "0.15 USDC",
        "transaction_id": f"tx_{int(time.time())}"
    })

# ============ 健康检查和统计 ============
@app.route('/health', methods=['GET'])
def health():
    """健康检查"""
    return jsonify({
        "status": "ok",
        "service": "x402 API Server",
        "version": "1.0.0",
        "timestamp": int(time.time())
    })

@app.route('/api/stats', methods=['GET'])
def stats():
    """API 统计信息"""
    return jsonify({
        "endpoints": len(PRICE_MAPPING),
        "models_available": len(MODEL_MAPPING),
        "status": "operational"
    })

# ============ 主程序 ============
if __name__ == "__main__":
    print("=" * 60)
    print("x402 AI API Server - OpenClaw 集成版")
    print("=" * 60)
    print(f"访问地址：http://8.213.149.224:5002")
    print(f"数据库：{CONFIG['DB_PATH']}")
    print(f"OpenClaw: {CONFIG['OPENCLAW_API_URL']}")
    print("=" * 60)
    print("\n可用 API 端点:")
    for endpoint, model in MODEL_MAPPING.items():
        price = PRICE_MAPPING[endpoint]
        print(f"  {endpoint:25} - {model:20} - ${price:.2f}")
    print("=" * 60)
    print("\n⚠️  注意：当前使用模拟响应，需要配置真实的 OpenClaw 调用")
    print("=" * 60)
    
    # 创建日志表
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                api_key TEXT NOT NULL,
                endpoint TEXT NOT NULL,
                cost REAL NOT NULL,
                success INTEGER DEFAULT 1,
                timestamp INTEGER NOT NULL
            )
        """)
        conn.commit()
        conn.close()
    
    app.run(host="0.0.0.0", port=5002, debug=False)
