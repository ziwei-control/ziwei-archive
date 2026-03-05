#!/bin/bash
# =============================================================================
# x402 API - 快速启动脚本
# 功能：一键启动 x402 API 服务并显示状态
# =============================================================================

echo "======================================================================="
echo "🚀 紫微智控 x402 API - 快速启动"
echo "======================================================================="
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装，请先安装 Python3"
    exit 1
fi

# 进入项目目录
cd /home/admin/Ziwei/projects/x402-api || exit 1

# 检查依赖
echo "📦 检查依赖..."
if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt 不存在"
    exit 1
fi

pip3 install -r requirements.txt -q
echo "✅ 依赖检查完成"
echo ""

# 检查是否已有进程运行
if pgrep -f "app_production.py" > /dev/null; then
    echo "⚠️  x402 API 已在运行"
    echo ""
    ps aux | grep app_production | grep -v grep
    echo ""
    read -p "是否重启？(y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 0
    fi
    pkill -f "app_production.py"
    sleep 2
fi

# 启动服务
echo "🚀 启动 x402 API 服务..."
nohup python3 app_production.py > api.log 2>&1 &
sleep 3

# 检查启动状态
if pgrep -f "app_production.py" > /dev/null; then
    echo "✅ x402 API 启动成功！"
    echo ""
    echo "======================================================================="
    echo "📊 服务信息"
    echo "======================================================================="
    echo ""
    echo "🌐 访问地址："
    echo "   内网：http://localhost:5002"
    echo "   本地：http://localhost:5002"
    echo ""
    echo "📋 API 端点："
    echo "   - /api/v1/architect    (架构设计)"
    echo "   - /api/v1/code-gen     (代码生成)"
    echo "   - /api/v1/code-audit   (代码审计)"
    echo "   - /api/v1/logic        (逻辑推理)"
    echo "   - /api/v1/translator   (翻译服务)"
    echo "   - /api/v1/long-text    (长文解析)"
    echo "   - /api/v1/crawl        (网络爬虫)"
    echo "   - /api/v1/vision       (视觉解析)"
    echo ""
    echo "💰 当前收入：$(cat data/payments.json 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(f\"{sum(p.get('amount',0) for p in d.get('payments',[]).values() if p.get('verified')):.4f} USDC\")" 2>/dev/null || echo "0.0000 USDC")"
    echo ""
    echo "📋 进程信息："
    ps aux | grep app_production | grep -v grep
    echo ""
    echo "📖 文档："
    echo "   - 实施计划：/home/admin/Ziwei/projects/x402-api/X402_IMPLEMENTATION_PLAN.md"
    echo "   - API 文档：https://docs.openclaw.ai/x402-api"
    echo ""
    echo "======================================================================="
    echo ""
    echo "💡 快速测试："
    echo "   curl http://localhost:5002/health"
    echo ""
else
    echo "❌ x402 API 启动失败！"
    echo ""
    echo "日志："
    tail -20 api.log
    exit 1
fi
