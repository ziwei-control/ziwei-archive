#!/usr/bin/env python3
# =============================================================================
# 全球战情室 - 邮件通知系统 (升级版)
# 功能：发送包含具体来源、证据包、详细分析的邮件到 19922307306@189.cn
# =============================================================================

import smtplib
import json
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# 邮件配置
EMAIL_CONFIG = {
    "smtp_server": "smtp.163.com",
    "smtp_port": 465,
    "sender_email": "pandac00@163.com", 
    "sender_password": "UMayTeWFZsFqwv6M",
    "receiver_email": "19922307306@189.cn"
}

def send_crypto_alert(symbol, current_price, change_percent, volume, sources, evidence_data):
    """
    发送加密货币暴涨暴跌警报（包含具体来源和证据）
    """
    subject = f"【全球战情室】🚨 加密货币暴涨暴跌警报: {symbol} {change_percent:+.1f}%"
    
    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
        <div style="background-color: white; padding: 20px; border-radius: 10px; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #333; border-bottom: 2px solid #dc3545; padding-bottom: 10px;">
                🚨 加密货币暴涨暴跌警报
            </h2>
            
            <div style="margin: 20px 0; background-color: #f8d7da; padding: 15px; border-radius: 5px; border-left: 4px solid #dc3545;">
                <h3>📊 核心数据</h3>
                <ul>
                    <li><strong>代币名称:</strong> {symbol}</li>
                    <li><strong>当前价格:</strong> ${current_price:,.2f}</li>
                    <li><strong>24小时涨跌幅:</strong> {change_percent:+.1f}%</li>
                    <li><strong>交易量:</strong> ${volume}</li>
                </ul>
            </div>
            
            <div style="margin: 20px 0; background-color: #d1ecf1; padding: 15px; border-radius: 5px; border-left: 4px solid #17a2b8;">
                <h3>🔍 数据来源</h3>
                <ul>
    """
    
    for source in sources:
        body += f"<li><strong>• {source['name']}:</strong> {source['url']}</li>\n"
    
    body += """
                </ul>
            </div>
            
            <div style="margin: 20px 0; background-color: #d4edda; padding: 15px; border-radius: 5px; border-left: 4px solid #28a745;">
                <h3>🎯 详细分析</h3>
                <ul>
    """
    
    for key, value in evidence_data.items():
        if key == 'exchange_data':
            body += f"<li><strong>交易所跟涨情况:</strong><br>{value}</li>\n"
        elif key == 'chain_analysis':
            body += f"<li><strong>链上大额转账记录:</strong><br>{value}</li>\n"
        elif key == 'project_news':
            body += f"<li><strong>项目方最新动态:</strong><br>{value}</li>\n"
        elif key == 'technical_analysis':
            body += f"<li><strong>技术分析:</strong><br>{value}</li>\n"
    
    body += f"""
                </ul>
            </div>
            
            <div style="margin: 20px 0; padding: 15px; background-color: #fff3cd; border-radius: 5px; border-left: 4px solid #ffc107;">
                <strong>⏰ 警报时间:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                <br><strong>📧 接收邮箱:</strong> {EMAIL_CONFIG['receiver_email']}
                <br><strong>⚠️ 风险提示:</strong> 请结合自身风险承受能力谨慎决策
            </div>
            
            <div style="text-align: center; margin-top: 20px; color: #666; font-size: 12px;">
                <p>全球战情室 - 24小时自动监控 | 紫微智控系统</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email(subject, body)

def send_social_trend_alert(topic, mentions, sentiment, evidence_posts, sources):
    """
    发送社交媒体热点警报（包含具体推文和证据）
    """
    subject = f"【全球战情室】🔥 社交媒体热点: {topic}"
    
    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
        <div style="background-color: white; padding: 20px; border-radius: 10px; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #333; border-bottom: 2px solid #fd7e14; padding-bottom: 10px;">
                🔥 社交媒体热点警报
            </h2>
            
            <div style="margin: 20px 0; background-color: #fff3cd; padding: 15px; border-radius: 5px; border-left: 4px solid #ffc107;">
                <h3>📊 热点概览</h3>
                <ul>
                    <li><strong>热点话题:</strong> {topic}</li>
                    <li><strong>提及次数:</strong> {mentions:,}+</li>
                    <li><strong>情绪倾向:</strong> {sentiment}</li>
                    <li><strong>监测平台:</strong> Twitter, Reddit, 雪球, 东方财富股吧</li>
                </ul>
            </div>
            
            <div style="margin: 20px 0; background-color: #d1ecf1; padding: 15px; border-radius: 5px; border-left: 4px solid #17a2b8;">
                <h3>🔍 具体证据包</h3>
    """
    
    for i, post in enumerate(evidence_posts[:3]):  # 显示前3个热门帖子
        body += f"""
                <div style="margin: 10px 0; padding: 10px; background-color: #e9ecef; border-radius: 5px;">
                    <strong>帖子 #{i+1}:</strong><br>
                    <strong>用户:</strong> {post.get('user_id', 'Unknown')}<br>
                    <strong>平台:</strong> {post.get('platform', 'Unknown')}<br>
                    <strong>发布时间:</strong> {post.get('timestamp', 'Unknown')}<br>
                    <strong>内容:</strong> {post.get('content', 'Content not available')}<br>
                    <strong>原文链接:</strong> <a href="{post.get('url', '#')}" target="_blank">{post.get('url', 'Link not available')}</a>
                </div>
        """
    
    body += """
            </div>
            
            <div style="margin: 20px 0; background-color: #f8d7da; padding: 15px; border-radius: 5px; border-left: 4px solid #dc3545;">
                <h3>📈 潜在影响</h3>
                <ul>
                    <li><strong>关联代币:</strong> 此热点可能影响相关代币价格</li>
                    <li><strong>建议操作:</strong> 密切关注相关资产价格变动</li>
                    <li><strong>风险等级:</strong> 中等 - 需要持续监控</li>
                </ul>
            </div>
            
            <div style="margin: 20px 0; padding: 15px; background-color: #e2e3e5; border-radius: 5px; border-left: 4px solid #6c757d;">
                <strong>⏰ 警报时间:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                <br><strong>📧 接收邮箱:</strong> {EMAIL_CONFIG['receiver_email']}
            </div>
            
            <div style="text-align: center; margin-top: 20px; color: #666; font-size: 12px;">
                <p>全球战情室 - 24小时自动监控 | 紫微智控系统</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email(subject, body)

def send_stock_ipo_alert(stock_name, stock_code, issue_price, expected_gain, underwriters, business_summary, sources):
    """
    发送新股上市警报（包含招股书摘要和来源）
    """
    subject = f"【全球战情室】🆕 新股上市机会: {stock_name} ({stock_code})"
    
    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
        <div style="background-color: white; padding: 20px; border-radius: 10px; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #333; border-bottom: 2px solid #28a745; padding-bottom: 10px;">
                🆕 新股上市机会
            </h2>
            
            <div style="margin: 20px 0; background-color: #d4edda; padding: 15px; border-radius: 5px; border-left: 4px solid #28a745;">
                <h3>📊 基本信息</h3>
                <ul>
                    <li><strong>公司名称:</strong> {stock_name}</li>
                    <li><strong>股票代码:</strong> {stock_code}</li>
                    <li><strong>发行价区间:</strong> ${issue_price}</li>
                    <li><strong>预期收益:</strong> {expected_gain}</li>
                    <li><strong>上市日期:</strong> {datetime.now().strftime('%Y-%m-%d')}</li>
                </ul>
            </div>
            
            <div style="margin: 20px 0; background-color: #d1ecf1; padding: 15px; border-radius: 5px; border-left: 4px solid #17a2b8;">
                <h3>🏢 主承销商</h3>
                <ul>
    """
    
    for underwriter in underwriters:
        body += f"<li>{underwriter}</li>\n"
    
    body += """
                </ul>
            </div>
            
            <div style="margin: 20px 0; background-color: #fff3cd; padding: 15px; border-radius: 5px; border-left: 4px solid #ffc107;">
                <h3>💼 核心业务拆解</h3>
                <p>{business_summary}</p>
            </div>
            
            <div style="margin: 20px 0; background-color: #f8d7da; padding: 15px; border-radius: 5px; border-left: 4px solid #dc3545;">
                <h3>📚 数据来源</h3>
                <ul>
    """
    
    for source in sources:
        body += f"<li><strong>• {source['name']}:</strong> {source['reference']}</li>\n"
    
    body += f"""
                </ul>
            </div>
            
            <div style="margin: 20px 0; padding: 15px; background-color: #e2e3e5; border-radius: 5px; border-left: 4px solid #6c757d;">
                <strong>⏰ 警报时间:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                <br><strong>📧 接收邮箱:</strong> {EMAIL_CONFIG['receiver_email']}
                <br><strong>⚠️ 风险提示:</strong> 新股投资存在破发风险，请谨慎决策
            </div>
            
            <div style="text-align: center; margin-top: 20px; color: #666; font-size: 12px;">
                <p>全球战情室 - 24小时自动监控 | 紫微智控系统</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email(subject, body)

def send_email(subject, body):
    """发送邮件"""
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_CONFIG["sender_email"]
        msg['To'] = EMAIL_CONFIG["receiver_email"] 
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'html', 'utf-8'))
        
        server = smtplib.SMTP_SSL(EMAIL_CONFIG["smtp_server"], EMAIL_CONFIG["smtp_port"])
        server.login(EMAIL_CONFIG["sender_email"], EMAIL_CONFIG["sender_password"])
        text = msg.as_string()
        server.sendmail(EMAIL_CONFIG["sender_email"], EMAIL_CONFIG["receiver_email"], text)
        server.quit()
        
        print(f"[{datetime.now()}] ✅ 邮件发送成功: {subject}")
        return True
        
    except Exception as e:
        print(f"[{datetime.now()}] ❌ 邮件发送失败: {str(e)}")
        return False

def test_detailed_emails():
    """测试详细的邮件内容"""
    print("🧪 测试详细邮件内容...")
    
    # 测试加密货币警报
    crypto_sources = [
        {"name": "Binance", "url": "https://www.binance.com/en/trade/BTC_USDT"},
        {"name": "CoinGecko", "url": "https://www.coingecko.com/en/coins/bitcoin"},
        {"name": "OKX", "url": "https://www.okx.com/trade-spot/btc-usdt"}
    ]
    
    crypto_evidence = {
        "exchange_data": "Binance: +35.2%, OKX: +36.1%, Bybit: +34.8% - 所有主流交易所同步上涨",
        "chain_analysis": "链上大额转账: 0x742d... → 0x8a3f... (500 BTC), 0x9c1e... → 0x2b4d... (300 BTC)",
        "project_news": "比特币ETF获批消息推动市场情绪，机构资金大量流入",
        "technical_analysis": "突破60000美元关键阻力位，RSI进入超买区域但未出现背离"
    }
    
    success1 = send_crypto_alert("BTC", 62500.00, 35.5, "25.8B", crypto_sources, crypto_evidence)
    
    # 测试社交媒体热点
    social_posts = [
        {
            "user_id": "@CryptoWhale",
            "platform": "Twitter",
            "timestamp": "2026-03-01 20:30:00",
            "content": "Just bought $5M worth of $BTC! ETF approval is just the beginning! 🚀",
            "url": "https://twitter.com/CryptoWhale/status/1234567890"
        },
        {
            "user_id": "u/BitcoinBull",
            "platform": "Reddit",
            "timestamp": "2026-03-01 20:25:00",
            "content": "This is the biggest bull run ever! Price target: $100K by end of year!",
            "url": "https://reddit.com/r/Bitcoin/comments/abc123"
        }
    ]
    
    social_sources = [
        {"name": "Twitter Trending", "url": "https://twitter.com/explore/tabs/trending"},
        {"name": "Reddit r/Bitcoin", "url": "https://reddit.com/r/Bitcoin"}
    ]
    
    success2 = send_social_trend_alert("Bitcoin ETF Approval", 15000, "极度看涨", social_posts, social_sources)
    
    # 测试新股上市
    ipo_underwriters = ["高盛", "摩根士丹利", "中金公司"]
    ipo_business = "AI科技公司专注于大模型训练和推理优化，拥有自主知识产权的AI芯片，客户包括腾讯、阿里等头部互联网公司。2025年营收增长150%，净利润率25%。"
    ipo_sources = [
        {"name": "港交所披露易", "reference": "文件第23页，招股说明书"},
        {"name": "中国证券报", "reference": "2026-03-01 深度报道"}
    ]
    
    success3 = send_stock_ipo_alert("AI科技", "688999.SH", "25.00", "15-20%", ipo_underwriters, ipo_business, ipo_sources)
    
    if success1 and success2 and success3:
        print("✅ 详细邮件测试通过！")
    else:
        print("❌ 详细邮件测试失败！")
    
    return success1 and success2 and success3

if __name__ == "__main__":
    test_detailed_emails()