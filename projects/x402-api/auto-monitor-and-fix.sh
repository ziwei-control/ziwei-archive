#!/bin/bash
# =============================================================================
# x402 API 自动监控和修复脚本
# 功能：检查服务状态，发现错误立即修复
# =============================================================================

LOG_FILE="/home/admin/Ziwei/projects/x402-api/monitor.log"
ERROR_LOG="/home/admin/Ziwei/projects/x402-api/api.error.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

check_and_restart() {
    local name=$1
    local port=$2
    local cmd=$3
    local pid=$(lsof -t -i:$port 2>/dev/null)
    
    if [ -z "$pid" ]; then
        log "❌ $name (端口$port) 未运行，正在重启..."
        cd $(dirname $cmd)
        nohup python3 $(basename $cmd) > $(basename $cmd .py).log 2>&1 &
        sleep 3
        if lsof -t -i:$port >/dev/null 2>&1; then
            log "✅ $name 重启成功"
        else
            log "❌ $name 重启失败"
        fi
    else
        log "✅ $name (端口$port) 运行中 (PID: $pid)"
    fi
}

clear_error_log() {
    # 每天清空一次错误日志
    if [ ! -f "${ERROR_LOG}.last_cleared" ]; then
        > "$ERROR_LOG"
        touch "${ERROR_LOG}.last_cleared"
        log "✅ 已清空错误日志"
    fi
}

check_disk_space() {
    local usage=$(df /home | tail -1 | awk '{print $5}' | sed 's/%//')
    if [ $usage -gt 90 ]; then
        log "⚠️ 磁盘使用率超过 90%: ${usage}%"
        # 清理旧日志
        find /home/admin/Ziwei/projects -name "*.log" -mtime +7 -delete
        log "✅ 已清理 7 天前的日志"
    else
        log "✅ 磁盘使用率正常：${usage}%"
    fi
}

check_memory() {
    local mem_used=$(free | grep Mem | awk '{printf("%.0f", $3/$2 * 100.0)}')
    if [ $mem_used -gt 90 ]; then
        log "⚠️ 内存使用率超过 90%: ${mem_used}%"
    else
        log "✅ 内存使用率正常：${mem_used}%"
    fi
}

# 主循环
log "╔═══════════════════════════════════════════════════════════╗"
log "║       x402 API 自动监控启动                                ║"
log "╚═══════════════════════════════════════════════════════════╝"

clear_error_log
check_disk_space
check_memory

log ""
log "【检查服务状态】"
check_and_restart "x402 API" 5002 "/home/admin/Ziwei/projects/x402-api/app_production.py"
check_and_restart "API Key Server" 8090 "/home/admin/Ziwei/projects/x402-api/api_key_server.py"
check_and_restart "User Dashboard" 8091 "/home/admin/Ziwei/projects/x402-api/x402_dashboard.py"
check_and_restart "Main Dashboard" 8081 "/home/admin/Ziwei/projects/dashboard_v4_0_1.py"

log ""
log "【检查 Nginx】"
if ! pgrep nginx > /dev/null; then
    log "❌ Nginx 未运行，正在重启..."
    /usr/sbin/nginx
    sleep 2
    if pgrep nginx > /dev/null; then
        log "✅ Nginx 重启成功"
    else
        log "❌ Nginx 重启失败"
    fi
else
    log "✅ Nginx 运行中"
fi

log ""
log "【监控完成】"
