#!/usr/bin/env python3
# =============================================================================
# 紫微智控 - 系统监控 Dashboard v4.0.1 (融合版)
# v3.0 美观设计 + v4.0 实用功能 + 实时监控 = 完美融合
# =============================================================================

import http.server
import socketserver
import json
import os
import subprocess
import psutil
from datetime import datetime
from pathlib import Path
import urllib.request
import glob

# 配置
VERSION = "4.0.1"
PORT = 8081
Ziwei_DIR = Path("/home/admin/Ziwei")

# HTML 模板
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>紫微智控 Dashboard v{version}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #e0e0e0;
            padding: 20px;
            min-height: 100vh;
        }}
        .container {{ max-width: 1600px; margin: 0 auto; }}
        
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }}
        .header h1 {{
            font-size: 2em;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }}
        .header-info {{
            display: flex;
            justify-content: center;
            gap: 20px;
            flex-wrap: wrap;
        }}
        .badge {{
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.85em;
            background: rgba(102, 126, 234, 0.2);
            border: 1px solid rgba(102, 126, 234, 0.3);
        }}
        
        .terminal-section {{ margin-bottom: 30px; }}
        .terminal {{
            background: rgba(15, 15, 15, 0.95);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 12px;
            overflow: hidden;
            margin-bottom: 20px;
        }}
        .terminal-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 20px;
            background: rgba(255,255,255,0.05);
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }}
        .terminal-title {{ font-weight: 600; color: #667eea; }}
        .terminal-output {{
            padding: 15px;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 13px;
            max-height: 200px;
            overflow-y: auto;
            color: #b0b0b0;
            background: #0d0d0d;
        }}
        .terminal-output .success {{ color: #22c55e; }}
        .terminal-output .error {{ color: #ef4444; }}
        .terminal-output .warning {{ color: #f59e0b; }}
        .terminal-output .info {{ color: #3b82f6; }}
        .terminal-input {{
            display: flex;
            padding: 10px 15px;
            background: rgba(255,255,255,0.05);
            gap: 10px;
        }}
        .prompt {{ color: #22c55e; font-family: monospace; padding: 8px 0; }}
        .cmd-input {{
            flex: 1;
            background: rgba(0,0,0,0.5);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 6px;
            padding: 8px 12px;
            color: #e0e0e0;
            font-family: monospace;
            font-size: 13px;
            outline: none;
        }}
        .cmd-input:focus {{ border-color: #667eea; }}
        .cmd-btn {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 8px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 500;
            font-size: 13px;
            transition: transform 0.2s;
        }}
        .cmd-btn:hover {{ transform: translateY(-2px); }}
        
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .card {{
            background: rgba(30, 30, 30, 0.8);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 12px;
            padding: 20px;
            transition: transform 0.3s, box-shadow 0.3s;
        }}
        .card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.2);
        }}
        .card h2 {{
            font-size: 1.1em;
            color: #667eea;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid rgba(102, 126, 234, 0.3);
        }}
        
        .stat {{
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }}
        .stat:last-child {{ border-bottom: none; }}
        .stat-label {{ color: #888; }}
        .stat-value {{ color: #e0e0e0; font-weight: 600; }}
        
        .big-stat {{ text-align: center; margin-bottom: 15px; }}
        .big-stat-value {{
            font-size: 2.5em;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .big-stat-label {{ color: #666; font-size: 0.9em; margin-top: 5px; }}
        
        .badge-status {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: 500;
        }}
        .badge-status.success {{ background: rgba(34, 197, 94, 0.2); color: #22c55e; }}
        .badge-status.danger {{ background: rgba(239, 68, 68, 0.2); color: #ef4444; }}
        .badge-status.warning {{ background: rgba(245, 158, 11, 0.2); color: #f59e0b; }}
        
        .dot {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 6px;
        }}
        .dot.active {{ background: #22c55e; box-shadow: 0 0 10px #22c55e; }}
        .dot.inactive {{ background: #ef4444; }}
        
        table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
        td {{ padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.05); }}
        tr:last-child td {{ border-bottom: none; }}
        
        .progress {{
            background: rgba(255,255,255,0.1);
            height: 8px;
            border-radius: 4px;
            overflow: hidden;
            margin: 10px 0;
        }}
        .progress-fill {{
            background: linear-gradient(90deg, #667eea, #764ba2);
            height: 100%;
            transition: width 0.5s;
        }}
        
        .footer {{
            text-align: center;
            color: #666;
            font-size: 0.85em;
            padding: 20px;
            margin-top: 30px;
        }}
        
        .crypto-price {{ font-size: 1.2em; font-weight: bold; }}
        .crypto-up {{ color: #22c55e; }}
        .crypto-down {{ color: #ef4444; }}
        
        ::-webkit-scrollbar {{ width: 8px; }}
        ::-webkit-scrollbar-track {{ background: rgba(0,0,0,0.3); }}
        ::-webkit-scrollbar-thumb {{ background: rgba(102, 126, 234, 0.5); border-radius: 4px; }}
        ::-webkit-scrollbar-thumb:hover {{ background: rgba(102, 126, 234, 0.7); }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 紫微智控 Dashboard</h1>
            <div class="header-info">
                <span class="badge">v{version}</span>
                <span class="badge">📅 {update_time}</span>
                <span class="badge">🔄 自动刷新：1200 秒</span>
            </div>
        </div>
        
        <div class="terminal-section">
            <div class="terminal">
                <div class="terminal-header">
                    <span class="terminal-title">💻 命令行终端</span>
                    <button class="cmd-btn" onclick="toggleFullTerminal()">🖥️ 展开/收起</button>
                </div>
                <div class="terminal-output" id="cliOutput">
<span class="info"># 系统已就绪</span>
<span class="info"># 示例：supervisorctl status | ps aux | grep python</span>
</div>
                <div class="terminal-input">
                    <span class="prompt">$</span>
                    <input type="text" class="cmd-input" id="cliInput" placeholder="输入命令..." autocomplete="off">
                    <button class="cmd-btn" onclick="executeCommand()">执行</button>
                </div>
            </div>
            
            <div class="terminal" id="fullTerminalContainer" style="display:none;">
                <div class="terminal-header">
                    <span class="terminal-title">🖥️ 完整交互式终端 (支持 vim/openclaw tui/python3)</span>
                    <button class="cmd-btn" onclick="toggleFullTerminal()" style="background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);">❌ 关闭</button>
                </div>
                <div style="position:relative;width:100%;height:500px;background:#0d0d0d;">
                    <iframe id="ttydFrame" src="" style="position:absolute;width:100%;height:100%;border:none;"></iframe>
                </div>
            </div>
        </div>
        
        <div class="grid">
            {system_stats}
            {service_stats}
            {trading_stats}
        </div>
        
        <div class="grid">
            {security_stats}
            {income_stats}
            {api_stats}
        </div>
        
        <div class="grid">
            {crypto_stats}
            {warroom_stats}
        </div>
        
        <div class="grid">
            {project_progress}
            {code_mapping}
        </div>
        
        <div class="footer">
            紫微智控 Dashboard v{version} | 最后更新：{update_time} | 自动刷新：1200 秒 (20 分钟)
        </div>
    </div>
    
    <script>
        setTimeout(function() {{ location.reload(); }}, 1200000);
        
        var cliOutput = document.getElementById('cliOutput');
        var cliInput = document.getElementById('cliInput');
        
        function toggleFullTerminal() {{
            var container = document.getElementById('fullTerminalContainer');
            var iframe = document.getElementById('ttydFrame');
            if (container.style.display === 'none') {{
                container.style.display = 'block';
                if (!iframe.src) {{
                    var url = window.location.protocol + '//' + window.location.hostname + ':8082';
                    iframe.src = url;
                }}
            }} else {{
                container.style.display = 'none';
            }}
        }}
        
        cliInput.addEventListener('keypress', function(e) {{
            if (e.key === 'Enter') executeCommand();
        }});
        
        function executeCommand() {{
            var cmd = cliInput.value.trim();
            if (!cmd) return;
            
            appendOutput('<span class="info">$ ' + cmd + '</span>');
            cliInput.value = '';
            var loadingId = 'loading-' + Date.now();
            appendOutput('<span id="' + loadingId + '" class="warning">执行中...</span>');
            
            fetch('/api/execute', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{ command: cmd }})
            }})
            .then(function(r) {{ return r.json(); }})
            .then(function(data) {{
                var loadingEl = document.getElementById(loadingId);
                if (loadingEl) loadingEl.remove();
                if (data.success) {{
                    appendOutput(formatOutput(data.output || '✓ 完成'));
                }} else {{
                    appendOutput('<span class="error">✗ ' + data.error + '</span>');
                }}
                cliOutput.scrollTop = cliOutput.scrollHeight;
            }})
            .catch(function(err) {{
                var loadingEl = document.getElementById(loadingId);
                if (loadingEl) loadingEl.remove();
                appendOutput('<span class="error">✗ ' + err.message + '</span>');
            }});
        }}
        
        function appendOutput(html) {{
            cliOutput.innerHTML += html + '<br>';
        }}
        
        function formatOutput(out) {{
            out = out.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
            out = out.replace(/\\n/g, '<br>');
            out = out.replace(/✓|✅/g,'<span class="success">$&</span>');
            out = out.replace(/✗|❌|Error/g,'<span class="error">$&</span>');
            out = out.replace(/⚠️|Warning/g,'<span class="warning">$&</span>');
            return out;
        }}
    </script>
</body>
</html>
"""


def get_system_stats():
    """系统状态"""
    try:
        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        boot_time = datetime.fromtimestamp(psutil.boot_time()).strftime('%Y-%m-%d %H:%M')
        
        return f"""
        <div class="card">
            <h2>💻 系统状态</h2>
            <div class="big-stat">
                <div class="big-stat-value">{cpu}%</div>
                <div class="big-stat-label">CPU 使用率</div>
            </div>
            <div class="stat">
                <span class="stat-label">内存使用</span>
                <span class="stat-value">{mem.percent}%</span>
            </div>
            <div class="stat">
                <span class="stat-label">磁盘使用</span>
                <span class="stat-value">{disk.percent}%</span>
            </div>
            <div class="stat">
                <span class="stat-label">运行时间</span>
                <span class="stat-value">{boot_time}</span>
            </div>
        </div>
        """
    except Exception as e:
        return f'<div class="card"><h2>系统状态</h2><span class="error">{e}</span></div>'


def get_service_stats():
    """服务状态"""
    services = [
        ("x402 API", "app_production.py"),
        ("交易机器人", "start_test.py"),
        ("Dashboard", "dashboard"),
        ("全球战情室", "global-warroom"),
        ("自动同步", "auto-sync"),
    ]
    rows = ""
    for name, keyword in services:
        result = subprocess.run(['pgrep', '-f', keyword], capture_output=True, text=True)
        running = bool(result.stdout.strip())
        status = '<span class="badge-status success"><span class="dot active"></span>运行</span>' if running else '<span class="badge-status danger"><span class="dot inactive"></span>停止</span>'
        rows += f"<tr><td>{name}</td><td style='text-align:right'>{status}</td></tr>"
    return f"""
    <div class="card">
        <h2>🔧 服务状态</h2>
        <table>{rows}</table>
    </div>
    """


def get_trading_stats():
    """交易机器人统计 - 模拟交易"""
    try:
        result = subprocess.run(['pgrep', '-f', 'soul_trader|strategy_engine|intel_collector'], capture_output=True, text=True)
        pids = result.stdout.strip().split()
        running_count = len(pids)
        
        # 读取模拟资金配置
        env_file = Ziwei_DIR / "projects" / "x402-trading-bot" / ".env"
        sim_balance = 10000  # 默认$10,000
        if env_file.exists():
            with open(env_file) as f:
                for line in f:
                    if 'INITIAL_BALANCE=' in line:
                        sim_balance = float(line.split('=')[1].strip())
                        break
        
        return f"""
        <div class="card">
            <h2>📈 交易机器人 (模拟)</h2>
            <div class="stat">
                <span class="stat-label">运行实例</span>
                <span class="stat-value">{running_count}</span>
            </div>
            <div class="stat">
                <span class="stat-label">策略引擎</span>
                <span class="stat-value">{"✅ 运行中" if running_count > 1 else "❌ 未运行"}</span>
            </div>
            <div class="stat">
                <span class="stat-label">情报收集</span>
                <span class="stat-value">{"✅ 运行中" if running_count > 2 else "❌ 未运行"}</span>
            </div>
            <div style="margin-top:15px;padding:10px;background:rgba(245,158,11,0.1);border-radius:6px;border-left:3px solid #f59e0b;">
                <div class="stat">
                    <span class="stat-label">💡 模拟资金</span>
                    <span class="stat-value" style="color:#f59e0b;">${sim_balance:,.0f} USDT</span>
                </div>
                <div style="font-size:0.8em;color:#f59e0b;margin-top:5px;">
                    ⚠️ 模拟交易，不动用真实资金
                </div>
            </div>
        </div>
        """
    except Exception as e:
        return f'<div class="card"><h2>交易机器人</h2><span class="error">{e}</span></div>'


def get_security_stats():
    """安全监控"""
    try:
        attack_log = Ziwei_DIR / "data" / "security" / "attack_log.json"
        total = 0
        if attack_log.exists():
            with open(attack_log) as f:
                total = len(json.load(f))
        return f"""
        <div class="card">
            <h2>🛡️ 安全监控</h2>
            <div class="big-stat">
                <div class="big-stat-value">{total}</div>
                <div class="big-stat-label">攻击总数</div>
            </div>
            <div class="stat">
                <span class="stat-label">状态</span>
                <span class="badge-status success">✅ 防护中</span>
            </div>
        </div>
        """
    except:
        return '<div class="card"><h2>安全监控</h2><span class="stat-value">-</span></div>'


def get_income_stats():
    """收入统计 - 真实数据"""
    try:
        # x402 API 真实收入
        payments_file = Ziwei_DIR / "projects" / "x402-api" / "data" / "payments.json"
        api_income = 0
        api_count = 0
        if payments_file.exists():
            with open(payments_file) as f:
                data = json.load(f)
            payments = data.get("payments", {})
            api_income = sum(p.get("amount", 0) for p in payments.values() if p.get("verified"))
            api_count = len([p for p in payments.values() if p.get("verified")])
        
        # Binance 真实余额
        binance_balance = 0
        try:
            result = subprocess.run(
                ['python3', '/home/admin/Ziwei/scripts/check_binance_balance_real.py'],
                capture_output=True, text=True, timeout=10
            )
            for line in result.stdout.split('\n'):
                if '总估值' in line:
                    binance_balance = float(line.split('$')[1].split()[0])
                    break
        except:
            binance_balance = 0
        
        total_income = api_income + binance_balance
        
        return f"""
        <div class="card">
            <h2>💰 真实收入统计</h2>
            <div class="stat">
                <span class="stat-label">x402 API 收入</span>
                <span class="stat-value" style="color:#22c55e;">{api_income:.4f} USDC ✅</span>
            </div>
            <div class="stat">
                <span class="stat-label">Binance 余额</span>
                <span class="stat-value" style="color:#22c55e;">${binance_balance:.2f} USD ✅</span>
            </div>
            <div class="stat">
                <span class="stat-label">API 交易笔数</span>
                <span class="stat-value">{api_count}</span>
            </div>
            <div style="margin-top:15px;padding-top:15px;border-top:2px solid rgba(102,126,234,0.3);">
                <div class="stat">
                    <span class="stat-label" style="font-weight:600;">总计估值</span>
                    <span class="stat-value" style="font-size:1.3em;color:#667eea;">${total_income:.2f} USD</span>
                </div>
            </div>
            <div style="margin-top:10px;font-size:0.8em;color:#666;">
                💡 数据来自真实 API 和 Binance 钱包
            </div>
        </div>
        """
    except Exception as e:
        return f"""
        <div class="card">
            <h2>💰 收入统计</h2>
            <div class="stat">
                <span class="stat-label">数据加载中</span>
                <span class="stat-value">...</span>
            </div>
        </div>
        """


def get_api_stats():
    """API 统计"""
    try:
        req = urllib.request.urlopen("http://localhost:5002/health", timeout=2)
        health = json.loads(req.read().decode())
        today = health.get('requests_today', 0)
        return f"""
        <div class="card">
            <h2>⚡ x402 API</h2>
            <div class="big-stat">
                <div class="big-stat-value">{today:,}</div>
                <div class="big-stat-label">今日请求</div>
            </div>
            <div class="stat">
                <span class="stat-label">状态</span>
                <span class="badge-status success">运行中</span>
            </div>
        </div>
        """
    except:
        return """
        <div class="card">
            <h2>⚡ x402 API</h2>
            <div class="big-stat">
                <div class="big-stat-value">-</div>
                <div class="big-stat-label">离线</div>
            </div>
        </div>
        """


def get_crypto_stats():
    """加密货币实时价格 (从战情室数据)"""
    try:
        intel_dir = Ziwei_DIR / "data" / "intel"
        intel_files = sorted(intel_dir.glob("intel_*.json"), reverse=True)
        
        if not intel_files:
            return """
            <div class="card">
                <h2>💰 加密货币实时价格</h2>
                <p style="color:#666;">暂无数据</p>
            </div>
            """
        
        with open(intel_files[0]) as f:
            data = json.load(f)
        
        prices = data.get('prices', {})
        rows = ""
        for coin, info in list(prices.items())[:6]:
            price = info.get('price', 0)
            change = info.get('change_24h', 0)
            change_class = 'crypto-up' if change >= 0 else 'crypto-down'
            change_sign = '+' if change >= 0 else ''
            rows += f"""
            <div class="stat">
                <span class="stat-label">{coin}</span>
                <span class="crypto-price {change_class}">${price:,.2f} ({change_sign}{change:.2f}%)</span>
            </div>
            """
        
        update_time = data.get('timestamp', 'N/A')[11:19] if data.get('timestamp') else 'N/A'
        
        return f"""
        <div class="card">
            <h2>💰 加密货币实时价格</h2>
            {rows}
            <div style="margin-top:15px;padding-top:10px;border-top:1px solid rgba(255,255,255,0.1);font-size:0.8em;color:#666;">
                📅 最后更新：{update_time}
            </div>
        </div>
        """
    except Exception as e:
        return f'<div class="card"><h2>加密货币实时价格</h2><span class="error">{e}</span></div>'


def get_warroom_stats():
    """全球战情室最新情报"""
    try:
        intel_dir = Ziwei_DIR / "data" / "intel"
        intel_files = sorted(intel_dir.glob("intel_*.json"), reverse=True)
        
        if not intel_files:
            return """
            <div class="card">
                <h2>🌍 全球战情室</h2>
                <p style="color:#666;">暂无数据</p>
            </div>
            """
        
        with open(intel_files[0]) as f:
            data = json.load(f)
        
        news = data.get('news', {})
        news_items = []
        for coin, articles in news.items():
            if articles and len(articles) > 0:
                news_items.append(f"📰 {coin}: {articles[0].get('title', 'N/A')[:50]}...")
        
        if not news_items:
            news_items = ["📊 正在收集情报..."]
        
        rows = ""
        for item in news_items[:5]:
            rows += f"<div class='stat'><span class='stat-label'>{item}</span></div>"
        
        update_time = data.get('timestamp', 'N/A')[11:19] if data.get('timestamp') else 'N/A'
        
        return f"""
        <div class="card">
            <h2>🌍 全球战情室</h2>
            {rows}
            <div style="margin-top:15px;padding-top:10px;border-top:1px solid rgba(255,255,255,0.1);font-size:0.8em;color:#666;">
                📅 最后更新：{update_time}
            </div>
        </div>
        """
    except Exception as e:
        return f'<div class="card"><h2>全球战情室</h2><span class="error">{e}</span></div>'


def get_project_progress():
    """项目进度"""
    projects = [
        ("紫微智控", 90, "success"),
        ("x402 API", 100, "success"),
        ("交易机器人", 65, "warning"),
        ("全球战情室", 100, "success"),
        ("安全防护", 100, "success"),
    ]
    rows = ""
    for name, prog, status in projects:
        rows += f"""
        <div style="margin-bottom:15px">
            <div style="display:flex;justify-content:space-between;margin-bottom:5px">
                <span>{name}</span>
                <span class="badge-status {status}">{prog}%</span>
            </div>
            <div class="progress"><div class="progress-fill" style="width:{prog}%"></div></div>
        </div>
        """
    return f"""
    <div class="card">
        <h2>📊 项目进度</h2>
        {rows}
    </div>
    """


def get_code_mapping():
    """系统运行代码映射"""
    try:
        code_files = {
            "x402 API": "/home/admin/Ziwei/projects/x402-api/app_production.py",
            "Dashboard": "/home/admin/Ziwei/projects/dashboard_minimal.py",
            "交易机器人": "/home/admin/Ziwei/projects/x402-trading-bot/start_test.py",
            "全球战情室": "/home/admin/Ziwei/scripts/global-warroom-upgraded.py",
        }
        
        rows = ""
        for name, filepath in code_files.items():
            try:
                process_running = False
                for proc in psutil.process_iter(['cmdline']):
                    try:
                        cmdline = ' '.join(proc.info.get('cmdline', []))
                        if filepath in cmdline:
                            process_running = True
                            break
                    except:
                        pass
                
                status = '<span class="badge-status success">✅ 运行中</span>' if process_running else '<span class="badge-status warning">⚠️ 未运行</span>'
                rows += f"""
                <div style="margin-bottom:12px;padding:10px;background:rgba(255,255,255,0.05);border-radius:6px;">
                    <div style="display:flex;justify-content:space-between;margin-bottom:5px;">
                        <span style="font-weight:600;color:#667eea;">{name}</span>
                        {status}
                    </div>
                    <div style="font-size:0.8em;color:#666;font-family:monospace;">{filepath}</div>
                </div>
                """
            except:
                pass
        
        return f"""
        <div class="card">
            <h2>🔍 系统代码映射</h2>
            <p style="color:#666;font-size:0.85em;margin-bottom:15px;">实时显示系统实际运行的核心代码</p>
            {rows}
        </div>
        """
    except Exception as e:
        return f'<div class="card"><h2>系统代码映射</h2><span class="error">{e}</span></div>'


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        content = HTML_TEMPLATE.format(
            system_stats=get_system_stats(),
            service_stats=get_service_stats(),
            trading_stats=get_trading_stats(),
            security_stats=get_security_stats(),
            income_stats=get_income_stats(),
            api_stats=get_api_stats(),
            crypto_stats=get_crypto_stats(),
            warroom_stats=get_warroom_stats(),
            project_progress=get_project_progress(),
            code_mapping=get_code_mapping(),
            update_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            version=VERSION
        )
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        self.wfile.write(content.encode('utf-8'))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_POST(self):
        if self.path == '/api/execute':
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length).decode())
            cmd = data.get('command', '')
            
            if not cmd:
                self._json(400, {'success': False, 'error': '命令为空'})
                return
            
            try:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60, cwd='/home/admin/Ziwei')
                output = result.stdout + result.stderr
                self._json(200, {'success': True, 'output': output or '✓ 完成'})
            except subprocess.TimeoutExpired:
                self._json(500, {'success': False, 'error': '命令执行超时 (60 秒) - 交互式命令不支持'})
            except Exception as e:
                self._json(500, {'success': False, 'error': str(e)})
        else:
            self._json(404, {'success': False, 'error': '不存在'})
    
    def _json(self, code, data):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def log_message(self, *args): pass


if __name__ == '__main__':
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"🚀 Dashboard v{VERSION} 运行在 http://0.0.0.0:{PORT}")
        print(f"📍 公网访问：http://8.213.149.224:{PORT}")
        print(f"⏰ 自动刷新：1200 秒 (20 分钟)")
        httpd.serve_forever()
