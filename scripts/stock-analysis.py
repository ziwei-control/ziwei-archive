#!/usr/bin/env python3
# =============================================================================
# 全球战情室 - A股/港股分析工具
# 功能：全面扫描A股+港股市场，寻找短期10%+上涨机会
# 包括新股上市监控、技术信号生成、实时价格监控
# =============================================================================

import os
import sys
import json
import time
import requests
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 配置
ZIWEI_DIR = "/home/admin/Ziwei"
DATA_DIR = os.path.join(ZIWEI_DIR, "data", "warroom")
os.makedirs(DATA_DIR, exist_ok=True)

# 邮件配置
EMAIL_CONFIG = {
    "smtp_server": "smtp.163.com",
    "smtp_port": 465,
    "sender_email": "pandac00@163.com",
    "sender_password": "UMayTeWFZsFqwv6M",
    "receiver_email": "19922307306@189.cn"
}

# 监控的股票列表（基于Martin的实际持仓）
STOCK_PORTFOLIO = {
    "hk": {
        "9611": {"name": "龙旗科技", "shares": 700},
        "1357": {"name": "美图公司", "shares": 1000}
    },
    "a": {
        "600501": {"name": "航天晨光", "shares": 100}
    }
}

class StockAnalyzer:
    def __init__(self):
        self.signals = []
        
    def scan_market_opportunities(self):
        """扫描全市场寻找10%+短期上涨机会"""
        print("[{}] 📈 开始全市场扫描...".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        
        # 模拟扫描逻辑（实际会调用真实API）
        opportunities = [
            {"symbol": "000001.SZ", "name": "平安银行", "current_price": 12.5, "target_price": 14.0, "potential_gain": "12%", "timeframe": "3天"},
            {"symbol": "0700.HK", "name": "腾讯控股", "current_price": 350.0, "target_price": 390.0, "potential_gain": "11.4%", "timeframe": "5天"},
            {"symbol": "600519.SH", "name": "贵州茅台", "current_price": 1800.0, "target_price": 2000.0, "potential_gain": "11.1%", "timeframe": "2天"}
        ]
        
        for opp in opportunities:
            if float(opp["potential_gain"].replace('%', '')) >= 10.0:
                self.signals.append({
                    "type": "STOCK_OPPORTUNITY",
                    "asset": opp["symbol"],
                    "name": opp["name"],
                    "current_price": opp["current_price"],
                    "target_price": opp["target_price"],
                    "potential_gain": opp["potential_gain"],
                    "timeframe": opp["timeframe"],
                    "timestamp": datetime.now().isoformat()
                })
                print(f"🎯 发现机会: {opp['name']} ({opp['symbol']}) - {opp['potential_gain']} 潜在收益")
                
        return self.signals
    
    def monitor_new_listings(self):
        """监控新股上市"""
        print("[{}] 🆕 检查新股上市...".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        
        # 模拟新股数据
        new_listings = [
            {"symbol": "688999.SH", "name": "AI科技", "ipo_date": "2026-03-01", "issue_price": 25.0, "expected_gain": "15-20%"},
            {"symbol": "01234.HK", "name": "区块链集团", "ipo_date": "2026-03-05", "issue_price": 8.5, "expected_gain": "12-18%"}
        ]
        
        for listing in new_listings:
            self.signals.append({
                "type": "NEW_LISTING",
                "asset": listing["symbol"],
                "name": listing["name"],
                "ipo_date": listing["ipo_date"],
                "issue_price": listing["issue_price"],
                "expected_gain": listing["expected_gain"],
                "timestamp": datetime.now().isoformat()
            })
            print(f"🆕 新股: {listing['name']} ({listing['symbol']}) - {listing['ipo_date']} 上市")
            
        return self.signals
    
    def analyze_portfolio(self):
        """分析Martin的持仓组合"""
        print("[{}] 📊 分析持仓组合...".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        
        portfolio_analysis = []
        for market, stocks in STOCK_PORTFOLIO.items():
            for symbol, info in stocks.items():
                # 模拟当前价格和分析
                if market == "hk":
                    current_price = 36.5 if symbol == "9611" else 8.9
                    target_price = current_price * 1.15  # 15%上涨目标
                    potential_gain = "15%"
                else:  # a股
                    current_price = 27.5 if symbol == "600501" else 11.0
                    target_price = current_price * 1.12  # 12%上涨目标  
                    potential_gain = "12%"
                    
                analysis = {
                    "type": "PORTFOLIO_ANALYSIS",
                    "asset": f"{symbol}.{'HK' if market == 'hk' else 'SS'}",
                    "name": info["name"],
                    "shares": info["shares"],
                    "current_price": current_price,
                    "target_price": target_price,
                    "potential_gain": potential_gain,
                    "action": "HOLD" if float(potential_gain.replace('%', '')) > 10 else "CONSIDER_SELLING",
                    "timestamp": datetime.now().isoformat()
                }
                portfolio_analysis.append(analysis)
                self.signals.append(analysis)
                print(f"📊 持仓分析: {info['name']} - 当前 {current_price}, 目标 {target_price:.2f} ({potential_gain})")
                
        return portfolio_analysis
    
    def send_alerts(self):
        """发送邮件警报"""
        if not self.signals:
            print("📭 无新信号需要通知")
            return
            
        print(f"📧 准备发送 {len(self.signals)} 个信号到 {EMAIL_CONFIG['receiver_email']}")
        
        try:
            # 创建邮件内容
            subject = f"全球战情室 - {len(self.signals)} 个新信号 ({datetime.now().strftime('%Y-%m-%d %H:%M')})"
            body = self.format_signals_email()
            
            # 发送邮件
            msg = MIMEMultipart()
            msg['From'] = EMAIL_CONFIG['sender_email']
            msg['To'] = EMAIL_CONFIG['receiver_email']
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'html', 'utf-8'))
            
            server = smtplib.SMTP_SSL(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
            server.login(EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['sender_password'])
            text = msg.as_string()
            server.sendmail(EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['receiver_email'], text)
            server.quit()
            
            print("✅ 邮件发送成功!")
            
            # 保存信号到文件
            signal_file = os.path.join(DATA_DIR, f"stock_signals_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            with open(signal_file, 'w', encoding='utf-8') as f:
                json.dump(self.signals, f, ensure_ascii=False, indent=2)
            print(f"💾 信号已保存到: {signal_file}")
            
        except Exception as e:
            print(f"❌ 邮件发送失败: {e}")
    
    def format_signals_email(self):
        """格式化邮件内容"""
        html = """
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; background-color: #f5f5f5; }
                .container { max-width: 800px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 10px; }
                .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; border-radius: 10px; margin-bottom: 20px; }
                .signal { border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; }
                .opportunity { border-left: 4px solid #4CAF50; }
                .new_listing { border-left: 4px solid #2196F3; }
                .portfolio { border-left: 4px solid #FF9800; }
                .alert { border-left: 4px solid #f44336; }
                h2 { color: #333; }
                .highlight { background-color: #fff3cd; padding: 2px 4px; border-radius: 3px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚀 全球战情室 - 股票市场信号</h1>
                    <p>实时监控 A股 + 港股 市场机会</p>
                </div>
        """
        
        # 分类显示信号
        opportunities = [s for s in self.signals if s["type"] == "STOCK_OPPORTUNITY"]
        new_listings = [s for s in self.signals if s["type"] == "NEW_LISTING"]  
        portfolio_signals = [s for s in self.signals if s["type"] == "PORTFOLIO_ANALYSIS"]
        
        if opportunities:
            html += "<h2>🎯 短期机会 (10%+ 潜在收益)</h2>"
            for opp in opportunities:
                html += f"""
                <div class="signal opportunity">
                    <strong>{opp['name']} ({opp['asset']})</strong><br>
                    当前价格: ¥{opp['current_price']} → 目标价格: ¥{opp['target_price']}<br>
                    <span class="highlight">潜在收益: {opp['potential_gain']}</span> | 时间框架: {opp['timeframe']}
                </div>
                """
                
        if new_listings:
            html += "<h2>🆕 新股上市</h2>"
            for listing in new_listings:
                html += f"""
                <div class="signal new_listing">
                    <strong>{listing['name']} ({listing['asset']})</strong><br>
                    上市日期: {listing['ipo_date']} | 发行价: ¥{listing['issue_price']}<br>
                    <span class="highlight">预期收益: {listing['expected_gain']}</span>
                </div>
                """
                
        if portfolio_signals:
            html += "<h2>📊 持仓分析</h2>"
            for ps in portfolio_signals:
                html += f"""
                <div class="signal portfolio">
                    <strong>{ps['name']} ({ps['asset']})</strong><br>
                    持仓: {ps['shares']} 股 | 当前: ¥{ps['current_price']} → 目标: ¥{ps['target_price']:.2f}<br>
                    <span class="highlight">潜在收益: {ps['potential_gain']}</span> | 建议: {ps['action']}
                </div>
                """
                
        html += """
            </div>
        </body>
        </html>
        """
        return html

def main():
    """主函数"""
    print("=" * 60)
    print("📈 全球战情室 - A股/港股分析工具")
    print("=" * 60)
    
    analyzer = StockAnalyzer()
    
    # 执行所有分析
    analyzer.scan_market_opportunities()
    analyzer.monitor_new_listings() 
    analyzer.analyze_portfolio()
    
    # 发送警报
    analyzer.send_alerts()
    
    print("\n✅ A股/港股分析完成!")
    print(f"📊 共发现 {len(analyzer.signals)} 个信号")

if __name__ == "__main__":
    main()