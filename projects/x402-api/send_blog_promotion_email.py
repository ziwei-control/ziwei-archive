#!/usr/bin/env python3
# =============================================================================
# 技术文章推广邮件发送脚本
# 文章：Micro-Payment Protocol 技术挑战
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

# 邮件内容
SUBJECT = "技术分享：微支付协议的技术挑战与解决方案"

BODY = f"""
您好！

我是紫微智控的技术团队。我们最近发表了一篇技术文章，
分享了构建 AI API 微支付协议时遇到的技术挑战和解决方案。

📄 文章链接：
{ARTICLE_URL}

文章涵盖：
• 微支付的经济模型分析（为什么 Stripe/PayPal 无法支持$0.02 支付）
• 支付验证延迟优化（从 3 秒降到 180ms 的实现）
• 防止重放攻击的 Bloom 过滤器实现（1MB 内存支持 10 万交易）
• 无用户认证下的 DDoS 防护（IP 多维度限流）
• 区块链重组处理（6 次确认，0.01% 重组风险）

所有代码开源，欢迎交流讨论！

技术栈：
• Python HTTP Server
• USDC on Base Chain
• Bloom Filter + TTL Cache
• 多线程异步验证

紫微智控团队
GitHub: https://github.com/ziwei-control/ziwei-archive
"""

# 收件人列表（示例）
RECEIVERS = [
    # 开发者社区
    # "python-china@example.com",
    # "blockchain-dev@example.com",
    
    # 测试邮箱
    "pandac00@163.com",
]

def send_email(to_email):
    """发送邮件"""
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
        print(f"❌ {to_email}: {e}")
        return False

def main():
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║       技术文章推广邮件发送                                ║")
    print("╠═══════════════════════════════════════════════════════════╣")
    print(f"  文章：Micro-Payment Protocol 技术挑战")
    print(f"  链接：{ARTICLE_URL}")
    print(f"  收件人：{len(RECEIVERS)}")
    print("╚═══════════════════════════════════════════════════════════╝")
    print()
    
    success = 0
    for email in RECEIVERS:
        print(f"📧 发送至：{email}")
        if send_email(email):
            success += 1
            print(f"   ✅ 成功")
        else:
            print(f"   ❌ 失败")
    
    print()
    print(f"发送完成：{success}/{len(RECEIVERS)}")

if __name__ == "__main__":
    main()
