#!/bin/bash
# 生成自签名 SSL 证书（用于 HTTPS）

echo "============================================================"
echo "生成 SSL 证书"
echo "============================================================"

# 检查 openssl
if ! command -v openssl &> /dev/null; then
    echo "❌ openssl 未安装，请先安装：sudo apt install openssl"
    exit 1
fi

echo "正在生成自签名证书..."

# 生成私钥和证书
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes \
    -subj "/C=CN/ST=Shanghai/L=Shanghai/O=Ziwei Control/OU=x402 API/CN=localhost"

echo ""
echo "✅ 证书生成完成！"
echo ""
echo "生成的文件："
echo "  - cert.pem (证书)"
echo "  - key.pem (私钥)"
echo ""
echo "使用方法："
echo "  1. 修改 api_key_server.py 中的配置："
echo "     HTTPS_ENABLED = True"
echo "  2. 启动服务："
echo "     python3 api_key_server.py"
echo "  3. 访问：https://localhost:4433"
echo ""
echo "⚠️  注意：这是自签名证书，浏览器会显示警告"
echo "   生产环境请使用 Let's Encrypt 等正规 CA 颁发的证书"
echo "============================================================"
