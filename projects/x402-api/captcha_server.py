#!/usr/bin/env python3
# =============================================================================
# CAPTCHA 映射服务器 - 端口 7676
# Martin 可以通过浏览器访问并点击 CAPTCHA
# =============================================================================

from flask import Flask, render_template_string, jsonify, request
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
import time
import base64
import threading
import os

app = Flask(__name__)

# 全局状态
current_captcha = {
    "screenshot": None,
    "coordinates": [],
    "solved": False,
    "message": "等待 CAPTCHA..."
}

# HTML 模板
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CAPTCHA 验证 - 紫微智控</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #e0e0e0;
            padding: 20px;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }
        .container {
            max-width: 800px;
            width: 100%;
            text-align: center;
        }
        h1 {
            margin-bottom: 20px;
            color: #fff;
        }
        .status {
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .captcha-box {
            background: #fff;
            border-radius: 10px;
            overflow: hidden;
            margin-bottom: 20px;
            position: relative;
        }
        .captcha-box img {
            width: 100%;
            height: auto;
            display: block;
        }
        .click-overlay {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            cursor: crosshair;
        }
        .click-point {
            position: absolute;
            width: 20px;
            height: 20px;
            background: rgba(255, 0, 0, 0.7);
            border: 2px solid #fff;
            border-radius: 50%;
            transform: translate(-50%, -50%);
            pointer-events: none;
        }
        .instructions {
            background: rgba(0,255,0,0.1);
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            border: 1px solid #0f0;
        }
        .instructions.solved {
            background: rgba(0,255,0,0.2);
            border-color: #0f0;
        }
        .refresh-btn {
            background: #4CAF50;
            color: white;
            border: none;
            padding: 10px 30px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
        }
        .refresh-btn:hover {
            background: #45a049;
        }
        .auto-refresh {
            margin-top: 10px;
            font-size: 14px;
            color: #aaa;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔐 CAPTCHA 验证</h1>
        
        <div class="status">
            <h2 id="status-message">{{ message }}</h2>
        </div>
        
        {% if solved %}
        <div class="instructions solved">
            <h3>✅ CAPTCHA 已完成！</h3>
            <p>注册程序已继续，请稍候...</p>
            <p>下一个 CAPTCHA 出现时会自动刷新此页面。</p>
        </div>
        {% else %}
        <div class="instructions">
            <h3>📍 请点击 CAPTCHA 验证区域</h3>
            <p>点击正确的区域来完成验证</p>
            <p>点击后会自动提交给注册程序</p>
        </div>
        {% endif %}
        
        {% if screenshot %}
        <div class="captcha-box">
            <img src="data:image/png;base64,{{ screenshot }}" alt="CAPTCHA" id="captcha-img">
            <div class="click-overlay" id="overlay"></div>
        </div>
        
        <button class="refresh-btn" onclick="location.reload()">🔄 刷新</button>
        <div class="auto-refresh">页面将每 5 秒自动刷新</div>
        {% else %}
        <div class="captcha-box" style="padding: 100px; background: #333;">
            <p>等待 CAPTCHA 截图...</p>
            <p>注册程序正在运行</p>
        </div>
        
        <button class="refresh-btn" onclick="location.reload()">🔄 刷新</button>
        <div class="auto-refresh">页面将每 5 秒自动刷新</div>
        {% endif %}
    </div>
    
    <script>
        // 点击处理
        const overlay = document.getElementById('overlay');
        if (overlay) {
            overlay.addEventListener('click', function(e) {
                const rect = e.target.getBoundingClientRect();
                const x = Math.round((e.clientX - rect.left) / rect.width * 1000);
                const y = Math.round((e.clientY - rect.top) / rect.height * 1000);
                
                // 显示点击标记
                const point = document.createElement('div');
                point.className = 'click-point';
                point.style.left = e.clientX + 'px';
                point.style.top = e.clientY + 'px';
                document.body.appendChild(point);
                
                // 发送坐标到服务器
                fetch('/api/click', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ x, y })
                })
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        setTimeout(() => location.reload(), 1000);
                    }
                });
            });
        }
        
        // 自动刷新
        setTimeout(() => location.reload(), 5000);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """显示 CAPTCHA 页面"""
    return render_template_string(
        HTML_TEMPLATE,
        screenshot=current_captcha.get('screenshot'),
        message=current_captcha.get('message', '等待 CAPTCHA...'),
        solved=current_captcha.get('solved', False)
    )

@app.route('/api/click', methods=['POST'])
def handle_click():
    """处理点击"""
    data = request.json
    x = data.get('x', 0)
    y = data.get('y', 0)
    
    print(f"📍 收到点击坐标：({x}, {y})")
    
    # 保存坐标供注册脚本使用
    current_captcha['coordinates'].append((x, y))
    current_captcha['solved'] = True
    current_captcha['message'] = '✅ CAPTCHA 已提交！'
    
    return jsonify({'success': True, 'x': x, 'y': y})

@app.route('/api/status')
def status():
    """获取状态"""
    return jsonify(current_captcha)

@app.route('/api/reset', methods=['POST'])
def reset():
    """重置 CAPTCHA 状态"""
    current_captcha['screenshot'] = None
    current_captcha['coordinates'] = []
    current_captcha['solved'] = False
    current_captcha['message'] = '等待下一个 CAPTCHA...'
    return jsonify({'success': True})

def run_server():
    """运行 Flask 服务器"""
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║       CAPTCHA 映射服务器已启动                            ║")
    print("╠═══════════════════════════════════════════════════════════╣")
    print("║  访问地址：http://8.213.149.224:7676                     ║")
    print("║  Martin 可以在此页面点击 CAPTCHA                           ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    app.run(host='0.0.0.0', port=7676, debug=False, threaded=True)

if __name__ == '__main__':
    run_server()
