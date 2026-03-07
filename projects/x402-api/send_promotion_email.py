#!/usr/bin/env python3
# =============================================================================
# x402 API 推广邮件发送脚本
# =============================================================================

import smtplib
from email.mime.text import MIMEText
from email.header import Header
import json

# 配置
SMTP_SERVER = "smtp.163.com"
SMTP_PORT = 465
SENDER_EMAIL = "pandac00@163.com"
SENDER_PASSWORD = "UMayTeWFZsFqwv6M"

# 推广邮件内容
SUBJECT = "🚀 x402 API - $0.02/次的 AI 微付费协议（限时免费测试中）"

BODY = """
您好！

我是紫微智控的 AI 助手。很高兴向您介绍我们的 x402 API 项目。

【核心特点】
💰 超低价格 - $0.02/次起（业界最低）
✅ 无需订阅 - 用多少付多少
🌐 全球可用 - 无地域限制
🔒 安全可靠 - 企业级防护

【8 个 AI Agent 端点】
- 翻译 API - $0.02/次
- 代码审计 - $0.05/次
- 逻辑推理 - $0.06/次
- 代码生成 - $0.08/次
- 架构设计 - $0.10/次
- 视觉解析 - $0.15/次
- 长文解析 - $0.03/次
- 网络爬虫 - $0.04/次

【限时免费】
即日起至 2026-03-09，所有 API 免费使用！
欢迎测试体验。

【立即测试】
📚 GitHub: https://github.com/ziwei-control/ziwei-archive
🔌 API 文档：查看 GitHub README
📝 文档：https://github.com/ziwei-control/ziwei-archive/tree/main/projects/x402-api
📚 文档：https://github.com/ziwei-control/ziwei-archive

【技术支持】
如有任何问题，欢迎通过 GitHub Issues 联系我们。

期待与您合作！

此致
敬礼

紫微智控团队
2026-03-07
"""

# 收件人列表（示例）
RECEIVERS = [
    # 添加潜在合作伙伴邮箱
    # "partner1@example.com",
    # "partner2@example.com",
]

def send_email(to_email, subject, body):
    """发送邮件"""
    try:
        msg = MIMEText(body, 'plain', 'utf-8')
        msg['From'] = Header("紫微智控", 'utf-8')
        msg['To'] = Header(to_email, 'utf-8')
        msg['Subject'] = Header(subject, 'utf-8')
        
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, [to_email], msg.as_string())
        server.quit()
        
        print(f"✅ 邮件已发送至：{to_email}")
        return True
    except Exception as e:
        print(f"❌ 发送失败 {to_email}: {e}")
        return False

def main():
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║       x402 API 推广邮件发送                               ║")
    print("╠═══════════════════════════════════════════════════════════╣")
    
    if not RECEIVERS:
        print("⚠️  收件人列表为空")
        print("💡 请编辑脚本添加收件人邮箱")
        print("\n示例：")
        print('RECEIVERS = [')
        print('    "partner@example.com",')
        print('    "developer@example.com",')
        print(']')
        return
    
    print(f"📧 准备发送 {len(RECEIVERS)} 封邮件\n")
    
    success = 0
    failed = 0
    
    for email in RECEIVERS:
        if send_email(email, SUBJECT, BODY):
            success += 1
        else:
            failed += 1
    
    print("\n╠═══════════════════════════════════════════════════════════╣")
    print(f"║  发送完成：成功 {success} 封，失败 {failed} 封                       ║")
    print("╚═══════════════════════════════════════════════════════════╝")

if __name__ == "__main__":
    main()
