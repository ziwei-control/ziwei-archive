#!/bin/bash
# =============================================================================
# 紫微制造 - 截图功能快速启动
# 功能：一键设置并启动截图监控
# =============================================================================

set -e

SCRIPT_DIR="/home/admin/Ziwei/scripts"
LOG_DIR="/home/admin/Ziwei/data/logs"
NODE_LOG="$LOG_DIR/node.log"
GATEWAY_TOKEN="73c8f5efc97f05b131130f5dc069b2aaee15d28761ddac2c"

echo "=========================================="
echo "🚀 紫微截图功能快速启动"
echo "=========================================="
echo ""

# 确保日志目录存在
mkdir -p "$LOG_DIR"

# 步骤 1: 设置环境变量
echo "1️⃣ 设置 Gateway Token..."
export OPENCLAW_GATEWAY_TOKEN="$GATEWAY_TOKEN"
echo "✅ 已设置"
echo ""

# 步骤 2: 检查 Gateway 状态
echo "2️⃣ 检查 Gateway 状态..."
if ps aux | grep -q "[o]penclaw.*gateway"; then
    echo "✅ Gateway 正在运行"
else
    echo "❌ Gateway 未运行，请先启动 Gateway"
    echo "   openclaw gateway start"
    exit 1
fi
echo ""

# 步骤 3: 检查并启动 Node
echo "3️⃣ 检查 Node 状态..."
NODE_STATUS=$(openclaw nodes status 2>&1)
echo "$NODE_STATUS"

if echo "$NODE_STATUS" | grep -q "Connected: 0"; then
    echo ""
    echo "⚠️  Node 未连接，开始设置..."
    
    # 停止旧 Node
    echo "停止旧 Node..."
    pkill -f "openclaw node" || true
    sleep 2
    
    # 启动新 Node
    echo "启动 Node..."
    nohup openclaw node run \
        --host 127.0.0.1 \
        --port 18789 \
        --display-name "Ziwei Server Node" \
        > "$NODE_LOG" 2>&1 &
    
    NODE_PID=$!
    echo "✅ Node 已启动 (PID: $NODE_PID)"
    echo ""
    
    # 等待配对
    echo "⏳ 等待配对请求..."
    sleep 5
    
    echo ""
    echo "📋 请执行以下命令批准配对:"
    echo "   openclaw devices list"
    echo "   openclaw devices approve <requestId>"
    echo ""
    echo "批准后，再次运行此脚本完成设置"
else
    echo "✅ Node 已连接"
fi

echo ""
echo "4️⃣ 测试截图功能..."
cd "$SCRIPT_DIR"
python3 screenshot_module.py status

echo ""
echo "=========================================="
echo "✅ 设置完成！"
echo "=========================================="
echo ""
echo "下一步:"
echo "1. 如果 Node 未配对，请批准配对请求"
echo "2. 运行测试截图：python3 screenshot_module.py capture"
echo "3. 查看截图：ls -lh /home/admin/Ziwei/data/screenshots/"
echo ""
echo "自动监控已启用（每 8 分钟）"
echo "查看日志：tail -f /home/admin/Ziwei/data/logs/observer/visual_monitor.log"
echo ""
