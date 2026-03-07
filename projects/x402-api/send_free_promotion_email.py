#!/usr/bin/env python3
# =============================================================================
# 免费推广邮件 - 技术文章分享
# =============================================================================

import smtplib
from email.mime.text import MIMEText
from email.header import Header

# 配置
SMTP_SERVER = "smtp.163.com"
SMTP_PORT = 465
SENDER_EMAIL = "pandac00@163.com"
SENDER_PASSWORD = "UMayTeWFZsFqwv6M"

# 文章链接
ARTICLE_URL = "https://github.com/ziwei-control/ziwei-archive/blob/main/projects/x402-api/BLOG_MICROPAYMENT_PROTOCOL.md"

SUBJECT = "技术分享：如何用 Base L2 实现$0.02的 AI API 调用"

BODY = f"""
您好！

紫微智控技术团队发表了一篇深度技术文章，
分享构建 AI API 微支付协议的技术挑战和解决方案。

📄 文章链接：
{ARTICLE_URL}

文章涵盖：
• 微支付经济模型分析（为什么 Stripe 无法支持$0.02 支付）
• 支付验证延迟优化（从 3 秒降到 180ms）
• Bloom 过滤器防重放攻击（1MB 内存支持 10 万交易）
• 无用户认证下的 DDoS 防护
• 区块链重组处理（6 次确认，0.01% 重组风险）

技术栈：
• Python HTTP Server
• USDC on Base Chain
• Bloom Filter + TTL Cache
• 多线程异步验证

所有代码开源，欢迎交流讨论！

紫微智控团队
GitHub: https://github.com/ziwei-control/ziwei-archive
"""

# 收件人列表
RECEIVERS = [
    "pandac00@163.com",  # 测试
]

def send_email(to_email):
    try:
        msg = MIMEText(BODY, 'plain', 'utf-8')
        msg['From'] = Header("紫微智控技术团队", 'utf-8')
        msg['To'] = Header(to_email, 'utf-8')
        msg['Subject'] = Header(SUBJECT, 'utf-8')
        
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, [to_email], msg.as_string())
        server.quit()
        return True
    except Exception as e:
        return False

print("╔═══════════════════════════════════════════════════════════╗")
print("║       免费推广 - 邮件发送                                  ║")
print("╠═══════════════════════════════════════════════════════════╣")
print(f"  文章：Micro-Payment Protocol 技术挑战")
print(f"  链接：{ARTICLE_URL}")
print(f"  收件人：{len(RECEIVERS)}")
print("╚═══════════════════════════════════════════════════════════╝")

success = 0
for email in RECEIVERS:
    print(f"📧 发送至：{email}")
    if send_email(email):
        success += 1
        print(f"   ✅ 成功")

print(f"\n发送完成：{success}/{len(RECEIVERS)}")
