# x402 API - 生产环境部署指南

## 🚀 快速开始

### 1. 准备服务器

```bash
# 推荐 VPS 提供商
# - DigitalOcean: $5/月起
# - Vultr: $5/月起
# - Linode: $5/月起
# - 阿里云: $8/月起
# - 腾讯云: $9/月起

# 系统要求
# - Ubuntu 20.04+ / CentOS 7+
# - Python 3.6+
# - 1GB RAM 以上
```

### 2. 上传文件

```bash
# 方法 1: 使用 scp
scp -r /home/admin/Ziwei/projects/x402-api user@your-server:/opt/x402-api

# 方法 2: 使用 git
cd /home/admin/Ziwei/projects/x402-api
git init
git add .
git commit -m "Initial deployment"
git remote add origin your-repo-url
git push -u origin main

# 在服务器上
git clone your-repo-url /opt/x402-api
```

### 3. 安装依赖

```bash
# 连接到服务器
ssh user@your-server

# 进入项目目录
cd /opt/x402-api

# 安装依赖（如果需要）
# pip3 install -r requirements.txt
```

### 4. 配置环境变量

```bash
# 创建 .env 文件
cat > .env << 'EOF'
DASHSCOPE_API_KEY=sk-sp-deb52dabf75c47308911359d51a0a420
PAYMENT_WALLET=0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb
EOF

# 设置权限
chmod 600 .env
```

### 5. 启动服务

```bash
# 使用部署脚本
python3 deploy.py start

# 或直接启动
nohup python3 app_production.py > api.log 2>&1 &

# 检查状态
python3 deploy.py status

# 查看日志
python3 deploy.py logs
```

### 6. 配置防火墙

```bash
# Ubuntu/Debian
sudo ufw allow 5002/tcp
sudo ufw enable

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=5002/tcp
sudo firewall-cmd --reload
```

### 7. 配置 Nginx 反向代理（可选）

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 8. 配置 SSL 证书

```bash
# 使用 Let's Encrypt（免费）
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

## 📊 运行管理

```bash
# 启动
python3 deploy.py start

# 停止
python3 deploy.py stop

# 重启
python3 deploy.py restart

# 状态
python3 deploy.py status

# 日志
python3 deploy.py logs

# 测试
python3 deploy.py test
```

---

## 🔧 常见问题

### 端口被占用

```bash
# 查看占用端口的进程
lsof -i :5002

# 杀死进程
kill -9 <PID>
```

### 服务无法启动

```bash
# 查看日志
tail -100 api.log

# 检查 Python 版本
python3 --version

# 手动测试
python3 app_production.py
```

---

## 🔒 安全建议

1. **使用防火墙**：只开放必要端口
2. **配置 SSL**：强制 HTTPS
3. **限制访问**：配置 IP 白名单
4. **定期更新**：保持系统和依赖更新
5. **监控日志**：定期检查异常访问

---

## 📈 性能优化

1. **使用 Gunicorn** (生产环境推荐)

```bash
pip3 install gunicorn

# 启动
gunicorn -w 4 -b 0.0.0.0:5002 app_production:app
```

2. **配置日志轮转**

```bash
# 使用 logrotate
sudo cat > /etc/logrotate.d/x402-api << 'EOF'
/opt/x402-api/api.log {
    daily
    rotate 7
    compress
    missingok
    notifempty
}
EOF
```

---

## 📞 技术支持

- 文档: /home/admin/Ziwei/projects/x402-api/docs/
- 部署脚本: deploy.py
- 健康检查: http://your-domain.com:5002/health

---

**部署日期**: 2026-03-02
**服务端口**: 5002
**API 基础路径**: /api/v1/