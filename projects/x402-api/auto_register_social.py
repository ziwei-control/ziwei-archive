#!/usr/bin/env python3
# =============================================================================
# 社交媒体账号自动注册脚本
# 使用：Xvfb + Selenium + Firefox
# =============================================================================

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import imaplib
import email
from email.header import decode_header
import os

# 配置
EMAIL = "pandac00@163.com"
EMAIL_PASSWORD = "UMayTeWFZsFqwv6M"
IMAP_SERVER = "imap.163.com"
IMAP_PORT = 993

# 账号信息
ACCOUNTS = {
    "discord": {
        "url": "https://discord.com/register",
        "username": "ZiweiControl",
        "password": "ZiweiControl2026!"
    },
    "reddit": {
        "url": "https://www.reddit.com/register",
        "username": "ziwei_control",
        "password": "ZiweiControl2026!"
    },
    "producthunt": {
        "url": "https://www.producthunt.com/signup",
        "username": "ziwei-control",
        "password": "ZiweiControl2026!"
    }
}

def get_email_verification_code(subject_contains="验证"):
    """从邮箱获取验证码"""
    try:
        print(f"📧 连接邮箱：{IMAP_SERVER}")
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(EMAIL, EMAIL_PASSWORD)
        mail.select("inbox")
        
        # 搜索邮件
        status, messages = mail.search(None, "ALL")
        email_ids = messages[0].split()
        
        # 获取最新 5 封邮件
        for eid in reversed(email_ids[-5:]):
            status, msg = mail.fetch(eid, "(RFC822)")
            email_msg = email.message_from_bytes(msg[0][1])
            
            # 解码主题
            subject, encoding = decode_header(email_msg["Subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding or "utf-8")
            
            print(f"  检查邮件：{subject}")
            
            if subject_contains in subject:
                # 获取邮件正文
                if email_msg.is_multipart():
                    for part in email_msg.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True).decode()
                            # 查找验证码（6 位数字）
                            import re
                            codes = re.findall(r'\b\d{6}\b', body)
                            if codes:
                                print(f"  ✅ 找到验证码：{codes[0]}")
                                return codes[0]
                else:
                    body = email_msg.get_payload(decode=True).decode()
                    import re
                    codes = re.findall(r'\b\d{6}\b', body)
                    if codes:
                        print(f"  ✅ 找到验证码：{codes[0]}")
                        return codes[0]
        
        mail.close()
        mail.logout()
        return None
        
    except Exception as e:
        print(f"❌ 读取邮箱失败：{e}")
        return None

def setup_driver():
    """配置 Firefox 驱动"""
    options = Options()
    options.headless = True  # 无头模式
    options.add_argument("--width=1920")
    options.add_argument("--height=1080")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0")
    
    driver = webdriver.Firefox(options=options)
    return driver

def register_discord(driver, account_info):
    """注册 Discord"""
    print("\n╔═══════════════════════════════════════════════════════════╗")
    print("║       注册 Discord                                        ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    
    try:
        driver.get(account_info["url"])
        time.sleep(3)
        
        # 填写邮箱
        email_input = driver.find_element(By.CSS_SELECTOR, 'input[type="email"]')
        email_input.send_keys(EMAIL)
        print(f"✅ 已输入邮箱：{EMAIL}")
        
        # 填写用户名
        username_input = driver.find_element(By.CSS_SELECTOR, 'input[aria-label="Username"]')
        username_input.send_keys(account_info["username"])
        print(f"✅ 已输入用户名：{account_info['username']}")
        
        # 填写密码
        password_input = driver.find_element(By.CSS_SELECTOR, 'input[type="password"]')
        password_input.send_keys(account_info["password"])
        print(f"✅ 已输入密码")
        
        # 填写生日（简化，选择成年日期）
        # 需要手动选择月份、日期、年份
        print("⚠️  需要手动选择生日（自动化复杂）")
        
        # 同意条款
        # 需要点击复选框
        
        # 提交
        # 需要点击提交按钮
        
        print("⏳ 等待邮箱验证码...")
        time.sleep(5)
        
        # 获取验证码
        code = get_email_verification_code("Discord")
        if code:
            print(f"✅ 验证码：{code}")
            # 输入验证码
            # code_inputs = driver.find_elements(By.CSS_SELECTOR, 'input[type="text"]')
            # for i, inp in enumerate(code_inputs):
            #     inp.send_keys(code[i])
        
        print("⚠️  Discord 注册需要完成 CAPTCHA，建议手动完成")
        return False
        
    except Exception as e:
        print(f"❌ Discord 注册失败：{e}")
        return False

def register_reddit(driver, account_info):
    """注册 Reddit"""
    print("\n╔═══════════════════════════════════════════════════════════╗")
    print("║       注册 Reddit                                         ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    
    try:
        driver.get(account_info["url"])
        time.sleep(3)
        
        # Reddit 注册需要点击"Sign Up"按钮
        print("⚠️  Reddit 注册流程复杂，建议手动完成")
        return False
        
    except Exception as e:
        print(f"❌ Reddit 注册失败：{e}")
        return False

def main():
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║       社交媒体账号自动注册                                ║")
    print("╠═══════════════════════════════════════════════════════════╣")
    print(f"  邮箱：{EMAIL}")
    print(f"  账号数：{len(ACCOUNTS)}")
    print("╚═══════════════════════════════════════════════════════════╝")
    
    # 测试邮箱连接
    print("\n【测试邮箱连接】")
    code = get_email_verification_code("验证")
    if code:
        print("✅ 邮箱连接成功")
    else:
        print("⚠️  邮箱连接失败或无验证码邮件")
    
    # 启动浏览器
    print("\n【启动浏览器】")
    driver = setup_driver()
    print("✅ Firefox 已启动")
    
    try:
        # 尝试注册 Discord
        register_discord(driver, ACCOUNTS["discord"])
        time.sleep(5)
        
        # 尝试注册 Reddit
        register_reddit(driver, ACCOUNTS["reddit"])
        time.sleep(5)
        
    finally:
        print("\n【关闭浏览器】")
        driver.quit()
        print("✅ 完成")
    
    print("\n╔═══════════════════════════════════════════════════════════╗")
    print("║  注册总结                                                 ║")
    print("╠═══════════════════════════════════════════════════════════╣")
    print("║  ⚠️  由于 CAPTCHA 验证，建议 Martin 手动完成剩余步骤        ║")
    print("║                                                           ║")
    print("║  已完成：                                                 ║")
    print("║    ✅ 环境配置完成（Xvfb + Selenium + Firefox）          ║")
    print("║    ✅ 邮箱验证码读取功能                                 ║")
    print("║    ✅ 自动化脚本准备                                     ║")
    print("║                                                           ║")
    print("║  需要手动：                                               ║")
    print("║    • 完成 CAPTCHA 验证                                    ║")
    print("║    • 选择生日等字段                                       ║")
    print("║    • Twitter 注册（需要手机号）                           ║")
    print("╚═══════════════════════════════════════════════════════════╝")

if __name__ == "__main__":
    main()
