#!/bin/bash
# =============================================================================
# 紫微智控 Dashboard 启动脚本 v4.0.1
# =============================================================================

echo "🚀 启动 Dashboard v4.0.1..."
echo ""

# 检查是否已有进程运行
if pgrep -f "dashboard.py" > /dev/null; then
    echo "⚠️  Dashboard 已在运行，正在停止..."
    pkill -f "dashboard.py"
    sleep 2
fi

# 启动新版本
cd /home/admin/Ziwei/projects
nohup python3 dashboard_v4_0_1.py > /tmp/dashboard_v4.log 2>&1 &

# 等待启动
sleep 3

# 检查是否成功
if pgrep -f "dashboard.py" > /dev/null; then
    echo "✅ Dashboard v4.0.1 启动成功！"
    echo ""
    echo "📍 访问地址："
    echo "   内网：http://localhost:8081"
    echo "   公网：http://panda66.duckdns.org/dashboard"
    echo ""
    echo "📊 进程信息："
    ps aux | grep dashboard_v4 | grep -v grep
else
    echo "❌ Dashboard 启动失败！"
    echo ""
    echo "日志："
    tail -20 /tmp/dashboard_v4.log
fi
