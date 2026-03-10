#!/usr/bin/env python3
# =============================================================================
# 简化版注册脚本 - 配合 CAPTCHA 网页使用
# =============================================================================

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
import time
import base64
import requests

EMAIL = "pandac00@163.com"
PASSWORD = "ZiweiControl2026!"
CAPTCHA_SERVER = "http://localhost:7676"

ACCOUNTS = [
    {"name": "Discord", "url": "https://discord.com/register", "username": "ZiweiControl"},
    {"name": "Reddit", "url": "https://www.reddit.com/register", "username": "ziwei_control"},
    {"name": "Product Hunt", "url": "https://www.producthunt.com/signup", "username": "ziwei-control"},
    {"name": "Indie Hackers", "url": "https://www.indiehackers.com/sign-up", "username": "ziwei-control"}
]

def setup_driver():
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options)
    return driver

def wait_for_captcha(driver, site_name):
    """截图并等待 Martin 点击"""
    print(f"  ⏳ 截取 {site_name} CAPTCHA...")
    screenshot = driver.get_screenshot_as_png()
    screenshot_base64 = base64.b64encode(screenshot).decode('utf-8')
    
    try:
        requests.post(f"{CAPTCHA_SERVER}/api/reset", timeout=5)
        import captcha_server
        captcha_server.current_captcha['screenshot'] = screenshot_base64
        captcha_server.current_captcha['message'] = f'请点击 {site_name} 的 CAPTCHA'
        captcha_server.current_captcha['solved'] = False
        captcha_server.current_captcha['coordinates'] = []
        
        print(f"  ✅ CAPTCHA 已显示在 http://8.213.149.224:7676")
        print(f"  💡 Martin，请访问网页点击 CAPTCHA")
        
        timeout = 120
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if captcha_server.current_captcha.get('solved'):
                print(f"  ✅ 收到点击！")
                return True
            time.sleep(1)
        
        print(f"  ⚠️ 等待超时")
        return False
    except Exception as e:
        print(f"  ❌ 错误：{e}")
        return False

def register_account(driver, account):
    """注册单个账号"""
    print(f"\n{'='*60}")
    print(f"注册 {account['name']}")
    print(f"{'='*60}")
    
    try:
        driver.get(account['url'])
        time.sleep(5)
        
        # 自动填写表单（根据网站不同选择器不同）
        if account['name'] == 'Discord':
            try:
                driver.find_element(By.CSS_SELECTOR, 'input[type="email"]').send_keys(EMAIL)
                driver.find_element(By.CSS_SELECTOR, 'input[aria-label="Username"]').send_keys(account['username'])
                driver.find_element(By.CSS_SELECTOR, 'input[type="password"]').send_keys(PASSWORD)
                print("  ✅ 已自动填写邮箱/用户名/密码")
            except Exception as e:
                print(f"  ⚠️  自动填写失败：{e}")
        
        elif account['name'] == 'Reddit':
            try:
                driver.find_element(By.CSS_SELECTOR, 'input[type="email"]').send_keys(EMAIL)
                driver.find_element(By.CSS_SELECTOR, 'input[id="username"]').send_keys(account['username'])
                driver.find_element(By.CSS_SELECTOR, 'input[type="password"]').send_keys(PASSWORD)
                print("  ✅ 已自动填写邮箱/用户名/密码")
            except Exception as e:
                print(f"  ⚠️  自动填写失败：{e}")
        
        # 等待 CAPTCHA
        print("  ⏳ 等待 CAPTCHA 出现...")
        time.sleep(5)
        
        # 截图并等待 Martin 点击
        if wait_for_captcha(driver, account['name']):
            print(f"  ✅ {account['name']} 注册进行中...")
            time.sleep(5)
            return True
        else:
            print(f"  ⚠️  {account['name']} 等待超时")
            return False
            
    except Exception as e:
        print(f"  ❌ {account['name']} 注册失败：{e}")
        return False

def main():
    print("\n" + "="*60)
    print("三人协作 - 社交媒体账号注册")
    print("="*60)
    print(f"邮箱：{EMAIL}")
    print(f"账号数：{len(ACCOUNTS)}")
    print(f"CAPTCHA 服务器：{CAPTCHA_SERVER}")
    print("="*60)
    
    driver = setup_driver()
    print("✅ 浏览器已启动")
    
    success = 0
    for account in ACCOUNTS:
        if register_account(driver, account):
            success += 1
        time.sleep(3)
    
    driver.quit()
    
    print("\n" + "="*60)
    print(f"注册完成：{success}/{len(ACCOUNTS)}")
    print("="*60)

if __name__ == "__main__":
    main()
