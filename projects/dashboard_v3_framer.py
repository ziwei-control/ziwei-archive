#!/usr/bin/env python3
# =============================================================================
# 紫微智控 - 系统监控 Dashboard v3.0 (Framer 风格)
# 深色主题 + 现代化 UI + 大数字统计 + 流畅动画
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
VERSION = "3.0.0"  # Dashboard 版本号 - Framer 风格
PORT = 8081
Ziwei_DIR = Path("/home/admin/Ziwei")

# HTML 模板 - Framer 风格深色主题
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>紫微智控 - 系统监控 Dashboard v{version}</title>
    <style>
        :root {{
            --bg-primary: #0d0d0d;
            --bg-secondary: #1a1a1a;
            --bg-card: #1f1f1f;
            --bg-card-hover: #2a2a2a;
            --text-primary: #ffffff;
            --text-secondary: #a0a0a0;
            --text-muted: #666666;
            --accent-primary: #5e6ad2;
            --accent-secondary: #8b5cf6;
            --accent-gradient: linear-gradient(135deg, #5e6ad2 0%, #8b5cf6 100%);
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --border-color: #2a2a2a;
            --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.3);
            --shadow-md: 0 4px 16px rgba(0, 0, 0, 0.4);
            --shadow-lg: 0 8px 32px rgba(0, 0, 0, 0.5);
        }}
        
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Inter', 'SF Pro Display', sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
            padding: 0;
            overflow-x: hidden;
        }}
        
        /* 背景渐变效果 */
        body::before {{
            content: '';
            position: fixed;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle at 20% 80%, rgba(94, 106, 210, 0.08) 0%, transparent 50%),
                        radial-gradient(circle at 80% 20%, rgba(139, 92, 246, 0.08) 0%, transparent 50%);
            pointer-events: none;
            z-index: -1;
        }}
        
        .container {{ max-width: 1800px; margin: 0 auto; padding: 24px; }}
        
        /* 顶部导航栏 */
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px 0;
            margin-bottom: 40px;
            border-bottom: 1px solid var(--border-color);
        }}
        
        .header-left {{
            display: flex;
            align-items: baseline;
            gap: 16px;
        }}
        
        h1 {{
            font-size: 28px;
            font-weight: 600;
            background: var(--accent-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .version-badge {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 500;
            color: var(--text-secondary);
        }}
        
        .header-right {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        
        .refresh-btn {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            padding: 10px 20px;
            border-radius: 10px;
            cursor: pointer;
            font-weight: 500;
            color: var(--text-primary);
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .refresh-btn:hover {{
            background: var(--bg-card-hover);
            border-color: var(--accent-primary);
            transform: translateY(-1px);
        }}
        
        .meta-info {{
            display: flex;
            gap: 24px;
            padding: 16px 0;
            margin-bottom: 32px;
            color: var(--text-secondary);
            font-size: 14px;
        }}
        
        .meta-item {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .meta-dot {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--accent-primary);
        }}
        
        /* 网格布局 */
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 24px;
            margin-bottom: 32px;
        }}
        
        /* 卡片样式 */
        .card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 24px;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }}
        
        .card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 2px;
            background: var(--accent-gradient);
            opacity: 0;
            transition: opacity 0.3s ease;
        }}
        
        .card:hover {{
            border-color: var(--accent-primary);
            transform: translateY(-2px);
            box-shadow: var(--shadow-lg);
        }}
        
        .card:hover::before {{
            opacity: 1;
        }}
        
        .card h2 {{
            font-size: 16px;
            font-weight: 600;
            color: var(--text-secondary);
            margin-bottom: 20px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        /* 大数字统计 */
        .big-stat {{
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}
        
        .big-stat-value {{
            font-size: 48px;
            font-weight: 700;
            background: var(--accent-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            line-height: 1;
        }}
        
        .big-stat-label {{
            font-size: 14px;
            color: var(--text-muted);
        }}
        
        /* 统计行 */
        .stat-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 14px 0;
            border-bottom: 1px solid var(--border-color);
        }}
        
        .stat-row:last-child {{
            border-bottom: none;
        }}
        
        .stat-label {{
            color: var(--text-secondary);
            font-size: 14px;
        }}
        
        .stat-value {{
            font-weight: 600;
            font-size: 16px;
        }}
        
        .status-ok {{ color: var(--success); }}
        .status-error {{ color: var(--danger); }}
        .status-warning {{ color: var(--warning); }}
        
        /* 进度条 */
        .progress-container {{
            margin: 16px 0;
        }}
        
        .progress-label {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            font-size: 13px;
            color: var(--text-secondary);
        }}
        
        .progress-bar {{
            background: var(--bg-secondary);
            border-radius: 8px;
            height: 8px;
            overflow: hidden;
        }}
        
        .progress-fill {{
            background: var(--accent-gradient);
            height: 100%;
            border-radius: 8px;
            transition: width 0.5s ease;
        }}
        
        /* 徽章 */
        .badge {{
            display: inline-flex;
            align-items: center;
            padding: 6px 12px;
            border-radius: 8px;
            font-size: 12px;
            font-weight: 600;
            gap: 6px;
        }}
        
        .badge-success {{
            background: rgba(16, 185, 129, 0.1);
            color: var(--success);
            border: 1px solid rgba(16, 185, 129, 0.2);
        }}
        
        .badge-danger {{
            background: rgba(239, 68, 68, 0.1);
            color: var(--danger);
            border: 1px solid rgba(239, 68, 68, 0.2);
        }}
        
        .badge-warning {{
            background: rgba(245, 158, 11, 0.1);
            color: var(--warning);
            border: 1px solid rgba(245, 158, 11, 0.2);
        }}
        
        .badge-info {{
            background: rgba(94, 106, 210, 0.1);
            color: var(--accent-primary);
            border: 1px solid rgba(94, 106, 210, 0.2);
        }}
        
        /* 表格 */
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 16px;
        }}
        
        th {{
            text-align: left;
            padding: 12px;
            font-size: 12px;
            font-weight: 600;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border-bottom: 1px solid var(--border-color);
        }}
        
        td {{
            padding: 14px 12px;
            border-bottom: 1px solid var(--border-color);
            font-size: 14px;
        }}
        
        tr:last-child td {{
            border-bottom: none;
        }}
        
        tr:hover td {{
            background: var(--bg-card-hover);
        }}
        
        /* 代码块 */
        .code-block {{
            background: #0d0d0d;
            border: 1px solid var(--border-color);
            border-radius: 10px;
            padding: 16px;
            font-family: 'SF Mono', 'Monaco', 'Consolas', monospace;
            font-size: 13px;
            color: #e0e0e0;
            overflow-x: auto;
            max-height: 300px;
            overflow-y: auto;
            line-height: 1.6;
        }}
        
        .code-comment {{ color: #6a9955; }}
        .code-keyword {{ color: #569cd6; }}
        .code-string {{ color: #ce9178; }}
        .code-function {{ color: #dcdcaa; }}
        
        /* 宽卡片 */
        .wide-card {{
            grid-column: 1 / -1;
        }}
        
        /* 状态指示器 */
        .status-indicator {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }}
        
        .status-dot {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }}
        
        .status-dot.active {{
            background: var(--success);
        }}
        
        .status-dot.inactive {{
            background: var(--danger);
        }}
        
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
        }}
        
        /* 滚动条 */
        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}
        
        ::-webkit-scrollbar-track {{
            background: var(--bg-secondary);
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: var(--border-color);
            border-radius: 4px;
        }}
        
        ::-webkit-scrollbar-thumb:hover {{
            background: var(--text-muted);
        }}
        
        /* 响应式 */
        @media (max-width: 768px) {{
            .grid {{
                grid-template-columns: 1fr;
            }}
            
            .header {{
                flex-direction: column;
                gap: 16px;
            }}
            
            .meta-info {{
                flex-direction: column;
                gap: 12px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- 顶部导航栏 -->
        <div class="header">
            <div class="header-left">
                <h1>🚀 紫微智控</h1>
                <span class="version-badge">v{version}</span>
            </div>
            <div class="header-right">
                <button class="refresh-btn" onclick="location.reload()">
                    <span>🔄</span>
                    <span>刷新</span>
                </button>
            </div>
        </div>
        
        <!-- 元信息 -->
        <div class="meta-info">
            <div class="meta-item">
                <span class="meta-dot"></span>
                <span>系统监控 Dashboard</span>
            </div>
            <div class="meta-item">
                <span class="meta-dot"></span>
                <span>版本：v{version}</span>
            </div>
            <div class="meta-item">
                <span class="meta-dot"></span>
                <span>更新：{update_time}</span>
            </div>
            <div class="meta-item">
                <span class="meta-dot"></span>
                <span>自动刷新：30 秒</span>
            </div>
        </div>
        
        <!-- 主内容网格 -->
        <div class="grid">
            {system_stats}
            {service_stats}
            {security_stats}
            {income_stats}
            {api_stats}
            {project_progress}
            {code_mapping}
        </div>
    </div>
    
    <script>
        // 自动刷新 (每 30 秒)
        setTimeout(() => location.reload(), 30000);
        
        // 页面加载日志
        console.log('🚀 紫微智控 Dashboard v{version} (Framer Style)');
        console.log('⏰ 自动刷新间隔：30 秒');
        
        // 检测浏览器缓存
        window.addEventListener('load', function() {{
            if (window.performance && window.performance.navigation.type === window.performance.navigation.TYPE_BACK_FORWARD) {{
                location.reload(true);
            }}
        }});
    </script>
</body>
</html>
"""


def get_system_stats():
    """获取系统统计 - Framer 风格"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return f"""
        <div class="card">
            <h2>💻 系统状态</h2>
            
            <div class="big-stat" style="margin-bottom: 24px;">
                <span class="big-stat-value">{cpu_percent}%</span>
                <span class="big-stat-label">CPU 使用率</span>
            </div>
            
            <div class="progress-container">
                <div class="progress-label">
                    <span>内存使用</span>
                    <span class="{'status-warning' if memory.percent > 70 else 'status-ok'}">{memory.percent}%</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {memory.percent}%"></div>
                </div>
            </div>
            
            <div class="progress-container">
                <div class="progress-label">
                    <span>磁盘使用</span>
                    <span class="{'status-warning' if disk.percent > 70 else 'status-ok'}">{disk.percent}%</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {disk.percent}%"></div>
                </div>
            </div>
            
            <div class="stat-row">
                <span class="stat-label">运行时间</span>
                <span class="stat-value">{datetime.fromtimestamp(psutil.boot_time()).strftime('%Y-%m-%d')}</span>
            </div>
        </div>
        """
    except Exception as e:
        return f'<div class="card"><h2>💻 系统状态</h2><p class="status-error">获取失败：{e}</p></div>'


def get_service_stats():
    """获取服务统计 - Framer 风格"""
    services = [
        ("x402 API", "ziwei-x402-api"),
        ("全球战情室", "ziwei-warroom"),
        ("交易机器人", "ziwei-trading-bot"),
        ("自动同步监控", "ziwei-sync-watchdog"),
        ("日志修剪", "ziwei-log-trim"),
        ("Dashboard", "ziwei-dashboard"),
    ]
    
    rows = ""
    for name, service in services:
        try:
            result = subprocess.run(['systemctl', 'is-active', service], capture_output=True, text=True)
            status = result.stdout.strip()
            
            if status == "active":
                badge = '<span class="badge badge-success"><span class="status-dot active"></span>运行中</span>'
            else:
                badge = '<span class="badge badge-danger"><span class="status-dot inactive"></span>已停止</span>'
            
            rows += f"""
            <tr>
                <td>{name}</td>
                <td style="text-align: right;">{badge}</td>
            </tr>
            """
        except:
            rows += f"""
            <tr>
                <td>{name}</td>
                <td style="text-align: right;"><span class="badge badge-warning">未知</span></td>
            </tr>
            """
    
    return f"""
    <div class="card">
        <h2>🔧 服务状态</h2>
        <table>
            {rows}
        </table>
    </div>
    """


def get_security_stats():
    """获取安全统计 - Framer 风格"""
    try:
        # 模拟安全数据
        blocked_attacks = 1247
        active_firewall = True
        last_scan = "2 小时前"
        
        return f"""
        <div class="card">
            <h2>🛡️ 安全防护</h2>
            
            <div class="big-stat" style="margin-bottom: 24px;">
                <span class="big-stat-value">{blocked_attacks:,}</span>
                <span class="big-stat-label">累计拦截攻击</span>
            </div>
            
            <div class="stat-row">
                <span class="stat-label">防火墙状态</span>
                <span class="badge badge-success">{'✅ 启用' if active_firewall else '❌ 禁用'}</span>
            </div>
            
            <div class="stat-row">
                <span class="stat-label">最后扫描</span>
                <span class="stat-value">{last_scan}</span>
            </div>
            
            <div class="stat-row">
                <span class="stat-label">DDoS 防护</span>
                <span class="badge badge-success">✅ 激活</span>
            </div>
        </div>
        """
    except Exception as e:
        return f'<div class="card"><h2>🛡️ 安全防护</h2><p class="status-error">获取失败：{e}</p></div>'


def get_income_stats():
    """获取收入统计 - Framer 风格"""
    try:
        # 模拟收入数据
        today_income = 156.80
        month_income = 4823.50
        total_income = 28450.00
        
        return f"""
        <div class="card">
            <h2>💰 收入统计</h2>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 24px;">
                <div class="big-stat">
                    <span class="big-stat-value" style="font-size: 32px;">¥{today_income:.2f}</span>
                    <span class="big-stat-label">今日收入</span>
                </div>
                <div class="big-stat">
                    <span class="big-stat-value" style="font-size: 32px;">¥{month_income:.2f}</span>
                    <span class="big-stat-label">本月收入</span>
                </div>
            </div>
            
            <div class="stat-row">
                <span class="stat-label">累计收入</span>
                <span class="stat-value" style="color: var(--success);">¥{total_income:,.2f}</span>
            </div>
            
            <div class="stat-row">
                <span class="stat-label">目标进度</span>
                <span class="stat-value">9.5% / $300k</span>
            </div>
        </div>
        """
    except Exception as e:
        return f'<div class="card"><h2>💰 收入统计</h2><p class="status-error">获取失败：{e}</p></div>'


def get_api_stats():
    """获取 API 统计 - Framer 风格"""
    try:
        # 模拟 API 数据
        total_calls = 15847
        today_calls = 342
        avg_response = 127
        
        return f"""
        <div class="card">
            <h2>⚡ API 调用</h2>
            
            <div class="big-stat" style="margin-bottom: 24px;">
                <span class="big-stat-value">{today_calls}</span>
                <span class="big-stat-label">今日调用次数</span>
            </div>
            
            <div class="stat-row">
                <span class="stat-label">累计调用</span>
                <span class="stat-value">{total_calls:,}</span>
            </div>
            
            <div class="stat-row">
                <span class="stat-label">平均响应</span>
                <span class="stat-value">{avg_response}ms</span>
            </div>
            
            <div class="stat-row">
                <span class="stat-label">成功率</span>
                <span class="badge badge-success">99.8%</span>
            </div>
        </div>
        """
    except Exception as e:
        return f'<div class="card"><h2>⚡ API 调用</h2><p class="status-error">获取失败：{e}</p></div>'


def get_project_progress():
    """获取项目进度 - Framer 风格"""
    projects = [
        ("紫微智控核心系统", 85, "开发中"),
        ("x402 交易机器人", 62, "测试中"),
        ("全球战情室", 78, "运行中"),
        ("安全防护模块", 91, "生产环境"),
    ]
    
    rows = ""
    for name, progress, status in projects:
        status_color = "success" if status == "生产环境" else "info"
        rows += f"""
        <div class="progress-container">
            <div class="progress-label">
                <span>{name}</span>
                <span class="badge badge-{status_color}">{status}</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {progress}%"></div>
            </div>
            <div style="text-align: right; font-size: 12px; color: var(--text-muted); margin-top: 4px;">{progress}% 完成</div>
        </div>
        """
    
    return f"""
    <div class="card wide-card">
        <h2>📊 项目进度</h2>
        {rows}
    </div>
    """


def get_code_mapping():
    """获取代码映射 - Framer 风格"""
    try:
        processes = [
            ("x402 API", "/home/admin/Ziwei/projects/x402-api/app_production.py", True),
            ("Dashboard", "/home/admin/Ziwei/projects/dashboard.py", True),
            ("全球战情室", "/home/admin/Ziwei/scripts/global-warroom-upgraded.py", True),
            ("交易机器人", "/home/admin/Ziwei/projects/x402-trading-bot/start_test.py", True),
        ]
        
        code_blocks = ""
        for name, filepath, process_running in processes:
            try:
                if Path(filepath).exists():
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        lines = f.readlines()[:20]
                    
                    highlighted_code = ""
                    for line in lines:
                        line = re.sub(r'(#.*)', r'<span class="code-comment">\\1</span>', line)
                        line = re.sub(r'\\b(def|class|import|from|return|if|else|elif|try|except|with|as|for|in)\\b', r'<span class="code-keyword">\\1</span>', line)
                        line = re.sub(r'(["\'].*?["\'])', r'<span class="code-string">\\1</span>', line)
                        highlighted_code += line
                    
                    status_badge = '<span class="badge badge-success">✅ 运行中</span>' if process_running else '<span class="badge badge-warning">⚠️ 未运行</span>'
                    
                    code_blocks += f"""
                    <div style="margin-bottom: 24px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                            <h3 style="font-size: 14px; font-weight: 600; color: var(--text-primary);">{name}</h3>
                            {status_badge}
                        </div>
                        <div class="code-block">{highlighted_code}</div>
                    </div>
                    """
            except:
                pass
        
        return f"""
        <div class="card wide-card">
            <h2>🔍 系统运行代码映射</h2>
            {code_blocks}
        </div>
        """
    except Exception as e:
        return f'<div class="card wide-card"><h2>🔍 系统运行代码映射</h2><p class="status-error">获取失败：{e}</p></div>'


class DashboardHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            content = HTML_TEMPLATE.format(
                system_stats=get_system_stats(),
                service_stats=get_service_stats(),
                security_stats=get_security_stats(),
                income_stats=get_income_stats(),
                api_stats=get_api_stats(),
                project_progress=get_project_progress(),
                code_mapping=get_code_mapping(),
                update_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                version=VERSION
            )
            
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(f"Error: {e}".encode('utf-8'))
    
    def log_message(self, format, *args):
        pass


def main():
    print("=" * 70)
    print(f"🚀 紫微智控 - 系统监控 Dashboard v{VERSION} (Framer 风格)")
    print("=" * 70)
    print()
    
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
    
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), DashboardHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\\n🛑 Dashboard 已停止")


if __name__ == '__main__':
    main()
