#!/usr/bin/env python3
# =============================================================================
# 强信号监控器 - 邮件通知
# 功能：监控策略引擎信号，发现强信号立即发送邮件
# =============================================================================

import os
import sys
import json
import smtplib
import time
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

# 配置
STRATEGY_DIR = Path("/home/admin/Ziwei/data/strategy")
SIGNAL_CACHE_FILE = Path("/home/admin/Ziwei/data/strategy/.last_signal_cache")

# 邮件配置
SMTP_SERVER = "smtp.163.com"
SMTP_PORT = 465
SENDER_EMAIL = "pandac00@163.com"
# 从环境变量读取密码，如果没有则使用硬编码（不推荐生产环境）
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "CVQSPKRDHFMZGQNB")  # 163 SMTP 授权码

# 收件人列表
RECEIVERS = [
    "19922307306@189.cn",  # 康纳
    # "pandac00@163.com",  # Martin (可选)
]

# 信号强度阈值
STRONG_SIGNAL_THRESHOLD = 15.0  # STRONG_BUY 阈值
BUY_SIGNAL_THRESHOLD = 10.0     # BUY 阈值


def load_last_signal():
    """加载最后处理的信号"""
    if SIGNAL_CACHE_FILE.exists():
        with open(SIGNAL_CACHE_FILE, 'r') as f:
            return json.load(f)
    return {'timestamp': '', 'signals': []}


def save_last_signal(data):
    """保存最后处理的信号"""
    with open(SIGNAL_CACHE_FILE, 'w') as f:
        json.dump(data, f)


def get_latest_signal():
    """获取最新信号文件"""
    signal_files = sorted(STRATEGY_DIR.glob("signals_*.json"), reverse=True)
    if not signal_files:
        return None
    
    with open(signal_files[0], 'r') as f:
        return json.load(f)


def find_strong_signals(signals):
    """找出强信号"""
    strong = []
    for signal in signals:
        score = signal.get('score', 0)
        signal_type = signal.get('signal', '')
        
        # STRONG_BUY 或分数超过阈值
        if signal_type == 'STRONG_BUY' or score >= STRONG_SIGNAL_THRESHOLD:
            strong.append({
                **signal,
                'alert_level': 'STRONG_BUY'
            })
        elif signal_type == 'BUY' or score >= BUY_SIGNAL_THRESHOLD:
            strong.append({
                **signal,
                'alert_level': 'BUY'
            })
    
    return strong


def send_email(subject, body, receivers=None):
    """发送邮件"""
    if receivers is None:
        receivers = RECEIVERS
    
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = ', '.join(receivers)
    msg['Subject'] = subject
    
    msg.attach(MIMEText(body, 'html', 'utf-8'))
    
    try:
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=10)
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"✅ 邮件已发送：{subject}")
        return True
    except Exception as e:
        print(f"❌ 邮件发送失败：{e}")
        return False


def create_signal_email(signals):
    """创建信号邮件内容"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 获取最新价格
    intel_file = sorted(Path("/home/admin/Ziwei/data/intel").glob("intel_*.json"), reverse=True)
    prices = {}
    if intel_file:
        with open(intel_file[0], 'r') as f:
            intel = json.load(f)
            prices = intel.get('prices', {})
    
    html = f"""
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #2c3e50; }}
        .strong {{ color: #e74c3c; font-weight: bold; }}
        .buy {{ color: #f39c12; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #3498db; color: white; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
        .alert {{ background-color: #fff3cd; border: 1px solid #ffc107; padding: 15px; margin: 20px 0; }}
        .footer {{ margin-top: 30px; color: #7f8c8d; font-size: 12px; }}
    </style>
</head>
<body>
    <h1>🚨 紫微智控 - 强信号警报</h1>
    <p><strong>发现时间：</strong>{now}</p>
    
    <div class="alert">
        <strong>⚠️ 发现 {len(signals)} 个强信号！</strong><br>
        请立即查看并考虑执行交易。
    </div>
    
    <h2>📊 信号详情</h2>
    <table>
        <tr>
            <th>代币</th>
            <th>信号</th>
            <th>分数</th>
            <th>价格</th>
            <th>24h 变化</th>
            <th>建议仓位</th>
            <th>止损</th>
            <th>止盈</th>
        </tr>
"""
    
    for signal in signals:
        alert_class = "strong" if signal['alert_level'] == 'STRONG_BUY' else "buy"
        html += f"""
        <tr>
            <td><strong>{signal['symbol']}</strong></td>
            <td class="{alert_class}">{signal['alert_level']}</td>
            <td>{signal['score']}</td>
            <td>${signal['price']:,.6f}</td>
            <td>{signal['change_24h']:.2f}%</td>
            <td>${signal['suggested_amount_usd']:,.2f}</td>
            <td>${signal['stop_loss']:,.6f}</td>
            <td>${signal['take_profit']:,.6f}</td>
        </tr>
"""
    
    html += """
    </table>
    
    <h2>💡 操作建议</h2>
    <ol>
        <li>立即登录 Dashboard 查看实时数据</li>
        <li>确认信号强度和风险</li>
        <li>考虑执行交易（模拟或真实）</li>
        <li>设置止损和止盈</li>
    </ol>
    
    <h2>🔗 快速链接</h2>
    <ul>
        <li><a href="http://panda66.duckdns.org:8081">Dashboard (内网)</a></li>
        <li><a href="http://8.213.149.224:8081">Dashboard (公网)</a></li>
    </ul>
    
    <div class="footer">
        <p>此邮件由紫微智控交易系统自动发送</p>
        <p>策略引擎 v3.0 | 信念×如意×爱人 联合监控</p>
    </div>
</body>
</html>
"""
    
    return html


def main():
    """主函数"""
    print("=" * 70)
    print("📧 强信号监控器启动")
    print("=" * 70)
    print(f"监控目录：{STRATEGY_DIR}")
    print(f"邮件接收：{', '.join(RECEIVERS)}")
    print(f"STRONG_BUY 阈值：>={STRONG_SIGNAL_THRESHOLD}")
    print(f"BUY 阈值：>={BUY_SIGNAL_THRESHOLD}")
    print("=" * 70)
    
    last_signal = load_last_signal()
    
    while True:
        try:
            # 获取最新信号
            signals = get_latest_signal()
            
            if not signals:
                print("⏳ 暂无信号数据，等待...")
                time.sleep(30)
                continue
            
            # 找出强信号
            strong_signals = find_strong_signals(signals)
            
            if strong_signals:
                # 检查是否是新信号（避免重复发送）
                current_timestamp = signals[0].get('timestamp', '') if signals else ''
                
                if current_timestamp != last_signal.get('timestamp', ''):
                    print(f"\n🚨 发现 {len(strong_signals)} 个强信号！")
                    for s in strong_signals:
                        print(f"   {s['symbol']}: {s['alert_level']} (score: {s['score']})")
                    
                    # 发送邮件
                    subject = f"🚨 紫微智控 - 发现{len(strong_signals)}个强信号 ({datetime.now().strftime('%m-%d %H:%M')})"
                    body = create_signal_email(strong_signals)
                    
                    if send_email(subject, body):
                        print("✅ 邮件已发送")
                        
                        # 更新缓存
                        last_signal = {
                            'timestamp': current_timestamp,
                            'signals': [s['symbol'] for s in strong_signals]
                        }
                        save_last_signal(last_signal)
                else:
                    print("⏭️ 信号已处理，跳过")
            else:
                print("⏳ 暂无强信号，继续监控...")
            
            # 等待 30 秒后检查
            time.sleep(30)
            
        except KeyboardInterrupt:
            print("\n🛑 监控器已停止")
            break
        except Exception as e:
            print(f"❌ 错误：{e}")
            import traceback
            traceback.print_exc()
            time.sleep(60)


if __name__ == '__main__':
    main()
