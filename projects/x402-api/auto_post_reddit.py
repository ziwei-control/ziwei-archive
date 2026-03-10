#!/usr/bin/env python3
# =============================================================================
# Reddit 自动发帖脚本
# 使用：python3 auto_post_reddit.py
# =============================================================================

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# 账号信息
EMAIL = "pandac00@163.com"
PASSWORD = "ZiweiControl2026!"

# 发帖内容
TITLE = "Built a pay-per-call AI API service ($0.02/call, no subscription)"

CONTENT = """
Hi r/programming!

I've been working on x402 API for the past month. The idea is simple: instead of paying $10-20/month for AI APIs you barely use, you pay per call starting from $0.02 USDC.

Tech stack:
- Backend: Python + HTTP Server
- AI: Aliyun Bailian API
- Payment: USDC on Base chain (low gas fees)
- Frontend: Pure HTML/CSS/JS

8 endpoints available:
- Translation: $0.02/call
- Code Audit: $0.05/call
- Code Generation: $0.08/call
- Architecture Design: $0.10/call
- And more...

Free trial until March 9th. No registration required.

👉 Try it: http://8.213.149.224:8090/get-api-key.html
📚 Code: https://github.com/ziwei-control/ziwei-archive

Happy to answer any questions!
"""

def main():
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║       Reddit 自动发帖脚本                                 ║")
    print("╠═══════════════════════════════════════════════════════════╣")
    print(f"  账号：{EMAIL}")
    print(f"  板块：r/programming")
    print("╚═══════════════════════════════════════════════════════════╝")
    print()
    
    # 启动浏览器
    print("🌐 启动浏览器...")
    options = webdriver.FirefoxOptions()
    options.headless = False  # 显示浏览器，方便处理 CAPTCHA
    driver = webdriver.Firefox(options=options)
    
    try:
        # 1. 登录 Reddit
        print("📝 步骤 1: 登录 Reddit")
        driver.get("https://www.reddit.com/login")
        time.sleep(3)
        
        print("  ⏳ 请手动登录（处理 CAPTCHA）...")
        print("  💡 登录完成后，脚本会自动继续")
        
        # 等待登录成功（检测用户头像）
        WebDriverWait(driver, 300).until(
            lambda d: d.find_element(By.CSS_SELECTOR, '[data-testid="user-menu"]')
        )
        print("  ✅ 登录成功！")
        time.sleep(2)
        
        # 2. 打开发帖页面
        print("\n📝 步骤 2: 打开发帖页面")
        driver.get("https://www.reddit.com/r/programming/submit")
        time.sleep(3)
        
        # 3. 填写标题
        print("📝 步骤 3: 填写标题")
        title_input = driver.find_element(By.CSS_SELECTOR, 'input[id="title"]')
        title_input.send_keys(TITLE)
        print(f"  ✅ 标题已填写")
        time.sleep(1)
        
        # 4. 选择 Text 帖子类型
        print("\n📝 步骤 4: 选择 Text 帖子类型")
        # Reddit 界面可能变化，这里需要手动选择
        print("  ⚠️  请手动点击'Text'选项")
        time.sleep(5)
        
        # 5. 填写内容
        print("\n📝 步骤 5: 填写内容")
        try:
            content_input = driver.find_element(By.CSS_SELECTOR, 'div[contenteditable="true"]')
            content_input.send_keys(CONTENT)
            print("  ✅ 内容已填写")
        except:
            print("  ⚠️  请手动粘贴内容（已复制到剪贴板）")
            import pyperclip
            pyperclip.copy(CONTENT)
        
        time.sleep(3)
        
        # 6. 等待发布
        print("\n📝 步骤 6: 等待发布")
        print("  ⏳ 请手动点击'Post'按钮")
        print("  ⏳ 可能需要完成 CAPTCHA 验证")
        
        # 等待发布成功
        input("\n  发布完成后按 Enter 继续...")
        
        print("\n╔═══════════════════════════════════════════════════════════╗")
        print("║       ✅ Reddit 发帖完成！                                 ║")
        print("╚═══════════════════════════════════════════════════════════╝")
        
    except Exception as e:
        print(f"\n❌ 错误：{e}")
        print("💡 请手动完成发帖")
    
    finally:
        driver.quit()
        print("\n👋 浏览器已关闭")

if __name__ == "__main__":
    main()
