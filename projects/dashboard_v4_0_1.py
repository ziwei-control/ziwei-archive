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
VERSION = "4.0.3"
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
    <!-- 禁止浏览器缓存 -->
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">
    <meta name="version" content="{version}">
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
            <h1>🚀 紫微智控 Dashboard <span style="font-size:0.5em;background:#667eea;color:white;padding:5px 15px;border-radius:20px;margin-left:10px;">v{version}</span></h1>
            <div class="header-info">
                <span class="badge">📅 {update_time}</span>
                <span class="badge">🔄 自动刷新：1200 秒</span>
                <span class="badge" style="cursor:pointer;" onclick="forceRefresh()" title="清除缓存并刷新">🧹 强制刷新</span>
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
            {trading_signals}
        </div>
        
        <div class="grid">
            {crypto_stats}
            {warroom_stats}
        </div>
        
        <div class="grid">
            {project_progress}
            {code_mapping}
        </div>
        
        <div class="grid" style="grid-template-columns:1fr;">
            {status_report}
        </div>
        
        <div class="grid" style="grid-template-columns:1fr;">
            {promotion_stats}
        </div>
        
        <div class="footer">
            紫微智控 Dashboard v{version} | 最后更新：{update_time} | 自动刷新：1200 秒 (20 分钟)
        </div>
    </div>
    
    <script>
        // 自动刷新（1200 秒 = 20 分钟）
        setTimeout(function() {{ location.reload(); }}, 1200000);
        
        // 强制刷新函数 - 清除缓存并重新加载
        function forceRefresh() {{
            // 添加时间戳参数，强制浏览器重新请求
            var timestamp = new Date().getTime();
            var url = window.location.href.split('?')[0] + '?v=' + timestamp;
            window.location.href = url;
        }}
        
        // 页面加载时显示版本信息
        window.addEventListener('load', function() {{
            console.log('Dashboard 版本：{version}');
            console.log('加载时间：' + new Date().toISOString());
            console.log('缓存策略：no-cache, no-store');
        }});
        
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
            out = out.replace(new RegExp('\\n', 'g'), '<br>');
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
    """交易机器人统计 - 模拟交易（详细真实数据）"""
    try:
        # 获取进程详细信息
        processes = []
        process_names = {
            'soul_trader': '🧠 主交易员',
            'strategy_engine_v3': '📊 策略引擎 v3',
            'intel_collector': '📡 情报收集器',
            'start_test': '🚀 启动器'
        }
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time', 'memory_percent']):
            try:
                cmdline = ' '.join(proc.info.get('cmdline', []))
                for key, name in process_names.items():
                    if key in cmdline:
                        uptime = datetime.now() - datetime.fromtimestamp(proc.info.get('create_time', 0))
                        processes.append({
                            'name': name,
                            'pid': proc.info.get('pid', 0),
                            'uptime': str(uptime).split('.')[0],
                            'memory': f"{proc.info.get('memory_percent', 0):.1f}%"
                        })
            except:
                pass
        
        # 读取配置文件
        env_file = Ziwei_DIR / "projects" / "x402-trading-bot" / ".env"
        config = {}
        if env_file.exists():
            with open(env_file) as f:
                for line in f:
                    if '=' in line and not line.strip().startswith('#'):
                        key, value = line.strip().split('=', 1)
                        config[key] = value.split('#')[0].strip()
        
        sim_balance = float(config.get('INITIAL_BALANCE', 10000))
        test_mode = config.get('TEST_MODE', 'true')
        trading_pairs = config.get('TRADING_PAIRS', 'VIRTUAL/USDT,PAYAI/USDT,PING/USDT')
        stop_loss = float(config.get('STOP_LOSS', -0.10)) * 100
        take_profit = float(config.get('TAKE_PROFIT', 0.05)) * 100
        
        # 策略详情
        strategy_details = f"""
        <div style="margin-top:15px;padding:10px;background:rgba(102,126,234,0.05);border-radius:6px;font-size:0.85em;">
            <div style="font-weight:600;color:#667eea;margin-bottom:8px;">📊 策略配置</div>
            <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:8px;">
                <div>• 技术指标：RSI(14), MACD(12,26,9), 均线 (MA20/50/200)</div>
                <div>• 动量指标：KDJ, BOLL, EMA</div>
                <div>• 情绪分析：新闻情感 (-5~5 分)</div>
                <div>• 链上数据：大额转账，持仓变化</div>
                <div>• 止损：{stop_loss:.0f}%</div>
                <div>• 止盈：+{take_profit:.0f}%</div>
            </div>
        </div>
        
        <div style="margin-top:10px;padding:10px;background:rgba(34,197,94,0.05);border-radius:6px;font-size:0.85em;">
            <div style="font-weight:600;color:#22c55e;margin-bottom:8px;">📡 情报收集</div>
            <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:8px;">
                <div>• 新闻源：Google News, CoinDesk, CoinTelegraph</div>
                <div>• 监控币种：Top 100 (BTC, ETH, SOL...)</div>
                <div>• 社交媒体：Twitter, Reddit 关键词</div>
                <div>• 价格数据：CoinGecko API 实时</div>
            </div>
        </div>
        """
        
        # 进程列表
        process_rows = ""
        for proc in processes:
            process_rows += f"""
            <div style="padding:6px;margin:4px 0;background:rgba(255,255,255,0.03);border-radius:4px;font-size:0.85em;display:flex;justify-content:space-between;">
                <span>{proc['name']}</span>
                <span style="color:#666;">PID:{proc['pid']} | 运行:{proc['uptime']} | 内存:{proc['memory']}</span>
            </div>
            """
        
        return f"""
        <div class="card" style="grid-column:span 2;">
            <h2>📈 交易机器人 (模拟)</h2>
            
            <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:15px;margin-bottom:15px;">
                <div style="text-align:center;padding:15px;background:rgba(102,126,234,0.1);border-radius:8px;">
                    <div style="font-size:1.8em;font-weight:700;color:#667eea;">{len(processes)}</div>
                    <div style="font-size:0.85em;color:#888;">运行实例</div>
                </div>
                <div style="text-align:center;padding:15px;background:rgba(34,197,94,0.1);border-radius:8px;">
                    <div style="font-size:1.8em;font-weight:700;color:#22c55e;">${sim_balance:,.0f}</div>
                    <div style="font-size:0.85em;color:#888;">模拟资金 (USDT)</div>
                </div>
                <div style="text-align:center;padding:15px;background:rgba(245,158,11,0.1);border-radius:8px;">
                    <div style="font-size:1.8em;font-weight:700;color:#f59e0b;">{test_mode}</div>
                    <div style="font-size:0.85em;color:#888;">测试模式</div>
                </div>
                <div style="text-align:center;padding:15px;background:rgba(139,92,246,0.1);border-radius:8px;">
                    <div style="font-size:1.8em;font-weight:700;color:#8b5cf6;">{trading_pairs.split(',')[0]}</div>
                    <div style="font-size:0.85em;color:#888;">主交易对</div>
                </div>
            </div>
            
            <div style="margin-bottom:15px;">
                <div style="font-weight:600;color:#667eea;margin-bottom:8px;">🖥️ 运行进程</div>
                {process_rows}
            </div>
            
            {strategy_details}
            
            <div style="margin-top:15px;padding:10px;background:rgba(239,68,68,0.1);border-radius:6px;border-left:3px solid #ef4444;">
                <div style="font-size:0.85em;color:#ef4444;">
                    ⚠️ <b>警告：</b>模拟交易，不动用真实资金！所有交易仅为测试和策略验证。
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
    """收入统计 - 真实数据（详细交易记录）"""
    try:
        # x402 API 真实收入
        payments_file = Ziwei_DIR / "projects" / "x402-api" / "data" / "payments.json"
        api_income = 0
        payments = {}
        if payments_file.exists():
            with open(payments_file) as f:
                data = json.load(f)
            payments = data.get("payments", {})
            api_income = sum(p.get("amount", 0) for p in payments.values() if p.get("verified"))
        
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
        
        # 收款钱包信息
        payment_wallet = "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
        network = "Base L2"
        
        # 交易记录详情
        tx_rows = ""
        sorted_payments = sorted(payments.values(), key=lambda x: x.get('timestamp', ''), reverse=True)
        
        for tx in sorted_payments[:10]:  # 显示最近 10 笔
            tx_hash = tx.get('tx_hash', 'N/A')
            amount = tx.get('amount', 0)
            sender = tx.get('sender', 'N/A')
            timestamp = tx.get('timestamp', 'N/A')[:19].replace('T', ' ')
            
            # Base 链浏览器链接
            tx_link = f"https://basescan.org/tx/{tx_hash}"
            
            tx_rows += f"""
            <div style="padding:8px;margin:4px 0;background:rgba(255,255,255,0.03);border-radius:6px;font-size:0.82em;">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
                    <span style="font-weight:600;color:#22c55e;">+{amount:.2f} USDC</span>
                    <span style="color:#666;font-size:0.9em;">{timestamp}</span>
                </div>
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <span style="color:#888;font-size:0.9em;">From: {sender[:10]}...{sender[-8:]}</span>
                    <a href="{tx_link}" target="_blank" style="color:#667eea;text-decoration:none;">🔗 查看交易 →</a>
                </div>
            </div>
            """
        
        if not tx_rows:
            tx_rows = '<div style="padding:20px;text-align:center;color:#666;">暂无交易记录</div>'
        
        # 判断是否为测试数据（假地址）
        test_tx_count = sum(1 for p in payments.values() if '0x0000' in p.get('tx_hash', '') or 'aaaa' in p.get('tx_hash', '') or 'bbbb' in p.get('tx_hash', ''))
        is_test_data = test_tx_count > 0 and test_tx_count == len(payments)
        income_label = "测试收入" if is_test_data and api_income > 0 else "x402 API 收入"
        income_note = "⚠️ 测试数据" if is_test_data and api_income > 0 else "✅ 真实收入"
        income_color = "#f59e0b" if is_test_data and api_income > 0 else "#22c55e"
        
        return f"""
        <div class="card" style="grid-column:span 2;">
            <h2>💰 收入统计</h2>
            
            <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:15px;margin-bottom:15px;">
                <div style="text-align:center;padding:15px;background:rgba(34,197,94,0.1);border-radius:8px;">
                    <div style="font-size:1.8em;font-weight:700;color:{income_color};">{api_income:.4f} USDC</div>
                    <div style="font-size:0.85em;color:#888;">{income_label}</div>
                    <div style="font-size:0.75em;color:{income_color};margin-top:5px;">{income_note}</div>
                </div>
                <div style="text-align:center;padding:15px;background:rgba(102,126,234,0.1);border-radius:8px;">
                    <div style="font-size:1.8em;font-weight:700;color:#667eea;">${binance_balance:.2f}</div>
                    <div style="font-size:0.85em;color:#888;">Binance 余额</div>
                </div>
                <div style="text-align:center;padding:15px;background:rgba(139,92,246,0.1);border-radius:8px;">
                    <div style="font-size:1.8em;font-weight:700;color:#8b5cf6;">${total_income:.2f}</div>
                    <div style="font-size:0.85em;color:#888;">总计估值 (USD)</div>
                </div>
            </div>
            
            <div style="padding:12px;margin-bottom:15px;background:rgba(102,126,234,0.05);border-radius:8px;">
                <div style="font-weight:600;color:#667eea;margin-bottom:8px;">💳 收款信息</div>
                <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:10px;font-size:0.9em;">
                    <div>
                        <span style="color:#888;">钱包地址：</span>
                        <span style="color:#e0e0e0;font-family:monospace;">{payment_wallet[:20]}...{payment_wallet[-18:]}</span>
                    </div>
                    <div>
                        <span style="color:#888;">网络：</span>
                        <span style="color:#e0e0e0;">{network}</span>
                    </div>
                    <div style="grid-column:span 2;">
                        <span style="color:#888;">区块浏览器：</span>
                        <a href="https://basescan.org/address/{payment_wallet}" target="_blank" style="color:#667eea;text-decoration:none;">🔗 basescan.org/address/{payment_wallet[:10]}... →</a>
                    </div>
                </div>
            </div>
            
            <div style="margin-bottom:15px;">
                <div style="font-weight:600;color:#667eea;margin-bottom:8px;display:flex;justify-content:space-between;align-items:center;">
                    <span>📋 交易记录（最近 {len(sorted_payments)} 笔）</span>
                    <span style="font-size:0.85em;color:#888;">共 {len(payments)} 笔</span>
                </div>
                {tx_rows}
            </div>
            
            <div style="margin-top:15px;padding:10px;background:rgba(34,197,94,0.05);border-radius:6px;font-size:0.85em;">
                <div style="color:{income_color};">
                    {'⚠️ 当前为测试数据 - 需要接入真实支付' if is_test_data and api_income > 0 else '✅ 所有收入均为真实 USDC，通过 x402 协议在 Base 链上结算'}
                </div>
            </div>
        </div>
        """
    except Exception as e:
        return f'<div class="card"><h2>💰 收入统计</h2><span class="error">{e}</span></div>'


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


def get_trading_signals():
    """交易机器人 - 实时信号分析"""
    try:
        strategy_dir = Ziwei_DIR / "data" / "strategy"
        signal_files = sorted(strategy_dir.glob("signals_*.json"), reverse=True)
        
        if not signal_files:
            return """
            <div class="card">
                <h2>🤖 交易信号分析</h2>
                <p style="color:#666;">暂无信号数据</p>
            </div>
            """
        
        with open(signal_files[0]) as f:
            signals = json.load(f)
        
        # 获取账户状态
        account_file = strategy_dir / "account_status.json"
        account = {}
        if account_file.exists():
            with open(account_file) as f:
                account = json.load(f)
        
        balance = account.get('balance', 10000)
        total_trades = account.get('total_trades', 0)
        
        # 信号分类
        strong_buy = [s for s in signals if s.get('signal') == 'STRONG_BUY']
        buy = [s for s in signals if s.get('signal') == 'BUY']
        weak_buy = [s for s in signals if s.get('signal') == 'WEAK_BUY']
        hold = [s for s in signals if s.get('signal') == 'HOLD']
        sell = [s for s in signals if s.get('signal') in ['SELL', 'WEAK_SELL', 'STRONG_SELL']]
        
        # 生成信号行
        rows = ""
        for signal in signals[:7]:  # 最多显示 7 个
            symbol = signal.get('symbol', '')
            sig = signal.get('signal', 'HOLD')
            score = signal.get('score', 0)
            price = signal.get('price', 0)
            change = signal.get('change_24h', 0)
            
            # 信号颜色
            if 'STRONG_BUY' in sig:
                sig_color = '#22c55e'  # 绿色
                sig_bg = 'rgba(34, 197, 94, 0.2)'
            elif 'BUY' in sig:
                sig_color = '#84cc16'
                sig_bg = 'rgba(132, 204, 22, 0.2)'
            elif 'SELL' in sig:
                sig_color = '#ef4444'
                sig_bg = 'rgba(239, 68, 68, 0.2)'
            else:
                sig_color = '#6b7280'
                sig_bg = 'rgba(107, 116, 128, 0.2)'
            
            # 分数颜色
            if score >= 15:
                score_color = '#22c55e'
            elif score >= 5:
                score_color = '#f59e0b'
            elif score <= -5:
                score_color = '#ef4444'
            else:
                score_color = '#6b7280'
            
            change_sign = '+' if change >= 0 else ''
            change_class = 'crypto-up' if change >= 0 else 'crypto-down'
            
            rows += f"""
            <div class="stat" style="align-items:center;">
                <div style="flex:1;">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:5px;">
                        <span class="stat-label" style="font-weight:600;color:#e0e0e0;">{symbol}</span>
                        <span style="background:{sig_bg};color:{sig_color};padding:2px 8px;border-radius:4px;font-size:0.75em;font-weight:600;">{sig}</span>
                    </div>
                    <div style="display:flex;justify-content:space-between;font-size:0.85em;">
                        <span style="color:#888;">${price:,.2f} <span class="{change_class}">({change_sign}{change:.2f}%)</span></span>
                        <span style="color:{score_color};font-weight:600;">分数：{score}</span>
                    </div>
                </div>
            </div>
            """
        
        # 信号统计
        signal_summary = f"""
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:15px;">
            <div style="background:rgba(34,197,94,0.1);border:1px solid rgba(34,197,94,0.3);border-radius:8px;padding:10px;text-align:center;">
                <div style="color:#22c55e;font-size:1.5em;font-weight:700;">{len(strong_buy)}</div>
                <div style="color:#888;font-size:0.75em;">强买</div>
            </div>
            <div style="background:rgba(132,204,22,0.1);border:1px solid rgba(132,204,22,0.3);border-radius:8px;padding:10px;text-align:center;">
                <div style="color:#84cc16;font-size:1.5em;font-weight:700;">{len(buy)}</div>
                <div style="color:#888;font-size:0.75em;">买入</div>
            </div>
            <div style="background:rgba(107,116,128,0.1);border:1px solid rgba(107,116,128,0.3);border-radius:8px;padding:10px;text-align:center;">
                <div style="color:#9ca3af;font-size:1.5em;font-weight:700;">{len(hold)}</div>
                <div style="color:#888;font-size:0.75em;">观望</div>
            </div>
        </div>
        """
        
        update_time = signal_files[0].stem.replace('signals_', '').replace('_', ':')[-8:] if signal_files else 'N/A'
        
        return f"""
        <div class="card" style="grid-column:span 2;">
            <h2>🤖 交易信号分析</h2>
            {signal_summary}
            <div style="margin-bottom:15px;padding:10px;background:rgba(255,255,255,0.05);border-radius:8px;">
                <div style="display:flex;justify-content:space-between;margin-bottom:5px;">
                    <span style="color:#888;">账户余额</span>
                    <span style="color:#e0e0e0;font-weight:600;">${balance:,.2f} USDC</span>
                </div>
                <div style="display:flex;justify-content:space-between;">
                    <span style="color:#888;">总交易数</span>
                    <span style="color:#e0e0e0;font-weight:600;">{total_trades}</span>
                </div>
            </div>
            {rows}
            <div style="margin-top:15px;padding-top:10px;border-top:1px solid rgba(255,255,255,0.1);font-size:0.8em;color:#666;">
                📅 最后更新：{update_time} | 策略引擎 v3.0
            </div>
        </div>
        """
    except Exception as e:
        return f'<div class="card" style="grid-column:span 2;"><h2>🤖 交易信号分析</h2><span class="error">{e}</span></div>'


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
    """全球战情室 - 实时新闻 + 市场情绪（每 60 秒更新）"""
    try:
        # 读取最新情报（实时数据，60 秒更新）
        intel_dir = Ziwei_DIR / "data" / "intel"
        intel_files = sorted(intel_dir.glob("intel_*.json"), reverse=True)
        
        if not intel_files:
            return """
            <div class="card" style="grid-column:span 2;">
                <h2>🌍 全球战情室</h2>
                <p style="color:#666;">暂无情报数据</p>
            </div>
            """
        
        with open(intel_files[0]) as f:
            intel = json.load(f)
        
        report_time = intel.get('timestamp', 'N/A')[11:19] if intel.get('timestamp') else 'N/A'
        
        # 获取新闻数据
        news = intel.get('news', {})
        total_news = sum(len(articles) for articles in news.values())
        
        # 获取情绪数据
        sentiment = intel.get('sentiment', {})
        
        # 获取价格数据
        prices = intel.get('prices', {})
        
        # 显示各币种新闻和情绪
        rows = ""
        for coin in ['BTC', 'ETH', 'SOL', 'BNB', 'XRP', 'DOGE']:
            coin_news = news.get(coin, [])[:3]  # 最新 3 条新闻
            coin_sentiment = sentiment.get(coin, {})
            coin_price = prices.get(coin, {})
            
            sentiment_label = coin_sentiment.get('label', 'neutral')
            sentiment_score = coin_sentiment.get('score', 0)
            
            # 情绪颜色
            if sentiment_label == 'bullish':
                sent_color = '#22c55e'
                sent_icon = '📈'
            elif sentiment_label == 'bearish':
                sent_color = '#ef4444'
                sent_icon = '📉'
            else:
                sent_color = '#6b7280'
                sent_icon = '➡️'
            
            price = coin_price.get('price', 0)
            change = coin_price.get('change_24h', 0)
            change_sign = '+' if change >= 0 else ''
            change_color = '#22c55e' if change >= 0 else '#ef4444'
            
            # 新闻标题
            news_html = ""
            for n in coin_news:
                title = n.get('title', '')[:60] + '...' if len(n.get('title', '')) > 60 else n.get('title', '')
                news_html += f'<div style="font-size:0.8em;color:#888;margin:4px 0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">📰 {title}</div>'
            
            if not news_html:
                news_html = '<div style="font-size:0.8em;color:#666;">暂无新闻</div>'
            
            rows += f"""
            <div style="padding:12px;margin:8px 0;background:rgba(255,255,255,0.03);border-radius:8px;border-left:3px solid {sent_color};">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                    <span style="font-weight:600;font-size:1.1em;">{coin}/USDT</span>
                    <span style="font-size:0.85em;color:{change_color};font-weight:600;">${price:,.2f} ({change_sign}{change:.2f}%)</span>
                </div>
                <div style="display:flex;justify-content:space-between;margin-bottom:8px;font-size:0.85em;">
                    <span style="color:{sent_color};">{sent_icon} 情绪：{sentiment_label} ({sentiment_score:+.2f})</span>
                    <span style="color:#888;">📰 {len(coin_news)} 条新闻</span>
                </div>
                <div style="border-top:1px solid rgba(255,255,255,0.05);padding-top:8px;">
                    {news_html}
                </div>
            </div>
            """
        
        return f"""
        <div class="card" style="grid-column:span 2;">
            <h2>🌍 全球战情室 · 实时新闻</h2>
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:15px;padding:10px;background:rgba(102,126,234,0.1);border-radius:8px;">
                <div>
                    <span style="font-size:0.9em;color:#888;">📰 新闻总数</span>
                    <div style="font-size:1.5em;font-weight:700;color:#667eea;">{total_news} 条</div>
                </div>
                <div>
                    <span style="font-size:0.9em;color:#888;">🕐 最后更新</span>
                    <div style="font-size:1.1em;font-weight:600;color:#e0e0e0;">{report_time}</div>
                </div>
                <div>
                    <span style="font-size:0.9em;color:#888;">🔄 更新频率</span>
                    <div style="font-size:1.1em;font-weight:600;color:#22c55e;">60 秒</div>
                </div>
            </div>
            
            <div style="margin-bottom:5px;">
                <h3 style="color:#667eea;margin-bottom:10px;font-size:1em;">📋 币种新闻 + 情绪</h3>
                {rows}
            </div>
            
            <div style="margin-top:15px;padding:10px;background:rgba(102,126,234,0.05);border-radius:8px;font-size:0.8em;color:#666;">
                📊 数据来源：Google News · 情绪分析：AI · 🔄 每 60 秒自动更新
            </div>
        </div>
        """
    except Exception as e:
        return f'<div class="card" style="grid-column:span 2;"><h2>🌍 全球战情室</h2><span class="error">加载失败：{e}</span></div>'


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


def get_promotion_stats():
    """推广活动统计"""
    try:
        promo_file = Ziwei_DIR / "data" / "x402" / "promotions" / "promotion_tracker.json"
        log_file = Ziwei_DIR / "data" / "x402" / "promotions" / "promotion_log.md"
        
        if not promo_file.exists():
            return f'<div class="card"><h2>📢 推广活动</h2><span class="warning">推广数据加载中...</span></div>'
        
        with open(promo_file) as f:
            promo = json.load(f)
        
        channels = promo.get('channels', {})
        referral = promo.get('referral_program', {})
        summary = promo.get('summary', {})
        
        # 渠道状态
        channel_rows = ""
        for key, channel in channels.items():
            status_icon = "🟢" if channel.get('status') == 'active' else "🟡" if channel.get('status') == 'ready' else "⚪"
            status_text = {"active": "进行中", "ready": "就绪", "preparing": "准备中", "scheduled": "计划中"}.get(channel.get('status'), '未知')
            channel_rows += f"""
            <div style="padding:6px;margin:4px 0;background:rgba(255,255,255,0.03);border-radius:4px;font-size:0.85em;display:flex;justify-content:space-between;align-items:center;">
                <span>{status_icon} {channel.get('name', key)}</span>
                <span style="color:#888;font-size:0.9em;">{status_text}</span>
            </div>
            """
        
        # 推荐计划
        referral_info = f"""
        <div style="margin-top:15px;padding:12px;background:rgba(34,197,94,0.05);border-radius:8px;">
            <div style="font-weight:600;color:#22c55e;margin-bottom:8px;">🤝 推荐计划</div>
            <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:10px;font-size:0.85em;">
                <div>
                    <span style="color:#888;">奖励类型：</span>
                    <span style="color:#e0e0e0;">{referral.get('reward_amount', 0)} 次 API 调用</span>
                </div>
                <div>
                    <span style="color:#888;">现金支出：</span>
                    <span style="color:#22c55e;">✅ 无（零风险）</span>
                </div>
                <div>
                    <span style="color:#888;">推荐人数：</span>
                    <span style="color:#e0e0e0;">{referral.get('total_referrers', 0)}</span>
                </div>
                <div>
                    <span style="color:#888;">实际成本：</span>
                    <span style="color:#e0e0e0;">${referral.get('cost_usd', 0):.2f} USDC</span>
                </div>
            </div>
        </div>
        """
        
        # 推广日志链接
        log_link = ""
        if log_file.exists():
            log_link = f"""
            <div style="margin-top:10px;text-align:center;">
                <a href="file://{log_file}" target="_blank" style="color:#667eea;text-decoration:none;font-size:0.85em;">📄 查看推广活动日志 →</a>
            </div>
            """
        
        return f"""
        <div class="card" style="grid-column:span 2;">
            <h2>📢 推广活动追踪</h2>
            
            <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:15px;margin-bottom:15px;">
                <div style="text-align:center;padding:15px;background:rgba(102,126,234,0.1);border-radius:8px;">
                    <div style="font-size:1.8em;font-weight:700;color:#667eea;">{summary.get('total_channels', 0)}</div>
                    <div style="font-size:0.85em;color:#888;">推广渠道</div>
                </div>
                <div style="text-align:center;padding:15px;background:rgba(34,197,94,0.1);border-radius:8px;">
                    <div style="font-size:1.8em;font-weight:700;color:#22c55e;">{summary.get('active_channels', 0)}</div>
                    <div style="font-size:0.85em;color:#888;">进行中</div>
                </div>
                <div style="text-align:center;padding:15px;background:rgba(245,158,11,0.1);border-radius:8px;">
                    <div style="font-size:1.8em;font-weight:700;color:#f59e0b;">{summary.get('total_conversions', 0)}</div>
                    <div style="font-size:0.85em;color:#888;">转化用户</div>
                </div>
                <div style="text-align:center;padding:15px;background:rgba(139,92,246,0.1);border-radius:8px;">
                    <div style="font-size:1.8em;font-weight:700;color:#8b5cf6;">${summary.get('total_cost_usd', 0):.2f}</div>
                    <div style="font-size:0.85em;color:#888;">总成本 (USD)</div>
                </div>
            </div>
            
            <div style="margin-bottom:15px;">
                <div style="font-weight:600;color:#667eea;margin-bottom:8px;">📡 推广渠道</div>
                {channel_rows}
            </div>
            
            {referral_info}
            
            <div style="margin-top:15px;padding:10px;background:rgba(102,126,234,0.05);border-radius:6px;font-size:0.85em;">
                <div style="color:#667eea;">
                    💡 <b>推广策略：</b>零现金支出，只送 API 调用次数。实际成本约 $0.0013/次，用户感知价值 $0.05/次。
                </div>
            </div>
            
            {log_link}
        </div>
        """
    except Exception as e:
        return f'<div class="card" style="grid-column:span 2;"><h2>📢 推广活动</h2><span class="error">{e}</span></div>'


def get_status_report():
    """项目状态完整报告"""
    try:
        report_path = Ziwei_DIR / "projects" / "x402-trading-bot" / "STATUS_REPORT.md"
        if not report_path.exists():
            return f'<div class="card"><h2>📋 项目状态报告</h2><span class="warning">报告文件不存在</span></div>'
        
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 将 Markdown 转换为简单 HTML
        lines = content.split('\n')
        html_parts = []
        in_code_block = False
        in_table = False
        
        for line in lines:
            if line.startswith('```'):
                if in_code_block:
                    html_parts.append('</pre></div>')
                    in_code_block = False
                else:
                    html_parts.append('<div style="background:rgba(0,0,0,0.3);border-radius:6px;padding:10px;margin:10px 0;overflow-x:auto;"><pre style="margin:0;font-family:monospace;font-size:0.85em;color:#22c55e;">')
                    in_code_block = True
            elif in_code_block:
                html_parts.append(line.replace('<', '&lt;').replace('>', '&gt;'))
            elif line.startswith('### '):
                html_parts.append(f'<h3 style="color:#667eea;margin:20px 0 10px 0;font-size:1.1em;">{line[4:].strip()}</h3>')
            elif line.startswith('## '):
                html_parts.append(f'<h2 style="color:#764ba2;margin:25px 0 15px 0;font-size:1.3em;border-bottom:2px solid rgba(118,75,162,0.3);padding-bottom:8px;">{line[3:].strip()}</h2>')
            elif line.startswith('- **'):
                # 加粗列表项
                text = line[2:].strip()
                text = text.replace('**', '</b>').replace('**', '<b>')
                html_parts.append(f'<div style="margin:8px 0;padding:8px;background:rgba(255,255,255,0.03);border-radius:4px;">{text}</div>')
            elif line.startswith('- '):
                html_parts.append(f'<div style="margin:6px 0;padding-left:15px;">• {line[2:].strip()}</div>')
            elif line.startswith('| **') and '|' in line:
                # 表格标题行
                cells = [c.strip() for c in line.split('|') if c.strip()]
                html_parts.append('<table style="width:100%;margin:15px 0;border-collapse:collapse;font-size:0.9em;">')
                html_parts.append('<tr style="background:rgba(102,126,234,0.2);">')
                for cell in cells:
                    cell = cell.replace('**', '')
                    html_parts.append(f'<th style="padding:10px;text-align:left;border-bottom:2px solid rgba(102,126,234,0.5);">{cell}</th>')
                html_parts.append('</tr>')
                in_table = True
            elif in_table and line.startswith('|'):
                cells = [c.strip() for c in line.split('|') if c.strip()]
                html_parts.append('<tr>')
                for cell in cells:
                    # 处理 ✅ ❌ 等符号
                    html_parts.append(f'<td style="padding:8px 10px;border-bottom:1px solid rgba(255,255,255,0.05);">{cell}</td>')
                html_parts.append('</tr>')
            elif in_table and not line.startswith('|'):
                html_parts.append('</table>')
                in_table = False
            elif line.strip() == '':
                if in_table:
                    html_parts.append('</table>')
                    in_table = False
            elif line.startswith('**'):
                text = line.strip().replace('**', '</b>').replace('**', '<b>')
                html_parts.append(f'<p style="margin:10px 0;"><b>{text}</b></p>')
            elif not line.startswith('#') and line.strip():
                html_parts.append(f'<p style="margin:8px 0;line-height:1.6;">{line.strip()}</p>')
        
        if in_code_block:
            html_parts.append('</pre></div>')
        if in_table:
            html_parts.append('</table>')
        
        html_content = ''.join(html_parts)
        
        return f"""
        <div class="card" style="grid-column:span 2;">
            <h2>📋 项目状态完整报告</h2>
            <div style="font-size:0.85em;color:#888;margin-bottom:15px;">最后更新：2026-03-05 12:00</div>
            <div style="max-height:600px;overflow-y:auto;padding-right:10px;">
                {html_content}
            </div>
        </div>
        """
    except Exception as e:
        return f'<div class="card" style="grid-column:span 2;"><h2>📋 项目状态报告</h2><span class="error">{e}</span></div>'


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        content = HTML_TEMPLATE.format(
            system_stats=get_system_stats(),
            service_stats=get_service_stats(),
            trading_stats=get_trading_stats(),
            trading_signals=get_trading_signals(),
            security_stats=get_security_stats(),
            income_stats=get_income_stats(),
            api_stats=get_api_stats(),
            crypto_stats=get_crypto_stats(),
            warroom_stats=get_warroom_stats(),
            project_progress=get_project_progress(),
            code_mapping=get_code_mapping(),
            status_report=get_status_report(),
            promotion_stats=get_promotion_stats(),
            update_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            version=VERSION
        )
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        # 强制禁止缓存，确保每次都是最新版本
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        self.send_header('X-Version', VERSION)  # 添加版本号头
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
