#!/usr/bin/env python3
"""
x402 API Dashboard - 监控面板

功能：
1. 实时显示 API 密钥发放统计
2. 收入统计
3. 交易记录
4. 系统状态

启动方式：
python3 x402_dashboard.py

访问：
http://8.213.149.224:8091
"""

from flask import Flask, render_template_string, jsonify
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)

# 配置
DB_PATH = "/home/admin/Ziwei/projects/x402-api/api_keys.db"

# Dashboard HTML 模板
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>x402 API Dashboard - 监控面板</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        .header {
            text-align: center;
            color: white;
            padding: 30px 20px;
            margin-bottom: 30px;
        }
        .header h1 { font-size: 36px; margin-bottom: 10px; }
        .header p { font-size: 18px; opacity: 0.95; }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
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
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .stat-value {
            font-size: 36px;
            font-weight: bold;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .stat-sub {
            font-size: 13px;
            color: #999;
            margin-top: 5px;
        }
        
        .card {
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .card-title {
            font-size: 20px;
            font-weight: bold;
            color: #333;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #f0f0f0;
        }
        
        .table {
            width: 100%;
            border-collapse: collapse;
        }
        .table th {
            text-align: left;
            padding: 12px;
            background: #f8f9fa;
            color: #666;
            font-size: 13px;
            text-transform: uppercase;
        }
        .table td {
            padding: 12px;
            border-bottom: 1px solid #f0f0f0;
            font-size: 14px;
        }
        .table tr:hover {
            background: #f8f9fa;
        }
        .status-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
        }
        .status-active { background: #e8f5e9; color: #2e7d32; }
        .status-disabled { background: #ffebee; color: #c62828; }
        
        .refresh-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 10px;
            font-size: 14px;
            font-weight: bold;
            cursor: pointer;
            margin-bottom: 20px;
        }
        .refresh-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        .footer {
            text-align: center;
            color: white;
            padding: 30px;
            font-size: 14px;
            opacity: 0.9;
        }
        
        @media (max-width: 768px) {
            .stats-grid { grid-template-columns: 1fr; }
            .table { font-size: 12px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 x402 API Dashboard</h1>
            <p>实时监控面板 · 自动刷新</p>
        </div>
        
        <!-- 统计卡片 -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">🔑 总发放数量</div>
                <div class="stat-value" id="totalKeys">-</div>
                <div class="stat-sub">个 API Key</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">📈 今日发放</div>
                <div class="stat-value" id="todayKeys">-</div>
                <div class="stat-sub">个</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">💰 总收入</div>
                <div class="stat-value" id="totalRevenue">-</div>
                <div class="stat-sub">USDC</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">💵 平均金额</div>
                <div class="stat-value" id="avgAmount">-</div>
                <div class="stat-sub">USDC/笔</div>
            </div>
        </div>
        
        <!-- 最近记录 -->
        <div class="card">
            <div class="card-title">📋 最近 API 密钥发放记录</div>
            <button class="refresh-btn" onclick="loadData()">🔄 刷新数据</button>
            <table class="table">
                <thead>
                    <tr>
                        <th>时间</th>
                        <th>API Key</th>
                        <th>交易 Hash</th>
                        <th>金额 (USDC)</th>
                        <th>发送地址</th>
                        <th>状态</th>
                    </tr>
                </thead>
                <tbody id="recentRecords">
                    <tr><td colspan="6" style="text-align:center;color:#999;">加载中...</td></tr>
                </tbody>
            </table>
        </div>
        
        <div class="footer">
            <p>x402 API Dashboard v1.0</p>
            <p style="margin-top: 10px;">
                <a href="http://8.213.149.224:8090/get-api-key.html" style="color:white;text-decoration:underline;">获取 API 密钥</a> · 
                <a href="https://github.com/ziwei-control/ziwei-archive" style="color:white;text-decoration:underline;" target="_blank">GitHub</a>
            </p>
        </div>
    </div>
    
    <script>
        async function loadData() {
            try {
                const response = await fetch('/api/stats');
                const data = await response.json();
                
                // 更新统计
                document.getElementById('totalKeys').textContent = data.total_keys || 0;
                document.getElementById('todayKeys').textContent = data.today_keys || 0;
                document.getElementById('totalRevenue').textContent = (data.total_revenue || 0).replace(' USDC', '');
                document.getElementById('avgAmount').textContent = data.avg_amount || '0.00';
                
                // 更新表格
                const tbody = document.getElementById('recentRecords');
                if (data.recent_keys && data.recent_keys.length > 0) {
                    tbody.innerHTML = data.recent_keys.map(record => `
                        <tr>
                            <td>${new Date(record.created_at).toLocaleString('zh-CN')}</td>
                            <td style="font-family:monospace;font-size:12px;">${record.api_key}</td>
                            <td style="font-family:monospace;font-size:12px;">${record.tx_hash.substring(0, 20)}...</td>
                            <td>${record.amount.toFixed(4)}</td>
                            <td style="font-family:monospace;font-size:12px;">${record.from_address ? record.from_address.substring(0, 18) + '...' : '-'}</td>
                            <td><span class="status-badge status-${record.is_active ? 'active' : 'disabled'}">${record.is_active ? '✅ 激活' : '❌ 禁用'}</span></td>
                        </tr>
                    `).join('');
                } else {
                    tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;color:#999;">暂无记录</td></tr>';
                }
            } catch (error) {
                console.error('加载数据失败:', error);
            }
        }
        
        // 页面加载时获取数据
        loadData();
        
        // 每 30 秒自动刷新
        setInterval(loadData, 30000);
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

@app.route("/")
def dashboard():
    """Dashboard 首页"""
    return render_template_string(DASHBOARD_HTML)

@app.route("/api/stats")
def api_stats():
    """获取统计数据"""
    conn = get_db_connection()
    if not conn:
        return jsonify({
            "total_keys": 0,
            "today_keys": 0,
            "total_revenue": "0 USDC",
            "avg_amount": "0.00",
            "recent_keys": []
        })
    
    cursor = conn.cursor()
    
    # 总数量
    cursor.execute("SELECT COUNT(*) FROM api_keys WHERE is_active = 1")
    total_keys = cursor.fetchone()[0]
    
    # 今日数量
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("""
        SELECT COUNT(*) FROM api_keys 
        WHERE is_active = 1 AND DATE(created_at) = ?
    """, (today,))
    today_keys = cursor.fetchone()[0]
    
    # 总收入
    cursor.execute("SELECT SUM(amount) FROM api_keys WHERE is_active = 1")
    total_revenue = cursor.fetchone()[0] or 0
    
    # 平均金额
    cursor.execute("SELECT AVG(amount) FROM api_keys WHERE is_active = 1")
    avg_amount = cursor.fetchone()[0] or 0
    
    # 最近 10 条记录
    cursor.execute("""
        SELECT api_key, tx_hash, amount, from_address, created_at, is_active
        FROM api_keys
        WHERE is_active = 1
        ORDER BY created_at DESC
        LIMIT 10
    """)
    recent_keys = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return jsonify({
        "total_keys": total_keys,
        "today_keys": today_keys,
        "total_revenue": f"{total_revenue:.4f} USDC",
        "avg_amount": f"{avg_amount:.4f}",
        "recent_keys": recent_keys
    })

if __name__ == "__main__":
    print("=" * 60)
    print("x402 API Dashboard - 监控面板")
    print("=" * 60)
    print(f"访问地址：http://8.213.149.224:8091")
    print(f"数据库：{DB_PATH}")
    print("=" * 60)
    
    app.run(host="0.0.0.0", port=8091, debug=False)
