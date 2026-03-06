#!/usr/bin/env python3
"""
修复管理员登录页面
"""

# 管理员登录页面 HTML
ADMIN_LOGIN_HTML = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>x402 API - 管理员登录</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .login-container {
            background: white;
            border-radius: 20px;
            padding: 50px;
            max-width: 500px;
            width: 100%;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        .logo {
            text-align: center;
            margin-bottom: 30px;
        }
        .logo h1 {
            font-size: 32px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 10px;
        }
        .logo p { color: #666; font-size: 14px; }
        .form-group { margin-bottom: 25px; }
        .form-label {
            display: block;
            font-size: 14px;
            font-weight: bold;
            color: #333;
            margin-bottom: 8px;
        }
        .form-input {
            width: 100%;
            padding: 15px;
            border: 2px solid #ddd;
            border-radius: 10px;
            font-size: 14px;
            font-family: 'Courier New', monospace;
            transition: all 0.3s;
        }
        .form-input:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        .submit-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px;
            border-radius: 10px;
            font-size: 16px;
            font-weight: bold;
            width: 100%;
            cursor: pointer;
            transition: all 0.3s;
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        .submit-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(102, 126, 234, 0.5);
        }
        .error-message {
            background: #ffebee;
            color: #c62828;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            border-left: 4px solid #f44336;
            display: none;
        }
        .footer {
            text-align: center;
            margin-top: 30px;
            color: #999;
            font-size: 13px;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="logo">
            <h1>🔐 管理员登录</h1>
            <p>x402 API 管理系统</p>
        </div>
        
        <div class="error-message" id="errorMessage"></div>
        
        <form id="adminForm" onsubmit="handleAdminLogin(event)">
            <div class="form-group">
                <label class="form-label">📍 管理员地址</label>
                <input 
                    type="text" 
                    class="form-input" 
                    id="adminAddress"
                    placeholder="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
                    required
                />
            </div>
            
            <div class="form-group">
                <label class="form-label">🔑 密码</label>
                <input 
                    type="password" 
                    class="form-input" 
                    id="adminPassword"
                    placeholder="••••••••"
                    required
                />
            </div>
            
            <button type="submit" class="submit-btn">
                登录
            </button>
        </form>
        
        <div class="footer">
            <p><a href="/" style="color: #667eea;">返回用户登录</a></p>
        </div>
    </div>
    
    <script>
        async function handleAdminLogin(event) {
            event.preventDefault();
            
            const address = document.getElementById('adminAddress').value.trim();
            const password = document.getElementById('adminPassword').value.trim();
            const errorMessage = document.getElementById('errorMessage');
            
            try {
                const response = await fetch('/api/admin-login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        address: address,
                        password: password
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    alert('✅ 登录成功！');
                    window.location.href = data.redirect || '/admin-dashboard.html';
                } else {
                    errorMessage.textContent = '❌ ' + data.message;
                    errorMessage.style.display = 'block';
                }
            } catch (error) {
                errorMessage.textContent = '❌ 网络错误，请稍后重试';
                errorMessage.style.display = 'block';
            }
        }
    </script>
</body>
</html>
"""

print("✅ 管理员登录页面 HTML 已定义")
print("ADMIN_LOGIN_HTML 变量已准备好使用")
