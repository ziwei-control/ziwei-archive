#!/usr/bin/env python3
# =============================================================================
# 紫微智控 - 系统监控 Dashboard v2.0
# 功能：系统状态、服务监控、安全统计、收入统计、API 调用、代码映射等
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
import re

# 配置
PORT = 8081
Ziwei_DIR = Path("/home/admin/Ziwei")

# HTML 模板
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>紫微智控 - 系统监控 Dashboard</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 20px; }}
        .container {{ max-width: 1600px; margin: 0 auto; }}
        h1 {{ color: white; text-align: center; margin-bottom: 30px; font-size: 2.5em; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .card {{ background: white; border-radius: 15px; padding: 25px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); transition: transform 0.3s; }}
        .card:hover {{ transform: translateY(-5px); }}
        .card h2 {{ color: #667eea; margin-bottom: 15px; font-size: 1.5em; border-bottom: 2px solid #667eea; padding-bottom: 10px; }}
        .stat {{ display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #eee; }}
        .stat:last-child {{ border-bottom: none; }}
        .stat-label {{ color: #666; font-weight: 500; }}
        .stat-value {{ color: #333; font-weight: bold; font-size: 1.2em; }}
        .status-ok {{ color: #28a745; }}
        .status-error {{ color: #dc3545; }}
        .status-warning {{ color: #ffc107; }}
        .progress-bar {{ background: #e9ecef; border-radius: 10px; height: 20px; overflow: hidden; margin: 10px 0; }}
        .progress-fill {{ background: linear-gradient(90deg, #667eea, #764ba2); height: 100%; transition: width 0.5s; }}
        .badge {{ display: inline-block; padding: 5px 10px; border-radius: 20px; font-size: 0.8em; font-weight: bold; }}
        .badge-success {{ background: #28a745; color: white; }}
        .badge-danger {{ background: #dc3545; color: white; }}
        .badge-warning {{ background: #ffc107; color: #333; }}
        .badge-info {{ background: #17a2b8; color: white; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #eee; }}
        th {{ background: #667eea; color: white; }}
        tr:hover {{ background: #f8f9fa; }}
        .refresh-btn {{ position: fixed; top: 20px; right: 20px; background: white; border: none; padding: 15px 25px; border-radius: 30px; cursor: pointer; box-shadow: 0 5px 15px rgba(0,0,0,0.2); font-weight: bold; color: #667eea; transition: all 0.3s; z-index: 1000; }}
        .refresh-btn:hover {{ transform: scale(1.05); box-shadow: 0 8px 20px rgba(0,0,0,0.3); }}
        .last-update {{ text-align: center; color: white; margin-top: 20px; opacity: 0.8; }}
        .code-block {{ background: #1e1e1e; color: #d4d4d4; padding: 15px; border-radius: 8px; font-family: 'Consolas', 'Monaco', monospace; font-size: 0.85em; overflow-x: auto; max-height: 400px; overflow-y: auto; }}
        .code-comment {{ color: #6a9955; }}
        .code-keyword {{ color: #569cd6; }}
        .code-string {{ color: #ce9178; }}
        .code-function {{ color: #dcdcaa; }}
        .code-explain {{ color: #4ec9b0; font-style: italic; }}
        .tx-link {{ color: #667eea; text-decoration: none; }}
        .tx-link:hover {{ text-decoration: underline; }}
        .wide-card {{ grid-column: 1 / -1; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 紫微智控 - 系统监控 Dashboard</h1>
        <button class="refresh-btn" onclick="location.reload()">🔄 刷新</button>
        
        <div class="grid">
            {system_stats}
            {service_stats}
            {security_stats}
            {income_stats}
            {api_stats}
            {project_progress}
            {code_mapping}
        </div>
        
        <div class="last-update">
            最后更新：{update_time} | 自动刷新：30 秒
        </div>
    </div>
    
    <script>
        // 自动刷新 (每 30 秒)
        setTimeout(() => location.reload(), 30000);
    </script>
</body>
</html>
"""


def get_system_stats():
    """获取系统统计"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return f"""
        <div class="card">
            <h2>💻 系统状态</h2>
            <div class="stat">
                <span class="stat-label">CPU 使用率</span>
                <span class="stat-value {'status-warning' if cpu_percent > 70 else 'status-ok'}">{cpu_percent}%</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {cpu_percent}%"></div>
            </div>
            
            <div class="stat">
                <span class="stat-label">内存使用</span>
                <span class="stat-value {'status-warning' if memory.percent > 70 else 'status-ok'}">{memory.percent}%</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {memory.percent}%"></div>
            </div>
            
            <div class="stat">
                <span class="stat-label">磁盘使用</span>
                <span class="stat-value {'status-warning' if disk.percent > 70 else 'status-ok'}">{disk.percent}%</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {disk.percent}%"></div>
            </div>
            
            <div class="stat">
                <span class="stat-label">运行时间</span>
                <span class="stat-value">{datetime.fromtimestamp(psutil.boot_time()).strftime('%Y-%m-%d %H:%M')}</span>
            </div>
        </div>
        """
    except Exception as e:
        return f'<div class="card"><h2>💻 系统状态</h2><p class="status-error">获取失败：{e}</p></div>'


def get_service_stats():
    """获取服务统计"""
    services = [
        ("x402 API", "ziwei-x402-api", "http://localhost:5002/health"),
        ("全球战情室", "ziwei-warroom", None),
        ("交易机器人", "ziwei-trading-bot", None),
        ("自动同步监控", "ziwei-sync-watchdog", None),
        ("日志修剪", "ziwei-log-trim", None),
        ("Dashboard", "ziwei-dashboard", None),
    ]
    
    rows = ""
    for name, service, health_url in services:
        try:
            result = subprocess.run(['systemctl', 'is-active', service], capture_output=True, text=True)
            status = result.stdout.strip()
            
            if status == "active":
                badge = '<span class="badge badge-success">✅ 运行中</span>'
            else:
                badge = '<span class="badge badge-danger">❌ 已停止</span>'
            
            rows += f"<tr><td>{name}</td><td>{badge}</td></tr>"
        except:
            rows += f"<tr><td>{name}</td><td><span class='badge badge-warning'>⚠️ 未知</span></td></tr>"
    
    return f"""
    <div class="card">
        <h2>🔧 服务状态</h2>
        <table>
            <tr><th>服务名称</th><th>状态</th></tr>
            {rows}
        </table>
    </div>
    """


def get_security_stats():
    """获取安全统计（带攻击来源地址）"""
    try:
        security_dir = Path("/home/admin/Ziwei/data/security")
        
        # 加载攻击日志
        attack_log = []
        attack_log_file = security_dir / "attack_log.json"
        if attack_log_file.exists():
            with open(attack_log_file, "r") as f:
                attack_log = json.load(f)
        
        # 加载黑名单
        blacklist = []
        blacklist_file = security_dir / "blacklist.json"
        if blacklist_file.exists():
            with open(blacklist_file, "r") as f:
                blacklist = json.load(f).get("ips", [])
        
        # 加载 IP 统计
        ip_stats = {}
        ip_stats_file = security_dir / "ip_stats.json"
        if ip_stats_file.exists():
            with open(ip_stats_file, "r") as f:
                ip_stats = json.load(f)
        
        total_attacks = len(attack_log)
        blocked_ips = len([ip for ip, stats in ip_stats.items() if stats.get("blocked_until", 0) > __import__('time').time()])
        
        # 攻击来源地址统计（带详情）
        attack_sources = {}
        for log in attack_log[-50:]:
            ip = log.get("ip", "unknown")
            attack_type = log.get("attack_type", "unknown")
            details = log.get("details", "")[:50]
            
            if ip not in attack_sources:
                attack_sources[ip] = {"count": 0, "types": [], "last_attack": ""}
            
            attack_sources[ip]["count"] += 1
            if attack_type not in attack_sources[ip]["types"]:
                attack_sources[ip]["types"].append(attack_type)
            attack_sources[ip]["last_attack"] = f"{attack_type}: {details}"
        
        # 生成攻击来源表格
        source_rows = ""
        for ip, data in sorted(attack_sources.items(), key=lambda x: x[1]["count"], reverse=True)[:10]:
            is_blocked = "🔒" if ip in blacklist else "⚠️"
            types_str = ", ".join(data["types"])
            source_rows += f"""
            <tr>
                <td>{is_blocked} {ip}</td>
                <td>{data['count']}次</td>
                <td>{types_str}</td>
                <td style="font-size:0.8em;color:#666;">{data['last_attack'][:40]}...</td>
            </tr>
            """
        
        return f"""
        <div class="card">
            <h2>🛡️ 安全监控</h2>
            <div class="stat">
                <span class="stat-label">总攻击数</span>
                <span class="stat-value status-danger">{total_attacks}</span>
            </div>
            <div class="stat">
                <span class="stat-label">当前封禁</span>
                <span class="stat-value status-warning">{blocked_ips}</span>
            </div>
            <div class="stat">
                <span class="stat-label">黑名单 IP</span>
                <span class="stat-value status-danger">{len(blacklist)}</span>
            </div>
            
            <h3 style="margin-top: 20px; color: #667eea;">攻击来源地址 (Top 10)</h3>
            <table>
                <tr><th>来源 IP</th><th>攻击次数</th><th>攻击类型</th><th>最近攻击</th></tr>
                {source_rows if source_rows else '<tr><td colspan="4">无攻击记录</td></tr>'}
            </table>
        </div>
        """
    except Exception as e:
        return f'<div class="card"><h2>🛡️ 安全监控</h2><p class="status-error">获取失败：{e}</p></div>'


def get_income_stats():
    """获取收入统计（带最近交易记录和链接）"""
    try:
        payments_file = Path("/home/admin/Ziwei/projects/x402-api/data/payments.json")
        
        if payments_file.exists():
            with open(payments_file, "r") as f:
                payments_data = json.load(f)
            
            payments = payments_data.get("payments", {})
            total_income = sum(p.get("amount", 0) for p in payments.values() if p.get("verified"))
            total_transactions = len([p for p in payments.values() if p.get("verified")])
            
            # 按日期统计
            daily_income = {}
            for p in payments.values():
                if p.get("verified"):
                    date = p.get("timestamp", "")[:10]
                    daily_income[date] = daily_income.get(date, 0) + p.get("amount", 0)
            
            income_rows = ""
            for date in sorted(daily_income.keys(), reverse=True)[:7]:
                income_rows += f"<tr><td>{date}</td><td>{daily_income[date]:.4f} USDC</td></tr>"
            
            # 最近交易记录（带链接）
            recent_txs = ""
            sorted_payments = sorted(payments.values(), key=lambda x: x.get("timestamp", ""), reverse=True)[:10]
            
            for p in sorted_payments:
                tx_hash = p.get("tx_hash", "")
                amount = p.get("amount", 0)
                timestamp = p.get("timestamp", "")[:19]
                sender = p.get("sender", "")[:20]
                
                # 区块链浏览器链接
                if tx_hash and not tx_hash.startswith("0x0000") and not tx_hash.startswith("0xaaaa"):
                    tx_link = f'<a href="https://basescan.org/tx/{tx_hash}" target="_blank" class="tx-link">🔗 查看</a>'
                else:
                    tx_link = '<span style="color:#999;">⚠️ 测试</span>'
                
                recent_txs += f"""
                <tr>
                    <td>{timestamp}</td>
                    <td>{amount:.4f} USDC</td>
                    <td style="font-size:0.85em;">{sender}...</td>
                    <td>{tx_link}</td>
                </tr>
                """
            
            return f"""
            <div class="card">
                <h2>💰 收入统计</h2>
                <div class="stat">
                    <span class="stat-label">总收入</span>
                    <span class="stat-value status-success">{total_income:.4f} USDC</span>
                </div>
                <div class="stat">
                    <span class="stat-label">总交易</span>
                    <span class="stat-value">{total_transactions}</span>
                </div>
                
                <h3 style="margin-top: 20px; color: #667eea;">每日收入</h3>
                <table>
                    <tr><th>日期</th><th>收入</th></tr>
                    {income_rows if income_rows else '<tr><td colspan="2">无收入记录</td></tr>'}
                </table>
                
                <h3 style="margin-top: 20px; color: #667eea;">最近交易记录</h3>
                <table>
                    <tr><th>时间</th><th>金额</th><th>发送方</th><th>交易链接</th></tr>
                    {recent_txs if recent_txs else '<tr><td colspan="4">无交易记录</td></tr>'}
                </table>
            </div>
            """
        else:
            return """
            <div class="card">
                <h2>💰 收入统计</h2>
                <div class="stat">
                    <span class="stat-label">总收入</span>
                    <span class="stat-value">0.0000 USDC</span>
                </div>
                <p style="color: #999; margin-top: 20px;">暂无支付记录</p>
            </div>
            """
    except Exception as e:
        return f'<div class="card"><h2>💰 收入统计</h2><p class="status-error">获取失败：{e}</p></div>'


def get_api_stats():
    """获取 API 统计"""
    try:
        # 尝试从 API 获取统计
        try:
            with urllib.request.urlopen("http://localhost:5002/api/v1/stats", timeout=5) as response:
                stats = json.loads(response.read().decode())
                
                api_prices = stats.get("prices", {})
                price_rows = ""
                for endpoint, price in api_prices.items():
                    price_rows += f"<tr><td>/api/v1/{endpoint}</td><td>{price} USDC</td></tr>"
                
                return f"""
                <div class="card">
                    <h2>📡 API 端点</h2>
                    <div class="stat">
                        <span class="stat-label">端点数量</span>
                        <span class="stat-value">{len(api_prices)}</span>
                    </div>
                    
                    <h3 style="margin-top: 20px; color: #667eea;">价格列表</h3>
                    <table>
                        <tr><th>端点</th><th>价格</th></tr>
                        {price_rows}
                    </table>
                </div>
                """
        except:
            # API 不可用时显示静态数据
            api_prices = {
                "code-audit": 0.05,
                "translate": 0.02,
                "architect": 0.10,
                "code-gen": 0.08,
                "logic": 0.06,
                "long-text": 0.03,
                "crawl": 0.04,
                "vision": 0.15
            }
            
            price_rows = ""
            for endpoint, price in api_prices.items():
                price_rows += f"<tr><td>/api/v1/{endpoint}</td><td>{price} USDC</td></tr>"
            
            return f"""
            <div class="card">
                <h2>📡 API 端点</h2>
                <div class="stat">
                    <span class="stat-label">端点数量</span>
                    <span class="stat-value">{len(api_prices)}</span>
                </div>
                
                <h3 style="margin-top: 20px; color: #667eea;">价格列表</h3>
                <table>
                    <tr><th>端点</th><th>价格</th></tr>
                    {price_rows}
                </table>
            </div>
            """
    except Exception as e:
        return f'<div class="card"><h2>📡 API 端点</h2><p class="status-error">获取失败：{e}</p></div>'


def get_project_progress():
    """获取项目进度"""
    projects = [
        ("x402 API", 100, "✅ 已完成", "success"),
        ("x402 Python SDK", 100, "✅ 已完成", "success"),
        ("x402 交易机器人", 90, "✅ 测试中", "success"),
        ("全球战情室", 100, "✅ 已完成", "success"),
        ("安全防护系统", 100, "✅ 已完成", "success"),
        ("邮件告警系统", 100, "✅ 已完成", "success"),
        ("系统监控 Dashboard", 100, "✅ 已完成", "success"),
    ]
    
    progress_rows = ""
    for name, progress, status, badge_type in projects:
        progress_rows += f"""
        <div style="margin-bottom: 15px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                <span style="font-weight: bold;">{name}</span>
                <span class="badge badge-{badge_type}">{status}</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {progress}%"></div>
            </div>
        </div>
        """
    
    return f"""
    <div class="card">
        <h2>📊 项目进度</h2>
        {progress_rows}
    </div>
    """


def get_code_mapping():
    """获取系统运行代码映射（实时显示实际运行代码 + 中文解释）"""
    try:
        # 获取正在运行的紫微智控进程
        code_files = {
            "x402 API": "/home/admin/Ziwei/projects/x402-api/app_production.py",
            "Dashboard": "/home/admin/Ziwei/projects/dashboard.py",
            "全球战情室": "/home/admin/Ziwei/scripts/global-warroom-upgraded.py",
            "交易机器人": "/home/admin/Ziwei/projects/x402-trading-bot/start_test.py",
            "安全防护": "/home/admin/Ziwei/projects/x402-api/security.py",
            "邮件告警": "/home/admin/Ziwei/projects/x402-api/email_alert.py",
        }
        
        code_blocks = ""
        
        for name, filepath in code_files.items():
            try:
                # 检查进程是否在运行
                process_running = False
                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    try:
                        cmdline = ' '.join(proc.info.get('cmdline', []))
                        if filepath in cmdline:
                            process_running = True
                            break
                    except:
                        pass
                
                # 读取代码文件
                if Path(filepath).exists():
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        lines = f.readlines()[:30]  # 只取前 30 行
                    
                    # 语法高亮
                    highlighted_code = ""
                    for line in lines:
                        # 注释
                        line = re.sub(r'(#.*)', r'<span class="code-comment">\1</span>', line)
                        # 关键字
                        line = re.sub(r'\b(def|class|import|from|return|if|else|elif|try|except|with|as|for|in)\b', r'<span class="code-keyword">\1</span>', line)
                        # 字符串
                        line = re.sub(r'(["\'].*?["\'])', r'<span class="code-string">\1</span>', line)
                        # 函数
                        line = re.sub(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', r'<span class="code-function">\1</span>(', line)
                        
                        highlighted_code += line
                    
                    # 中文解释
                    explanations = {
                        "x402 API": "💡 这是 x402 API 主程序，负责处理所有 API 请求、x402 支付验证、AI 模型调用。当前正在运行，监听端口 5002。",
                        "Dashboard": "💡 这是系统监控 Dashboard，提供实时系统状态、服务监控、安全统计、收入统计等可视化界面。每 30 秒自动刷新。",
                        "全球战情室": "💡 这是全球战情室监控程序，24 小时监控加密货币市场、股票市场、社交媒体热点，发现机会自动发送邮件警报。",
                        "交易机器人": "💡 这是 x402 交易机器人，监控 VIRTUAL、PAYAI 等 x402 生态代币，自动执行网格交易、趋势跟踪等策略。当前为测试模式。",
                        "安全防护": "💡 这是安全防护模块，提供 DDoS 防护、频率限制、IP 黑名单、SQL 注入检测、XSS 检测等功能。实时拦截恶意请求。",
                        "邮件告警": "💡 这是邮件告警模块，当检测到攻击、DDoS、或安全事件时，自动发送邮件通知管理员。支持告警冷却机制。",
                    }
                    
                    explanation = explanations.get(name, "")
                    
                    status_badge = '<span class="badge badge-success">✅ 运行中</span>' if process_running else '<span class="badge badge-warning">⚠️ 未运行</span>'
                    
                    code_blocks += f"""
                    <div style="margin-bottom: 25px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                            <h3 style="color: #667eea; margin: 0;">{name}</h3>
                            {status_badge}
                        </div>
                        <div class="code-block">{highlighted_code}</div>
                        <div style="margin-top: 10px; padding: 10px; background: #e7f3ff; border-left: 4px solid #17a2b8; border-radius: 5px;">
                            <strong>{explanation}</strong>
                        </div>
                    </div>
                    """
                else:
                    code_blocks += f"""
                    <div style="margin-bottom: 25px;">
                        <h3 style="color: #667eea;">{name}</h3>
                        <p class="status-error">❌ 文件不存在：{filepath}</p>
                    </div>
                    """
            except Exception as e:
                code_blocks += f"""
                <div style="margin-bottom: 25px;">
                    <h3 style="color: #667eea;">{name}</h3>
                    <p class="status-error">❌ 读取失败：{e}</p>
                </div>
                """
        
        return f"""
        <div class="card wide-card">
            <h2>🔍 系统运行代码映射</h2>
            <p style="color: #666; margin-bottom: 20px;">实时显示系统实际运行的核心代码，附带中文解释</p>
            {code_blocks}
        </div>
        """
    except Exception as e:
        return f'<div class="card wide-card"><h2>🔍 系统运行代码映射</h2><p class="status-error">获取失败：{e}</p></div>'


class DashboardHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # 收集所有数据
            content = HTML_TEMPLATE.format(
                system_stats=get_system_stats(),
                service_stats=get_service_stats(),
                security_stats=get_security_stats(),
                income_stats=get_income_stats(),
                api_stats=get_api_stats(),
                project_progress=get_project_progress(),
                code_mapping=get_code_mapping(),
                update_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )
            
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(f"Error: {e}".encode('utf-8'))
    
    def log_message(self, format, *args):
        pass  # 禁用日志


def main():
    print("=" * 70)
    print("🚀 紫微智控 - 系统监控 Dashboard v2.0")
    print("=" * 70)
    print()
    
    # 检查依赖
    try:
        import psutil
    except ImportError:
        print("❌ 缺少 psutil 库，正在安装...")
        subprocess.run(['pip3', 'install', 'psutil', '-q'])
        import psutil
    
    print(f"📍 Dashboard 地址：http://0.0.0.0:{PORT}")
    print(f"🌐 公网访问：http://8.213.149.224/dashboard")
    print()
    print("⏰ 自动刷新：每 30 秒")
    print()
    print("=" * 70)
    
    # 允许端口重用
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), DashboardHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Dashboard 已停止")


if __name__ == '__main__':
    main()
