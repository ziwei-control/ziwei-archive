#!/usr/bin/env python3
import smtplib
from email.mime.text import MIMEText
from email.header import Header

SMTP_SERVER = "smtp.163.com"
SMTP_PORT = 465
SENDER_EMAIL = "pandac00@163.com"
SENDER_PASSWORD = "UMayTeWFZsFqwv6M"

SUBJECT = "🚀 x402 API - $0.02/次的 AI 微付费协议（限时免费）"

BODY = """
您好！

我是紫微智控的 AI 助手。向您介绍我们的 x402 API 项目。

【核心特点】
💰 超低价格 - $0.02/次起（业界最低）
✅ 无需订阅 - 用多少付多少
🌐 全球可用 - 无地域限制

【8 个 AI Agent 端点】
- 翻译 API - $0.02/次
- 代码审计 - $0.05/次
- 逻辑推理 - $0.06/次
- 代码生成 - $0.08/次
- 架构设计 - $0.10/次

【限时免费】
即日起至 2026-03-09，所有 API 免费使用！

【立即获取 API Key】
🔑 http://8.213.149.224:8090/get-api-key.html
📚 GitHub: https://github.com/ziwei-control/ziwei-archive

紫微智控团队
2026-03-07
"""

# 开发者社区邮箱列表
RECEIVERS = [
    "pandac00@163.com",  # 测试
    # 可以添加更多开发者邮箱
]

def send_email(to_email):
    try:
        msg = MIMEText(BODY, 'plain', 'utf-8')
        msg['From'] = Header("紫微智控", 'utf-8')
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

print("╔═══════════════════════════════════════════════════════════╗")
print("║       x402 API 推广邮件发送                               ║")
print("╠═══════════════════════════════════════════════════════════╣")

success = 0
for email in RECEIVERS:
    print(f"📧 发送至：{email}")
    if send_email(email):
        success += 1
        print(f"   ✅ 成功")
    else:
        print(f"   ❌ 失败")

print(f"\n发送完成：{success}/{len(RECEIVERS)}")
