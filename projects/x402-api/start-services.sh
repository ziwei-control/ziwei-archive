#!/bin/bash
# x402 API 服务自启动脚本

echo "============================================================"
echo "x402 API 服务启动脚本"
echo "============================================================"

# 进入项目目录
cd /home/admin/Ziwei/projects/x402-api

# 停止旧服务
echo "停止旧服务..."
pkill -f api_key_server.py 2>/dev/null
pkill -f x402_dashboard.py 2>/dev/null
sleep 2

# 启动 API 密钥发放服务
echo "启动 API 密钥发放服务..."
nohup python3 api_key_server.py > /tmp/api_key.log 2>&1 &
sleep 3

# 启动 Dashboard 服务
echo "启动 Dashboard 服务..."
nohup python3 x402_dashboard.py > /tmp/dashboard.log 2>&1 &
sleep 3

# 检查服务状态
echo ""
echo "============================================================"
echo "服务状态检查"
echo "============================================================"
ps aux | grep -E "api_key_server|x402_dashboard" | grep -v grep

echo ""
echo "============================================================"
echo "访问地址"
echo "============================================================"
echo "API 密钥获取：http://8.213.149.224:8090/get-api-key.html"
echo "Dashboard 监控：http://8.213.149.224:8091"
echo "API 服务器：http://8.213.149.224:5002"
echo "============================================================"
echo ""
echo "✅ 服务启动完成！"
