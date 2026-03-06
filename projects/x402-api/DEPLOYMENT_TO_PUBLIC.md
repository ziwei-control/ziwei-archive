# 🚀 x402 API - 公网部署指南

## 📋 部署方案

### 推荐 VPS 提供商

| 提供商 | 价格 | 配置 | 链接 |
|--------|------|------|------|
| **DigitalOcean** | $5/月 | 1GB/1CPU/25GB SSD | https://digitalocean.com |
| **Vultr** | $5/月 | 1GB/1CPU/25GB SSD | https://vultr.com |
| **Linode** | $5/月 | 1GB/1CPU/25GB SSD | https://linode.com |
| **阿里云** | ¥24/月 | 1GB/1CPU/40GB SSD | https://aliyun.com |
| **腾讯云** | ¥25/月 | 1GB/1CPU/50GB SSD | https://tencentcloud.com |

---

## 🛠️ 部署步骤

### 第 1 步：购买 VPS

```bash
选择配置:
- 系统：Ubuntu 20.04 LTS
- CPU: 1 核心
- 内存：1GB
- 硬盘：25GB SSD
- 带宽：1TB/月
```

### 第 2 步：连接服务器

```bash
# 获取 VPS IP 地址后
ssh root@your-vps-ip

# 输入密码登录
```

### 第 3 步：安装依赖

```bash
# 更新系统
apt update && apt upgrade -y

# 安装 Python3 和 pip
apt install -y python3 python3-pip git

# 安装必要工具
apt install -y curl wget nginx certbot
```

### 第 4 步：上传代码

```bash
# 方法 1: 使用 git
cd /opt
git clone https://github.com/ziwei-control/ziwei-audit-system.git
cd ziwei-audit-system

# 方法 2: 使用 scp (本地执行)
scp -r /home/admin/Ziwei/projects/x402-api root@your-vps-ip:/opt/
```

### 第 5 步：配置环境

```bash
cd /opt/x402-api

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 创建.env 文件
nano .env
```

.env 内容：
```
DASHSCOPE_API_KEY=sk-sp-deb52dabf75c47308911359d51a0a420
PAYMENT_WALLET=0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb
PORT=5002
```

### 第 6 步：创建 systemd 服务

```bash
nano /etc/systemd/system/x402-api.service
```

服务内容：
```ini
[Unit]
Description=x402 API Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/x402-api
ExecStart=/opt/x402-api/venv/bin/python3 /opt/x402-api/app_production.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
systemctl daemon-reload
systemctl enable x402-api
systemctl start x402-api
systemctl status x402-api
```

### 第 7 步：配置 Nginx 反向代理

```bash
nano /etc/nginx/sites-available/x402-api
```

Nginx 配置：
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://8.213.149.224:5002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

启用配置：
```bash
ln -s /etc/nginx/sites-available/x402-api /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

### 第 8 步：配置域名

```bash
# 在域名 DNS 设置中添加 A 记录
类型：A
主机：@ 或 api
值：your-vps-ip
TTL: 600
```

### 第 9 步：配置 SSL 证书

```bash
# 安装 Certbot
apt install -y certbot python3-certbot-nginx

# 获取证书
certbot --nginx -d your-domain.com

# 自动续期
certbot renew --dry-run
```

### 第 10 步：配置防火墙

```bash
# 安装 UFW
apt install -y ufw

# 允许 SSH
ufw allow ssh

# 允许 HTTP/HTTPS
ufw allow http
ufw allow https

# 启用防火墙
ufw enable
ufw status
```

---

## 📊 部署后验证

### 检查服务状态

```bash
systemctl status x402-api
journalctl -u x402-api -f
```

### 测试 API

```bash
# 本地测试
curl http://8.213.149.224:5002/health

# 公网测试
curl https://your-domain.com/health
```

### 查看日志

```bash
# 应用日志
tail -f /opt/x402-api/api.log

# Nginx 日志
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

---

## 💰 成本估算

| 项目 | 费用 |
|------|------|
| VPS | $5/月 |
| 域名 | $10/年 |
| SSL | 免费 |
| **总计** | **$70/年** |

---

## 🎯 预期收益

| 项目 | 收入 |
|------|------|
| API 调用 | $1,500/月 |
| 成本 | $6/月 |
| **利润** | **$1,494/月** |

---

## 📞 技术支持

### 常见问题

**Q: 服务无法启动？**
```bash
# 检查日志
journalctl -u x402-api -n 50

# 检查端口
netstat -tlnp | grep 5002
```

**Q: 无法访问？**
```bash
# 检查防火墙
ufw status

# 检查 Nginx
nginx -t
systemctl status nginx
```

**Q: API 调用失败？**
```bash
# 检查 API Key
cat .env

# 测试连接
curl http://8.213.149.224:5002/health
```

---

## 🚀 快速部署脚本

```bash
#!/bin/bash
# 一键部署脚本

DOMAIN=$1
EMAIL=$2

# 安装依赖
apt update && apt upgrade -y
apt install -y python3 python3-pip git nginx certbot python3-certbot-nginx

# 克隆代码
cd /opt
git clone https://github.com/ziwei-control/ziwei-audit-system.git
cd ziwei-audit-system

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 创建服务
cat > /etc/systemd/system/x402-api.service << 'EOF'
[Unit]
Description=x402 API Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/x402-api
ExecStart=/opt/x402-api/venv/bin/python3 /opt/x402-api/app_production.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable x402-api
systemctl start x402-api

# 配置 Nginx
cat > /etc/nginx/sites-available/x402-api << EOF
server {
    listen 80;
    server_name $DOMAIN;
    location / {
        proxy_pass http://8.213.149.224:5002;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF

ln -s /etc/nginx/sites-available/x402-api /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx

# 配置 SSL
certbot --nginx -d $DOMAIN --email $EMAIL --agree-tos --non-interactive

echo "✅ 部署完成！"
echo "访问地址：https://$DOMAIN"
```

使用：
```bash
bash deploy.sh api.yourdomain.com your@email.com
```

---

**准备开始部署吗？** 🚀
