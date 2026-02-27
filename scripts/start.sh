#!/bin/bash
# =============================================================================
# 紫微智控 - 快速启动脚本
# =============================================================================

set -e

Ziwei_DIR="/home/admin/Ziwei"
SCRIPTS_DIR="$Ziwei_DIR/scripts"
LOGS_DIR="$Ziwei_DIR/data/logs"

echo "╔════════════════════════════════════════════════════════╗"
echo "║          紫微智控 (Ziwei Control & Intelligence)        ║"
echo "║                   快速启动脚本                          ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# 检查配置文件
if [ ! -f "$Ziwei_DIR/.env" ]; then
    echo "⚠ 警告：.env 文件不存在"
    echo "  请复制 .env.example 并填写 API Key"
    echo ""
fi

# 检查 API Key
if grep -q "YOUR_API_KEY" "$Ziwei_DIR/.env" 2>/dev/null; then
    echo "⚠ 警告：API Key 未配置"
    echo "  请编辑 .env 文件填写真实的 BAILIAN_API_KEY"
    echo ""
fi

# 启动本地监控
echo "[1/3] 启动本地监控..."
cd "$SCRIPTS_DIR"
nohup python3 local_monitor.py > "$LOGS_DIR/local_monitor.log" 2>&1 &
MONITOR_PID=$!
echo "  ✓ 本地监控已启动 (PID: $MONITOR_PID)"

# 启动进度监工
echo "[2/3] 启动进度监工（18 分钟巡查）..."
nohup python3 supervisor.py > "$LOGS_DIR/supervisor.log" 2>&1 &
SUPERVISOR_PID=$!
echo "  ✓ 进度监工已启动 (PID: $SUPERVISOR_PID)"

# 启动急救员
echo "[3/3] 启动急救员（心跳监控）..."
nohup python3 paramedic.py > "$LOGS_DIR/paramedic.log" 2>&1 &
PARAMEDIC_PID=$!
echo "  ✓ 急救员已启动 (PID: $PARAMEDIC_PID)"

# 保存 PID 文件
cat > "$Ziwei_DIR/data/pids.txt" << EOF
local_monitor=$MONITOR_PID
supervisor=$SUPERVISOR_PID
paramedic=$PARAMEDIC_PID
started=$(date -Iseconds)
EOF

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║                    启动完成！                          ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "运行中的服务:"
echo "  - 本地监控：PID $MONITOR_PID"
echo "  - 进度监工：PID $SUPERVISOR_PID"
echo "  - 急救员：PID $PARAMEDIC_PID"
echo ""
echo "查看日志:"
echo "  tail -f $LOGS_DIR/local_monitor.log"
echo "  tail -f $LOGS_DIR/supervisor.log"
echo "  tail -f $LOGS_DIR/paramedic.log"
echo ""
echo "停止服务:"
echo "  $SCRIPTS_DIR/stop.sh"
echo ""
