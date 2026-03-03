#!/usr/bin/env python3
# =============================================================================
# 邮件告警系统配置
# =============================================================================

import os
import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from pathlib import Path

# 配置
EMAIL_CONFIG = {
    "smtp_server": "smtp.163.com",
    "smtp_port": 465,
    "sender_email": "pandac00@163.com",
    "sender_password": os.getenv("SENDER_PASSWORD", "UMayTeWFZsFqwv6M"),
    "receiver_email": "19922307306@189.cn",  # 康纳
    "alert_email": "pandac00@163.com",  # 告警接收邮箱
}

SECURITY_DIR = Path("/home/admin/Ziwei/data/security")
SECURITY_DIR.mkdir(parents=True, exist_ok=True)


class EmailAlerter:
    """邮件告警器"""
    
    def __init__(self, config=None):
        self.config = config or EMAIL_CONFIG
        self.last_alert_time = 0
        self.alert_cooldown = 300  # 告警冷却时间 (5 分钟)
    
    def send_alert(self, subject, content, alert_type="security"):
        """发送告警邮件"""
        try:
            # 检查冷却时间
            now = __import__('time').time()
            if now - self.last_alert_time < self.alert_cooldown:
                print(f"⏳ 告警冷却中，跳过发送")
                return False
            
            # 创建邮件
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"🚨 [{alert_type.upper()}] {subject}"
            msg['From'] = self.config["sender_email"]
            msg['To'] = self.config["alert_email"]
            
            # 邮件内容
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
                <div style="background-color: white; padding: 20px; border-radius: 10px; max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #dc3545; border-bottom: 2px solid #dc3545; padding-bottom: 10px;">
                        🚨 安全告警
                    </h2>
                    
                    <div style="margin: 20px 0; padding: 15px; background-color: #fff3cd; border-left: 4px solid #ffc107;">
                        <h3>告警类型：{alert_type.upper()}</h3>
                        <p><strong>时间:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                        <p><strong>主题:</strong> {subject}</p>
                    </div>
                    
                    <div style="margin: 20px 0; padding: 15px; background-color: #f8f9fa; border-radius: 5px;">
                        <h3>详细内容:</h3>
                        <pre style="background-color: #f1f1f1; padding: 10px; border-radius: 5px; overflow-x: auto;">{content}</pre>
                    </div>
                    
                    <div style="margin: 20px 0; padding: 15px; background-color: #e7f3ff; border-left: 4px solid #007bff;">
                        <h3>建议操作:</h3>
                        <ul>
                            <li>检查安全监控面板</li>
                            <li>查看攻击日志</li>
                            <li>必要时封禁 IP</li>
                            <li>导出安全报告</li>
                        </ul>
                    </div>
                    
                    <div style="text-align: center; margin-top: 20px; color: #666; font-size: 12px;">
                        <p>紫微智控安全系统 | 自动发送</p>
                        <p>不要回复此邮件</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(html_content, 'html', 'utf-8'))
            
            # 发送邮件
            server = smtplib.SMTP_SSL(self.config["smtp_server"], self.config["smtp_port"])
            server.login(self.config["sender_email"], self.config["sender_password"])
            server.sendmail(self.config["sender_email"], [self.config["alert_email"]], msg.as_string())
            server.quit()
            
            # 记录发送时间
            self.last_alert_time = now
            
            # 记录日志
            self.log_alert(subject, alert_type)
            
            print(f"✅ 告警邮件已发送：{subject}")
            return True
            
        except Exception as e:
            print(f"❌ 邮件发送失败：{e}")
            self.log_alert(subject, alert_type, str(e))
            return False
    
    def log_alert(self, subject, alert_type, error=None):
        """记录告警日志"""
        alert_log = {
            "timestamp": datetime.now().isoformat(),
            "subject": subject,
            "type": alert_type,
            "status": "failed" if error else "sent",
            "error": error,
        }
        
        log_file = SECURITY_DIR / "email_alert_log.json"
        try:
            alerts = []
            if log_file.exists():
                with open(log_file, "r") as f:
                    alerts = json.load(f)
            alerts.append(alert_log)
            
            # 只保留最近 100 条
            alerts = alerts[-100:]
            
            with open(log_file, "w") as f:
                json.dump(alerts, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ 记录告警日志失败：{e}")
    
    def send_attack_alert(self, ip, attack_type, attack_count):
        """发送攻击告警"""
        subject = f"检测到攻击 - {ip}"
        content = f"""
攻击 IP: {ip}
攻击类型：{attack_type}
攻击次数：{attack_count}
触发阈值：10 次
状态：已自动封禁

详细攻击日志请查看安全监控面板。
        """
        return self.send_alert(subject, content, "attack")
    
    def send_ddos_alert(self, ip, requests_per_second):
        """发送 DDoS 告警"""
        subject = f"DDoS 攻击检测 - {ip}"
        content = f"""
攻击 IP: {ip}
请求频率：{requests_per_second} 次/秒
阈值：100 次/秒
状态：已自动封禁 1 小时

建议:
1. 检查是否为误报
2. 考虑加入永久黑名单
3. 查看其他攻击来源
        """
        return self.send_alert(subject, content, "ddos")
    
    def send_daily_report(self, stats):
        """发送每日安全报告"""
        subject = f"每日安全报告 - {datetime.now().strftime('%Y-%m-%d')}"
        content = f"""
日期：{datetime.now().strftime('%Y-%m-%d')}

安全统计:
- 总 IP 数：{stats.get('total_ips', 0)}
- 当前封禁：{stats.get('blocked_ips', 0)}
- 黑名单 IP: {stats.get('blacklisted_ips', 0)}
- 总攻击数：{stats.get('total_attacks', 0)}
- 最近 1 小时攻击：{stats.get('attacks_last_hour', 0)}
- 最近 1 小时请求：{stats.get('total_requests_last_hour', 0)}
- 告警次数：{stats.get('alerts', 0)}

建议操作:
1. 查看安全监控面板
2. 检查攻击日志
3. 清理过期日志
4. 导出安全报告
        """
        return self.send_alert(subject, content, "daily_report")


# 全局告警器实例
email_alerter = EmailAlerter()


# 测试函数
def test_email_alert():
    """测试邮件告警"""
    print("=" * 70)
    print("📧 测试邮件告警系统")
    print("=" * 70)
    print()
    
    # 测试 1: 普通告警
    print("测试 1: 发送普通告警...")
    result = email_alerter.send_alert(
        subject="测试告警",
        content="这是一封测试邮件，如果收到说明邮件系统正常工作。",
        alert_type="test"
    )
    print(f"结果：{'✅ 成功' if result else '❌ 失败'}")
    print()
    
    # 测试 2: 攻击告警
    print("测试 2: 发送攻击告警...")
    result = email_alerter.send_attack_alert(
        ip="192.168.1.100",
        attack_type="sql_injection",
        attack_count=10
    )
    print(f"结果：{'✅ 成功' if result else '❌ 失败'}")
    print()
    
    # 测试 3: DDoS 告警
    print("测试 3: 发送 DDoS 告警...")
    result = email_alerter.send_ddos_alert(
        ip="10.0.0.100",
        requests_per_second=150
    )
    print(f"结果：{'✅ 成功' if result else '❌ 失败'}")
    print()
    
    # 查看告警日志
    print("📋 告警日志:")
    log_file = SECURITY_DIR / "email_alert_log.json"
    if log_file.exists():
        with open(log_file, "r") as f:
            alerts = json.load(f)
        for alert in alerts[-5:]:
            print(f"  {alert['timestamp'][:19]} | {alert['type']:15s} | {alert['status']}")
    else:
        print("  无告警记录")
    print()
    
    print("=" * 70)
    print("✅ 邮件告警测试完成")
    print("=" * 70)


if __name__ == "__main__":
    test_email_alert()
