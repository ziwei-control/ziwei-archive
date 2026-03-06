#!/bin/bash
# x402 API 服务守护脚本
# 自动重启停止的服务

LOG_FILE="/tmp/x402-services-watchdog.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

check_and_restart() {
    local port=$1
    local name=$2
    local script=$3
    
    if ! pgrep -f "$script" > /dev/null; then
        log "⚠️ $name 服务已停止，正在重启..."
        cd /home/admin/Ziwei/projects/x402-api
        nohup python3 "$script" > "/tmp/${name}.log" 2>&1 &
        sleep 3
        if pgrep -f "$script" > /dev/null; then
            log "✅ $name 服务已重启"
        else
            log "❌ $name 服务重启失败"
        fi
    fi
}

log "=== 开始检查服务 ==="

# 检查 8090 端口 - API 密钥发放
check_and_restart 8090 "api-key-server" "api_key_server.py"

# 检查 8091 端口 - 用户登录
check_and_restart 8091 "dashboard" "x402_dashboard.py"

# 检查 5002 端口 - AI API
check_and_restart 5002 "api-server" "x402_api_server.py"

log "=== 服务检查完成 ==="
