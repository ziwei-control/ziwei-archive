#!/usr/bin/env python3
# =============================================================================
# 紫微智控 - 系统监控 Dashboard
# 功能：系统状态、服务监控、安全统计、收入统计、API 调用等
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

# 配置
PORT = 8080
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
        .container {{ max-width: 1400px; margin: 0 auto; }}
        h1 {{ color: white; text-align: center; margin-bottom: 30px; font-size: 2.5em; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 30px; }}
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
        .refresh-btn {{ position: fixed; top: 20px; right: 20px; background: white; border: none; padding: 15px 25px; border-radius: 30px; cursor: pointer; box-shadow: 0 5px 15px rgba(0,0,0,0.2); font-weight: bold; color: #667eea; transition: all 0.3s; }}
        .refresh-btn:hover {{ transform: scale(1.05); box-shadow: 0 8px 20px rgba(0,0,0,0.3); }}
        .last-update {{ text-align: center; color: white; margin-top: 20px; opacity: 0.8; }}
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
        </div>
        
        <div class="last-update">
            最后更新：{update_time}
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
    """获取安全统计"""
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
        
        # 最近攻击类型统计
        attack_types = {}
        for log in attack_log[-50:]:
            t = log.get("attack_type", "unknown")
            attack_types[t] = attack_types.get(t, 0) + 1
        
        attack_type_rows = ""
        for atype, count in sorted(attack_types.items(), key=lambda x: x[1], reverse=True)[:5]:
            attack_type_rows += f"<tr><td>{atype}</td><td>{count} 次</td></tr>"
        
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
            
            <h3 style="margin-top: 20px; color: #667eea;">攻击类型统计</h3>
            <table>
                <tr><th>攻击类型</th><th>次数</th></tr>
                {attack_type_rows if attack_type_rows else '<tr><td colspan="2">无攻击记录</td></tr>'}
            </table>
        </div>
        """
    except Exception as e:
        return f'<div class="card"><h2>🛡️ 安全监控</h2><p class="status-error">获取失败：{e}</p></div>'


def get_income_stats():
    """获取收入统计"""
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
                
                <h3 style="margin-top: 20px; color: #667eea;">最近收入</h3>
                <table>
                    <tr><th>日期</th><th>收入</th></tr>
                    {income_rows if income_rows else '<tr><td colspan="2">无收入记录</td></tr>'}
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
    print("🚀 紫微智控 - 系统监控 Dashboard")
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
    print(f"🌐 公网访问：http://8.213.149.224:{PORT}")
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
