# 🔒 global-warroom-upgraded 安全漏洞修复

## 🚨 严重安全问题

### 硬编码敏感凭证

**文件**:
- `/home/admin/Ziwei/projects/global-warroom-upgraded/scripts/global-warroom-upgraded.py`
- `/home/admin/Ziwei/projects/global-warroom-upgraded/scripts/global-warroom.py`

**危险代码**:
```python
"sender_password": "UMayTeWFZsFqwv6M"  # ❌ 明文密码！
```

**风险等级**: CRITICAL（最高危）

**危害**:
- 邮箱被盗
- 窃取所有邮件内容
- 接管其他账户
- 发送钓鱼邮件

---

## ✅ 修复方案

### 方案 1：使用环境变量（推荐）

**创建 `.env` 文件**:
```bash
# /home/admin/Ziwei/projects/global-warroom-upgraded/.env
SMTP_SERVER=smtp.163.com
SMTP_PORT=465
SENDER_EMAIL=pandac00@163.com
SENDER_PASSWORD=UMayTeWFZsFqwv6M
RECEIVER_EMAIL=19922307306@189.cn
```

**修改代码**:
```python
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

CONFIG = {
    "email": {
        "smtp_server": os.getenv("SMTP_SERVER"),
        "smtp_port": int(os.getenv("SMTP_PORT", 465)),
        "sender_email": os.getenv("SENDER_EMAIL"),
        "sender_password": os.getenv("SENDER_PASSWORD"),
        "receiver_email": os.getenv("RECEIVER_EMAIL")
    }
}
```

**保护 .env 文件**:
```bash
# 添加到 .gitignore
echo ".env" >> /home/admin/Ziwei/projects/global-warroom-upgraded/.gitignore

# 设置文件权限（仅所有者可读）
chmod 600 /home/admin/Ziwei/projects/global-warroom-upgraded/.env
```

---

### 方案 2：使用 Python keyring（更安全）

**安装**:
```bash
pip3 install keyring
```

**存储密码**:
```python
import keyring

# 设置密码
keyring.set_password("global-warroom", "smtp", "UMayTeWFZsFqwv6M")
```

**读取密码**:
```python
import keyring

# 获取密码
password = keyring.get_password("global-warroom", "smtp")
```

**优势**:
- ✅ 密码不存储在代码中
- ✅ 使用系统密钥环加密
- ✅ 不需要文件权限管理

---

## 📝 修复步骤

### 立即执行

```bash
# 1. 创建 .env 文件
cat > /home/admin/Ziwei/projects/global-warroom-upgraded/.env << 'EOF'
SMTP_SERVER=smtp.163.com
SMTP_PORT=465
SENDER_EMAIL=pandac00@163.com
SENDER_PASSWORD=UMayTeWFZsFqwv6M
RECEIVER_EMAIL=19922307306@189.cn
EOF

# 2. 设置文件权限
chmod 600 /home/admin/Ziwei/projects/global-warroom-upgraded/.env

# 3. 添加到 .gitignore
echo ".env" >> /home/admin/Ziwei/projects/global-warroom-upgraded/.gitignore

# 4. 从代码中移除硬编码密码
# （需要手动编辑文件）
```

### 代码修改

在 `global-warroom-upgraded.py` 和 `global-warroom.py` 中：

**删除**:
```python
# ❌ 删除这行
"sender_password": "UMayTeWFZsFqwv6M",
```

**添加**:
```python
# ✅ 添加环境变量读取
import os
from dotenv import load_dotenv

load_dotenv()

CONFIG = {
    "email": {
        "smtp_server": os.getenv("SMTP_SERVER"),
        "smtp_port": int(os.getenv("SMTP_PORT", 465)),
        "sender_email": os.getenv("SENDER_EMAIL"),
        "sender_password": os.getenv("SENDER_PASSWORD"),  # 从环境变量读取
        "receiver_email": os.getenv("RECEIVER_EMAIL")
    }
}
```

---

## 🔍 验证修复

```bash
# 检查 .env 文件权限
ls -la /home/admin/Ziwei/projects/global-warroom-upgraded/.env

# 检查 .gitignore
cat /home/admin/Ziwei/projects/global-warroom-upgraded/.gitignore

# 测试配置加载
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('SMTP:', os.getenv('SMTP_SERVER'))
print('Password:', '***' if os.getenv('SENDER_PASSWORD') else 'NOT FOUND')
"
```

---

## ⚠️ 其他注意事项

### 密码轮换

建议定期更换邮箱密码：

1. 登录 163 邮箱
2. 修改密码
3. 更新 `.env` 文件
4. 重启服务

### 访问控制

- ✅ 仅授权人员可访问服务器
- ✅ 使用 SSH 密钥认证
- ✅ 禁用密码登录
- ✅ 定期审计访问日志

---

## 📊 修复前对比

| 项目 | 修复前 | 修复后 |
|------|--------|--------|
| 密码存储 | ❌ 代码中明文 | ✅ 环境变量/密钥环 |
| 风险等级 | 🔴 CRITICAL | 🟢 LOW |
| 代码泄露影响 | ❌ 密码直接暴露 | ✅ 密码不在代码中 |
| 密码轮换 | ❌ 需要修改代码 | ✅ 只需更新环境变量 |

---

## 🎯 总结

**修复优先级**: 立即（CRITICAL）

**修复方案**:
1. 创建 `.env` 文件
2. 移动密码到环境变量
3. 设置文件权限
4. 添加到 `.gitignore`
5. 重新部署

**修复后**: 安全风险从 CRITICAL 降至 LOW

---

**修复日期**: 2026-03-02
**审计工具**: x402 API 代码审计
**发现**: 硬编码敏感凭证