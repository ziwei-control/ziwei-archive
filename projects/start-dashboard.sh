#!/bin/bash
# 紫微智控 - Dashboard 启动脚本

PORT=8081
PID_FILE=/tmp/dashboard.pid
LOG_FILE=/home/admin/Ziwei/data/logs/dashboard.log

# 创建日志目录
mkdir -p /home/admin/Ziwei/data/logs

# 检查是否已运行
if ps aux | grep "[d]ashboard.py" > /dev/null 2>&1; then
    EXISTING_PID=$(ps aux | grep "[d]ashboard.py" | awk '{print $2}')
    echo "✅ Dashboard 已在运行 (PID: $EXISTING_PID)"
    echo "📍 访问地址：http://8.213.149.224/dashboard"
    exit 0
fi

# 启动 Dashboard
cd /home/admin/Ziwei/projects
nohup python3 dashboard.py > "$LOG_FILE" 2>&1 &
NEW_PID=$!

# 保存 PID
echo "$NEW_PID" > "$PID_FILE"

# 等待启动
sleep 3

# 检查是否启动成功
if ps -p "$NEW_PID" > /dev/null 2>&1; then
    echo "✅ Dashboard 已启动"
    echo "📍 访问地址："
    echo "   内网：http://localhost:$PORT"
    echo "   公网：http://8.213.149.224/dashboard"
    echo "📄 日志文件：$LOG_FILE"
else
    echo "❌ Dashboard 启动失败"
    cat "$LOG_FILE"
    exit 1
fi
