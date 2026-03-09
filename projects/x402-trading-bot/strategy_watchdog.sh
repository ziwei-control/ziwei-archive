#!/bin/bash
# =============================================================================
# 策略引擎看门狗 - 确保策略引擎持续运行
# 功能：检测进程是否存在，如果停止则自动重启
# =============================================================================

LOG_FILE="/home/admin/Ziwei/data/logs/soul-trader/strategy_watchdog.log"
STRATEGY_SCRIPT="/home/admin/Ziwei/projects/x402-trading-bot/strategy_engine_v3.py"
PROCESS_NAME="strategy_engine_v3.py"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

check_and_restart() {
    # 检查进程是否存在
    if ! pgrep -f "$PROCESS_NAME" > /dev/null; then
        log "❌ 策略引擎未运行，正在重启..."
        
        # 启动策略引擎
        cd /home/admin/Ziwei/projects/x402-trading-bot
        nohup python3 "$STRATEGY_SCRIPT" > /home/admin/Ziwei/data/logs/soul-trader/strategy_engine_$(date +%Y%m%d).log 2>&1 &
        
        sleep 5
        
        # 验证是否启动成功
        if pgrep -f "$PROCESS_NAME" > /dev/null; then
            log "✅ 策略引擎已重启 (PID: $(pgrep -f "$PROCESS_NAME"))"
        else
            log "❌ 策略引擎重启失败"
        fi
    else
        log "✅ 策略引擎运行中 (PID: $(pgrep -f "$PROCESS_NAME"))"
    fi
}

# 主循环
log "╔═══════════════════════════════════════════════════════════╗"
log "║       策略引擎看门狗启动                                   ║"
log "╚═══════════════════════════════════════════════════════════╝"

while true; do
    check_and_restart
    sleep 60  # 每分钟检查一次
done
