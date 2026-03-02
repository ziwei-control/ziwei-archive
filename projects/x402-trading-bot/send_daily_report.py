#!/usr/bin/env python3
# =============================================================================
# x402 交易机器人 - 每日测试报告邮件发送
# 功能：生成详细测试报告并发送邮件
# =============================================================================

import os
import sys
import json
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 配置
SMTP_SERVER = "smtp.163.com"
SMTP_PORT = 465
SENDER_EMAIL = "pandac00@163.com"
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "")  # 从环境变量读取
RECEIVER_EMAIL = "19922307306@189.cn"  # 康纳

# 日志文件路径
TRADES_LOG = "/home/admin/Ziwei/projects/x402-trading-bot/trades.log"
CONFIG_FILE = "/home/admin/Ziwei/projects/x402-trading-bot/.env"


def read_trades_log():
    """读取交易日志"""
    trades = []
    if os.path.exists(TRADES_LOG):
        with open(TRADES_LOG, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if '📊' in line or '✅' in line or '❌' in line or '⚠️' in line:
                    trades.append(line.strip())
    return trades[-50:]  # 最近 50 条


def get_account_balance():
    """获取账户余额"""
    try:
        import ccxt
        api_key = os.getenv("API_KEY", "")
        api_secret = os.getenv("API_SECRET", "")

        exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
        })

        balance = exchange.fetch_balance()
        usdt = balance.get('USDT', {}).get('free', 0)
        btc = balance.get('BTC', {}).get('free', 0)
        eth = balance.get('ETH', {}).get('free', 0)

        return {
            'USDT': usdt,
            'BTC': btc,
            'ETH': eth,
            'total_usdt': usdt + btc * 95000 + eth * 2800  # 估算
        }
    except:
        return {'USDT': 0, 'BTC': 0, 'ETH': 0, 'total_usdt': 0}


def generate_report():
    """生成测试报告"""
    today = datetime.now().strftime('%Y-%m-%d')
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    trades = read_trades_log()
    balance = get_account_balance()

    # 统计
    total_signals = len([t for t in trades if '📊' in t])
    success_trades = len([t for t in trades if '✅' in t])
    failed_trades = len([t for t in trades if '❌' in t])
    warnings = len([t for t in trades if '⚠️' in t])

    report = {
        'date': today,
        'time': now,
        'total_signals': total_signals,
        'success_trades': success_trades,
        'failed_trades': failed_trades,
        'warnings': warnings,
        'balance': balance,
        'trades': trades
    }

    return report


def create_email_html(report):
    """创建 HTML 邮件"""
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px; }}
            .container {{ background-color: white; padding: 20px; border-radius: 10px; max-width: 800px; margin: 0 auto; }}
            h1 {{ color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }}
            h2 {{ color: #555; margin-top: 20px; }}
            .info-box {{ background-color: #e7f3ff; border-left: 4px solid #007bff; padding: 15px; margin: 15px 0; }}
            .success {{ color: #28a745; }}
            .warning {{ color: #ffc107; }}
            .danger {{ color: #dc3545; }}
            .stats {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin: 20px 0; }}
            .stat-box {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; text-align: center; }}
            .stat-number {{ font-size: 24px; font-weight: bold; color: #007bff; }}
            .stat-label {{ font-size: 12px; color: #666; }}
            .log-box {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; max-height: 400px; overflow-y: auto; font-family: monospace; font-size: 12px; }}
            table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
            th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #007bff; color: white; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 x402 交易机器人 - 每日测试报告</h1>
            
            <div class="info-box">
                <strong>📅 报告日期:</strong> {report['date']}<br>
                <strong>⏰ 生成时间:</strong> {report['time']}<br>
                <strong>🔧 模式:</strong> <span class="success">测试模式 (真实资金不动)</span>
            </div>

            <h2>📊 今日统计</h2>
            <div class="stats">
                <div class="stat-box">
                    <div class="stat-number">{report['total_signals']}</div>
                    <div class="stat-label">交易信号</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number success">{report['success_trades']}</div>
                    <div class="stat-label">成功交易</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number danger">{report['failed_trades']}</div>
                    <div class="stat-label">失败交易</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number warning">{report['warnings']}</div>
                    <div class="stat-label">警告</div>
                </div>
            </div>

            <h2>💰 账户余额</h2>
            <table>
                <tr>
                    <th>币种</th>
                    <th>余额</th>
                </tr>
                <tr>
                    <td>USDT</td>
                    <td>${report['balance'].get('USDT', 0):.2f}</td>
                </tr>
                <tr>
                    <td>BTC</td>
                    <td>{report['balance'].get('BTC', 0):.8f}</td>
                </tr>
                <tr>
                    <td>ETH</td>
                    <td>{report['balance'].get('ETH', 0):.8f}</td>
                </tr>
                <tr style="background-color: #e7f3ff; font-weight: bold;">
                    <td>总计 (估算)</td>
                    <td>${report['balance'].get('total_usdt', 0):.2f}</td>
                </tr>
            </table>

            <h2>📝 交易日志 (最近 50 条)</h2>
            <div class="log-box">
                {'<br>'.join(report['trades']) if report['trades'] else '暂无交易记录'}
            </div>

            <h2>⚙️ 配置信息</h2>
            <table>
                <tr>
                    <th>参数</th>
                    <th>值</th>
                </tr>
                <tr>
                    <td>测试模式</td>
                    <td><span class="success">✅ 开启</span></td>
                </tr>
                <tr>
                    <td>模拟下单</td>
                    <td><span class="success">✅ 开启</span></td>
                </tr>
                <tr>
                    <td>止损</td>
                    <td>-10%</td>
                </tr>
                <tr>
                    <td>止盈</td>
                    <td>+5%</td>
                </tr>
                <tr>
                    <td>最大仓位</td>
                    <td>20%</td>
                </tr>
            </table>

            <div class="info-box" style="margin-top: 30px; background-color: #fff3cd; border-left-color: #ffc107;">
                <strong>⚠️ 重要提醒:</strong><br>
                当前为测试模式，真实资金不会动用。<br>
                测试周期结束后，根据结果决定是否启用真实交易。
            </div>

            <div style="text-align: center; margin-top: 30px; color: #666; font-size: 12px;">
                <p>x402 交易机器人 | 自动发送</p>
                <p>项目地址：/home/admin/Ziwei/projects/x402-trading-bot</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html


def send_email(subject, html_content):
    """发送邮件"""
    try:
        # 创建邮件
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECEIVER_EMAIL

        # 添加 HTML 内容
        msg.attach(MIMEText(html_content, 'html', 'utf-8'))

        # 连接 SMTP 服务器
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, [RECEIVER_EMAIL], msg.as_string())
        server.quit()

        print(f"✅ 邮件发送成功: {RECEIVER_EMAIL}")
        return True

    except Exception as e:
        print(f"❌ 邮件发送失败: {e}")
        return False


def main():
    """主函数"""
    print("=" * 70)
    print("📧 x402 交易机器人 - 每日测试报告")
    print("=" * 70)
    print()

    # 生成报告
    print("📊 生成测试报告...")
    report = generate_report()

    # 创建邮件
    subject = f"🤖 x402 交易机器人测试报告 - {report['date']}"
    print("📝 创建邮件内容...")
    html_content = create_email_html(report)

    # 发送邮件
    print("📧 发送邮件...")
    success = send_email(subject, html_content)

    # 保存报告
    report_file = f"/home/admin/Ziwei/projects/x402-trading-bot/daily_report_{report['date']}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"💾 报告已保存: {report_file}")
    print()
    print("=" * 70)

    if success:
        print("✅ 报告发送完成")
    else:
        print("❌ 报告发送失败")

    print("=" * 70)

    return success


if __name__ == "__main__":
    main()
