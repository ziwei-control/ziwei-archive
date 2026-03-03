#!/bin/bash
# =============================================================================
# 紫微智控 - 停止脚本
# =============================================================================

Ziwei_DIR="/home/admin/Ziwei"
PID_FILE="$Ziwei_DIR/data/pids.txt"

echo "紫微智控 - 停止服务..."
echo ""

if [ ! -f "$PID_FILE" ]; then
    echo "⚠ PID 文件不存在，尝试查找进程..."
    pkill -f "local_monitor.py"
    pkill -f "supervisor.py"
    pkill -f "paramedic.py"
    echo "已停止所有紫微智控进程"
    exit 0
fi

# 读取 PID
source "$PID_FILE"

# 停止进程
if [ -n "$local_monitor" ] && kill -0 "$local_monitor" 2>/dev/null; then
    kill "$local_monitor"
    echo "  ✓ 已停止本地监控 (PID: $local_monitor)"
fi

if [ -n "$supervisor" ] && kill -0 "$supervisor" 2>/dev/null; then
    kill "$supervisor"
    echo "  ✓ 已停止进度监工 (PID: $supervisor)"
fi

if [ -n "$paramedic" ] && kill -0 "$paramedic" 2>/dev/null; then
    kill "$paramedic"
    echo "  ✓ 已停止急救员 (PID: $paramedic)"
fi

# 删除 PID 文件
rm "$PID_FILE"

echo ""
echo "所有服务已停止"
