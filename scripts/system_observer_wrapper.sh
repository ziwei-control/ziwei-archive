#!/bin/bash
# Observer包装脚本 - 每20分钟运行一次

OBSERVER_SCRIPT="/home/admin/Ziwei/scripts/system_observer.py"
LOG_FILE="/home/admin/Ziwei/data/logs/observer/wrapper.log"
INTERVAL_MINUTES=60  # 优化：从 20 分钟改为 60 分钟，减少重复报告

# 创建日志目录
mkdir -p "$(dirname "$LOG_FILE")"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "🚀 Observer包装脚本启动"
log "📅 观察间隔：${INTERVAL_MINUTES}分钟"
log "⚡ 优先保证Telegram响应"

while true; do
    log "🔍 开始观察..."
    
    # 运行observer
    python3 "$OBSERVER_SCRIPT"
    EXIT_CODE=$?
    
    if [ $EXIT_CODE -eq 0 ]; then
        log "✅ 观察完成，等待${INTERVAL_MINUTES}分钟..."
    else
        log "❌ 观察异常退出（代码：$EXIT_CODE），等待${INTERVAL_MINUTES}分钟后重试..."
    fi
    
    # 等待指定间隔
    sleep $((INTERVAL_MINUTES * 60))
    
    log "🔄 准备下一次观察..."
done
