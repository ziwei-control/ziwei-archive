#!/usr/bin/env python3
"""
x402 API Dashboard - 登录验证页面

功能：
1. 用户登录（输入发送地址和交易 hash）
2. 验证是否发送过 USDC
3. 显示用户的 API Key 和统计信息

启动方式：
python3 x402_dashboard.py

访问：
http://8.213.149.224:8091
"""

from flask import Flask, render_template_string, jsonify, request
import sqlite3
import requests
import os
import hashlib
from datetime import datetime

app = Flask(__name__, static_folder='/home/admin/Ziwei/projects/x402-api')

# 配置
DB_PATH = "/home/admin/Ziwei/projects/x402-api/api_keys.db"
PAYMENT_ADDRESS = "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
BASESCAN_API = "https://api.basescan.org/api"

# 登录页面 HTML
LOGIN_HTML = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>x402 API - 用户登录</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .login-container {
            background: white;
            border-radius: 20px;
            padding: 50px;
            max-width: 500px;
            width: 100%;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        .logo {
            text-align: center;
            margin-bottom: 30px;
        }
        .logo h1 {
            font-size: 32px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 10px;
        }
        .logo p {
            color: #666;
            font-size: 14px;
        }
        .form-group {
            margin-bottom: 25px;
        }
        .form-label {
            display: block;
            font-size: 14px;
            font-weight: bold;
            color: #333;
            margin-bottom: 8px;
        }
        .form-input {
            width: 100%;
            padding: 15px;
            border: 2px solid #ddd;
            border-radius: 10px;
            font-size: 14px;
            font-family: 'Courier New', monospace;
            transition: all 0.3s;
        }
        .form-input:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        .form-hint {
            font-size: 12px;
            color: #999;
            margin-top: 5px;
        }
        .submit-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px;
            border-radius: 10px;
            font-size: 16px;
            font-weight: bold;
            width: 100%;
            cursor: pointer;
            transition: all 0.3s;
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        .submit-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(102, 126, 234, 0.5);
        }
        .submit-btn:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
        }
        .error-message {
            background: #ffebee;
            color: #c62828;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            border-left: 4px solid #f44336;
            display: none;
        }
        .info-box {
            background: #e3f2fd;
            color: #1976D2;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            border-left: 4px solid #2196F3;
            font-size: 13px;
            line-height: 1.6;
        }
        .footer {
            text-align: center;
            margin-top: 30px;
            color: #999;
            font-size: 13px;
        }
        .footer a {
            color: #667eea;
            text-decoration: none;
        }
        .loading {
            text-align: center;
            padding: 20px;
            display: none;
        }
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 15px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="logo">
            <h1>🔐 x402 API 登录</h1>
            <p>验证您的 USDC 支付并获取 API 访问权限</p>
        </div>
        
        <div class="info-box">
            <strong>💡 登录说明：</strong><br>
            1. 发送 0.03-0.07 USDC 到：0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb<br>
            2. 使用 Base 网络（ERC-20 USDC）<br>
            3. 输入您的发送地址和交易 hash<br>
            4. 系统将自动验证并显示您的 API Key
        </div>
        
        <div class="error-message" id="errorMessage"></div>
        
        <form id="loginForm" onsubmit="handleLogin(event)">
            <div class="form-group">
                <label class="form-label">📍 发送方地址（您的钱包地址）</label>
                <input 
                    type="text" 
                    class="form-input" 
                    id="fromAddress"
                    placeholder="0x..."
                    required
                />
                <div class="form-hint">
                    💡 发送 USDC 的钱包地址
                </div>
            </div>
            
            <div class="form-group">
                <label class="form-label">🔗 交易 Hash</label>
                <input 
                    type="text" 
                    class="form-input" 
                    id="txHash"
                    placeholder="0x..."
                    required
                />
                <div class="form-hint">
                    💡 USDC 转账的交易哈希
                </div>
            </div>
            
            <button type="submit" class="submit-btn" id="submitBtn">
                🔍 验证并登录
            </button>
            
            <div class="loading" id="loading">
                <div class="spinner"></div>
                <div id="loadingText">正在验证交易...</div>
            </div>
        </form>
        
        <div class="footer">
            <p>还没有获取 API Key？<a href="http://8.213.149.224:8090/get-api-key.html" target="_blank">立即获取</a></p>
            <p style="margin-top: 10px;">
                <a href="https://github.com/ziwei-control/ziwei-archive" target="_blank">GitHub</a> · 
                <a href="https://github.com/ziwei-control/ziwei-archive/issues" target="_blank">技术支持</a>
            </p>
        </div>
    </div>
    
    <script>
        async function handleLogin(event) {
            event.preventDefault();
            
            const fromAddress = document.getElementById('fromAddress').value.trim();
            const txHash = document.getElementById('txHash').value.trim();
            const submitBtn = document.getElementById('submitBtn');
            const loading = document.getElementById('loading');
            const errorMessage = document.getElementById('errorMessage');
            
            // 验证输入格式
            if (!fromAddress.startsWith('0x') || fromAddress.length !== 42) {
                showError('请输入有效的发送方地址（0x 开头，42 位字符）');
                return;
            }
            
            if (!txHash.startsWith('0x') || txHash.length !== 66) {
                showError('请输入有效的交易 hash（0x 开头，66 位字符）');
                return;
            }
            
            // 显示加载状态
            submitBtn.disabled = true;
            submitBtn.textContent = '验证中...';
            loading.style.display = 'block';
            errorMessage.style.display = 'none';
            
            try {
                const response = await fetch('/api/verify-login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        from_address: fromAddress,
                        tx_hash: txHash
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    // 验证成功，重定向到仪表板
                    localStorage.setItem('userAddress', fromAddress);
                    window.location.href = '/dashboard.html?address=' + fromAddress;
                } else {
                    showError(data.message || '验证失败，请检查输入');
                }
            } catch (error) {
                showError('网络错误，请稍后重试');
                console.error('登录失败:', error);
            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = '🔍 验证并登录';
                loading.style.display = 'none';
            }
        }
        
        function showError(message) {
            const errorMessage = document.getElementById('errorMessage');
            errorMessage.textContent = '❌ ' + message;
            errorMessage.style.display = 'block';
        }
    </script>
</body>
</html>
"""

# Dashboard 页面 HTML

# 管理员登录页面 HTML
ADMIN_LOGIN_HTML = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>x402 API - 管理员登录</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .login-box {
            background: white;
            border-radius: 20px;
            padding: 50px;
            max-width: 500px;
            width: 100%;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        h1 { text-align: center; color: #667eea; margin-bottom: 30px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; font-weight: bold; }
        input {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 14px;
        }
        button {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
        }
        .error { background: #ffebee; color: #c62828; padding: 15px; border-radius: 8px; margin-bottom: 20px; display: none; }
        .footer { text-align: center; margin-top: 20px; }
        .footer a { color: #667eea; }
    </style>
</head>
<body>
    <div class="login-box">
        <h1>🔐 管理员登录</h1>
        <div class="error" id="error"></div>
        <form onsubmit="return handleLogin(event)">
            <div class="form-group">
                <label>地址</label>
                <input type="text" id="addr" placeholder="0x..." required>
            </div>
            <div class="form-group">
                <label>密码</label>
                <input type="password" id="pwd" placeholder="••••••••" required>
            </div>
            <button type="submit">登录</button>
        </form>
        <div class="footer"><a href="/">← 返回用户登录</a></div>
    </div>
    <script>
        async function handleLogin(e) {
            e.preventDefault();
            const addr = document.getElementById('addr').value;
            const pwd = document.getElementById('pwd').value;
            try {
                const r = await fetch('/api/admin-login', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({address: addr, password: pwd})
                });
                const d = await r.json();
                if (d.success) {
                    alert('✅ 登录成功');
                    window.location.href = d.redirect || '/admin-dashboard.html';
                } else {
                    document.getElementById('error').textContent = '❌ ' + d.message;
                    document.getElementById('error').style.display = 'block';
                }
            } catch (err) {
                document.getElementById('error').textContent = '❌ 网络错误';
                document.getElementById('error').style.display = 'block';
            }
            return false;
        }
    </script>
</body>
</html>
"""

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>x402 API - 用户仪表板</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        .header {
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .header h1 {
            font-size: 28px;
            color: #333;
            margin-bottom: 10px;
        }
        .user-info {
            color: #666;
            font-size: 14px;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .stat-card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .stat-label {
            font-size: 14px;
            color: #666;
            margin-bottom: 10px;
        }
        .stat-value {
            font-size: 32px;
            font-weight: bold;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .credential-box {
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .credential-item {
            margin: 20px 0;
        }
        .credential-label {
            font-size: 13px;
            color: #666;
            margin-bottom: 8px;
            font-weight: bold;
        }
        .credential-value {
            font-family: 'Courier New', monospace;
            font-size: 16px;
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            border: 2px solid #667eea;
            word-break: break-all;
        }
        .copy-btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 8px 15px;
            border-radius: 5px;
            font-size: 13px;
            cursor: pointer;
            margin-top: 10px;
        }
        .logout-btn {
            background: #f44336;
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 10px;
            font-size: 14px;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>👤 用户仪表板</h1>
            <div class="user-info">
                地址：<span id="userAddress">-</span>
                <button class="logout-btn" onclick="logout()" style="float: right;">退出登录</button>
            </div>
        </div>
        
        <div class="credential-box">
            <h2>🔑 您的 API 凭证</h2>
            <div class="credential-item">
                <div class="credential-label">API_BASE_URL</div>
                <div class="credential-value" id="apiBaseUrl">-</div>
                <button class="copy-btn" onclick="copyToClipboard('apiBaseUrl')">📋 复制</button>
            </div>
            <div class="credential-item">
                <div class="credential-label">API_KEY</div>
                <div class="credential-value" id="apiKey">-</div>
                <button class="copy-btn" onclick="copyToClipboard('apiKey')">📋 复制</button>
            </div>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">💰 支付金额</div>
                <div class="stat-value" id="paidAmount">- USDC</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">📅 验证时间</div>
                <div class="stat-value" id="verifyTime" style="font-size: 18px;">-</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">✅ 状态</div>
                <div class="stat-value" id="status" style="font-size: 18px;">-</div>
            </div>
        </div>
    </div>
    
    <script>
        const urlParams = new URLSearchParams(window.location.search);
        const userAddress = urlParams.get('address') || localStorage.getItem('userAddress');
        
        if (!userAddress) {
            window.location.href = '/';
        }
        
        document.getElementById('userAddress').textContent = userAddress;
        
        async function loadUserData() {
            try {
                const response = await fetch('/api/user-data?address=' + userAddress);
                const data = await response.json();
                
                if (data.success && data.api_key) {
                    document.getElementById('apiBaseUrl').textContent = data.api_base_url || '8.213.149.224';
                    document.getElementById('apiKey').textContent = data.api_key;
                    document.getElementById('paidAmount').textContent = (data.amount || 0) + ' USDC';
                    document.getElementById('verifyTime').textContent = new Date(data.timestamp * 1000).toLocaleString('zh-CN');
                    document.getElementById('status').textContent = '✅ 已激活';
                } else {
                    alert('未找到您的 API Key 记录，请重新验证');
                    logout();
                }
            } catch (error) {
                console.error('加载数据失败:', error);
            }
        }
        
        function copyToClipboard(elementId) {
            const text = document.getElementById(elementId).textContent;
            navigator.clipboard.writeText(text).then(() => {
                alert('✅ 已复制到剪贴板');
            });
        }
        
        function logout() {
            localStorage.removeItem('userAddress');
            window.location.href = '/';
        }
        
        loadUserData();
    </script>
</body>
</html>
"""

def get_db_connection():
    """获取数据库连接"""
    if not os.path.exists(DB_PATH):
        return None
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def query_basescan(tx_hash):
    """查询 BaseScan 验证交易"""
    params = {
        "module": "proxy",
        "action": "eth_getTransactionByHash",
        "txhash": tx_hash
    }
    
    try:
        response = requests.get(BASESCAN_API, params=params, timeout=30)
        return response.json()
    except Exception as e:
        return {"status": "0", "message": str(e)}

@app.route("/")
def login():
    """用户登录页面"""
    return render_template_string(LOGIN_HTML)

@app.route("/admin")
def admin_login():
    """管理员登录页面"""
    return render_template_string(ADMIN_LOGIN_HTML)

@app.route("/api/admin-login", methods=["POST"])
def admin_verify():
    """管理员验证"""
    data = request.get_json() or {}
    address = data.get("address", "").strip()
    password = data.get("password", "").strip()
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "message": "数据库连接失败"})
    
    cursor = conn.cursor()
    cursor.execute("""
        SELECT password_hash, salt, is_active
        FROM admins
        WHERE address = ?
    """, (address,))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row or row[2] != 1:
        return jsonify({"success": False, "message": "管理员账户不存在"})
    
    # 验证密码
    password_hash = hashlib.sha256(f"{password}{row[1]}".encode()).hexdigest()
    if password_hash != row[0]:
        return jsonify({"success": False, "message": "密码错误"})
    
    return jsonify({
        "success": True,
        "message": "登录成功",
        "redirect": "/admin-dashboard.html"
    })

@app.route("/dashboard.html")
def dashboard():
    """用户仪表板"""
    return render_template_string(DASHBOARD_HTML)

@app.route("/api/verify-login", methods=["POST"])
def verify_login():
    """验证用户登录"""
    data = request.get_json() or {}
    from_address = data.get("from_address", "").strip().lower()
    tx_hash = data.get("tx_hash", "").strip().lower()
    
    # 1. 检查数据库是否已有记录
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT api_key, api_base_url, amount, timestamp, is_active
            FROM api_keys
            WHERE tx_hash = ? AND from_address = ?
        """, (tx_hash, from_address))
        
        row = cursor.fetchone()
        if row and row[4] == 1:  # is_active = 1
            conn.close()
            return jsonify({
                "success": True,
                "message": "验证成功",
                "api_key": row[0],
                "api_base_url": row[1],
                "amount": row[2],
                "timestamp": row[3]
            })
        conn.close()
    
    # 2. 查询 BaseScan 验证交易
    tx_data = query_basescan(tx_hash)
    
    if tx_data.get("status") != "1" or not tx_data.get("result"):
        return jsonify({
            "success": False,
            "message": "交易 hash 无效或不存在"
        })
    
    result = tx_data.get("result", {})
    
    # 3. 验证发送地址
    if result.get("from", "").lower() != from_address:
        return jsonify({
            "success": False,
            "message": "发送地址与交易不匹配"
        })
    
    # 4. 验证收款地址
    if result.get("to", "").lower() != PAYMENT_ADDRESS.lower():
        return jsonify({
            "success": False,
            "message": "该交易不是发送给我们的收款地址"
        })
    
    # 5. 检查是否是 USDC 交易（需要查询代币转账）
    token_tx_params = {
        "module": "account",
        "action": "tokentx",
        "address": from_address,
        "startblock": 0,
        "endblock": 99999999
    }
    
    token_txs = requests.get(BASECAN_API, params=token_tx_params, timeout=30).json()
    
    found_usdc = False
    amount = 0
    
    if token_txs.get("status") == "1":
        for tx in token_txs.get("result", []):
            if tx.get("hash", "").lower() == tx_hash:
                if "USDC" in tx.get("tokenSymbol", "") or "USD Coin" in tx.get("tokenName", ""):
                    found_usdc = True
                    decimal = int(tx.get("tokenDecimal", 6))
                    value = int(tx.get("value", 0))
                    amount = value / (10 ** decimal)
                    break
    
    if not found_usdc:
        return jsonify({
            "success": False,
            "message": "未找到 USDC 转账记录"
        })
    
    # 6. 验证金额范围
    if amount < 0.03 or amount > 0.07:
        return jsonify({
            "success": False,
            "message": f"金额不符合要求（需要 0.03-0.07 USDC，实际：{amount:.4f}）"
        })
    
    # 7. 生成 API Key
    timestamp = int(result.get("blockTimestamp", "0"), 16)
    salt = "x402_secret_salt_2026_production"
    hash_data = f"{tx_hash}{timestamp}{salt}"
    import hashlib
    hash_hex = hashlib.sha256(hash_data.encode()).hexdigest()[:16]
    api_key = f"x402_{hash_hex}_{timestamp:x}"
    
    # 8. 保存到数据库
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO api_keys
            (api_key, api_base_url, tx_hash, amount, from_address, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (api_key, "8.213.149.224", tx_hash, amount, from_address, timestamp))
        conn.commit()
        conn.close()
    
    return jsonify({
        "success": True,
        "message": "验证成功",
        "api_key": api_key,
        "api_base_url": "8.213.149.224",
        "amount": amount,
        "timestamp": timestamp
    })

@app.route("/api/user-data", methods=["GET"])
def get_user_data():
    """获取用户数据"""
    address = request.args.get("address", "").strip().lower()
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT api_key, api_base_url, amount, timestamp, is_active
            FROM api_keys
            WHERE from_address = ?
            ORDER BY created_at DESC
            LIMIT 1
        """, (address,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return jsonify({
                "success": True,
                "api_key": row[0],
                "api_base_url": row[1],
                "amount": row[2],
                "timestamp": row[3],
                "is_active": row[4]
            })
    
    return jsonify({
        "success": False,
        "message": "未找到记录"
    })

@app.route("/admin-dashboard.html")
def admin_dashboard():
    """管理员后台仪表板"""
    with open('/home/admin/Ziwei/projects/x402-api/admin-dashboard.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route("/api/admin-users")
def admin_users():
    """获取所有用户数据"""
    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "message": "数据库连接失败"})
    
    cursor = conn.cursor()
    cursor.execute("""
        SELECT api_key, api_base_url, tx_hash, from_address, amount, timestamp, is_active
        FROM api_keys
        ORDER BY timestamp DESC
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    users = []
    for row in rows:
        users.append({
            "api_key": row[0],
            "api_base_url": row[1],
            "tx_hash": row[2],
            "from_address": row[3],
            "amount": row[4],
            "timestamp": row[5],
            "is_active": row[6]
        })
    
    return jsonify({
        "success": True,
        "users": users,
        "total": len(users)
    })

if __name__ == "__main__":
    print("=" * 60)
    print("x402 API Dashboard - 用户登录验证")
    print("=" * 60)
    print(f"访问地址：http://8.213.149.224:8091")
    print(f"数据库：{DB_PATH}")
    print("=" * 60)
    
    app.run(host="0.0.0.0", port=8091, debug=False)
