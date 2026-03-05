#!/bin/bash
# x402 API 密钥自动发放服务 - 快速启动脚本

echo "============================================================"
echo "x402 API 密钥自动发放服务"
echo "============================================================"

# 检查 Python 依赖
echo "检查依赖..."
python3 -c "import flask" 2>/dev/null || {
    echo "❌ Flask 未安装，正在安装..."
    pip3 install flask
}

python3 -c "import requests" 2>/dev/null || {
    echo "❌ Requests 未安装，正在安装..."
    pip3 install requests
}

echo "✅ 依赖检查完成"

# 创建 templates 目录
mkdir -p templates

# 复制 HTML 到 templates 目录
cp api-key-generator.html templates/ 2>/dev/null || true

echo ""
echo "============================================================"
echo "启动服务..."
echo "访问地址：http://localhost:8080"
echo "============================================================"
echo ""

# 启动服务
python3 api_key_server.py "$@"
