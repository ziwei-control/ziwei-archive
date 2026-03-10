#!/bin/bash
# =============================================================================
# 策略引擎看门狗 v2.0 - 确保策略引擎持续运行
# 功能：检测进程是否存在，如果停止则自动重启
# 改进：添加异常处理、日志轮转、systemd 状态检查
# =============================================================================

set -e  # 遇到错误立即退出

LOG_FILE="/home/admin/Ziwei/data/logs/soul-trader/strategy_watchdog.log"
STRATEGY_SCRIPT="/home/admin/Ziwei/projects/x402-trading-bot/strategy_engine_v3.py"
PROCESS_NAME="strategy_engine_v3.py"
MAX_LOG_SIZE=10485760  # 10MB

# 日志轮转函数
rotate_log() {
    if [ -f "$LOG_FILE" ] && [ $(stat -c%s "$LOG_FILE" 2>/dev/null || echo 0) -gt $MAX_LOG_SIZE ]; then
        mv "$LOG_FILE" "${LOG_FILE}.$(date +%Y%m%d_%H%M%S).bak"
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] 🔄 日志轮转完成" > "$LOG_FILE"
    fi
}

log() {
    # 确保日志目录存在
    mkdir -p "$(dirname "$LOG_FILE")"
    
    # 写入日志
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 错误处理
handle_error() {
    log "❌ 看门狗错误：$1"
    # 不退出，继续尝试恢复
    sleep 10
}

# 陷阱处理（确保优雅退出）
trap 'log "⚠️ 看门狗收到终止信号，正在退出..."; exit 0' SIGTERM SIGINT

check_account_health() {
    local ACCOUNT_FILE="/home/admin/Ziwei/data/strategy/account_status.json"
    
    # 检查账户文件是否存在
    if [ ! -f "$ACCOUNT_FILE" ]; then
        log "⚠️ 账户状态文件不存在，跳过健康检查"
        return 0
    fi
    
    # 检查 jq 是否可用
    if ! command -v jq &> /dev/null; then
        log "⚠️ jq 未安装，跳过账户健康检查"
        return 0
    fi
    
    # 读取账户余额
    local balance=$(jq -r '.balance // 0' "$ACCOUNT_FILE" 2>/dev/null)
    
    # 检查余额是否异常（< $100 或为 0）
    if [ "$balance" != "null" ] && [ -n "$balance" ]; then
        local is_low=$(echo "$balance < 100" | bc -l 2>/dev/null || echo "0")
        if [ "$is_low" = "1" ]; then
            log "❌ 账户余额异常：$balance USDC (< $100)，需要重启策略引擎"
            return 1
        fi
        
        # 检查是否是科学计数法极小值（如 2.22e-64）
        if echo "$balance" | grep -qiE 'e-[0-9]{2,}'; then
            log "❌ 账户余额为科学计数法极小值：$balance，需要重启策略引擎"
            return 1
        fi
    fi
    
    # 检查持仓是否异常（所有持仓都是 0 或极小值）
    local positions=$(jq -r '.portfolio | length' "$ACCOUNT_FILE" 2>/dev/null)
    if [ "$positions" != "null" ] && [ "$positions" -gt 0 ]; then
        # 检查是否有正常持仓（金额 > $1）
        local has_valid_position=$(jq -r '
            .portfolio | to_entries | map(
                select(.value.amount != null and .value.amount != 0) |
                select((.value.amount | tostring) | test("e-[0-9]{2,}") | not)
            ) | length
        ' "$ACCOUNT_FILE" 2>/dev/null || echo "0")
        
        if [ "$has_valid_position" = "0" ] && [ "$positions" -gt 0 ]; then
            log "❌ 所有持仓都是 0 或无效值，需要重启策略引擎"
            return 1
        fi
    fi
    
    log "✅ 账户健康检查通过 (余额：$balance USDC, 持仓：$positions 个)"
    return 0
}

restart_strategy_engine() {
    log "🔄 正在重启策略引擎..."
    
    # 尝试停止 systemd 服务
    if systemctl stop ziwei-strategy 2>/dev/null; then
        log "✅ 已停止 systemd 服务"
    fi
    
    # 杀死所有相关进程
    pkill -f "$PROCESS_NAME" 2>/dev/null || true
    sleep 2
    
    # 尝试启动 systemd 服务
    if systemctl start ziwei-strategy 2>/dev/null; then
        sleep 5
        if systemctl is-active --quiet ziwei-strategy; then
            log "✅ 策略引擎已通过 systemd 重启"
            return 0
        fi
    fi
    
    # 降级方案：直接启动进程
    log "⚠️ systemd 启动失败，使用降级方案..."
    cd /home/admin/Ziwei/projects/x402-trading-bot || handle_error "无法切换目录"
    
    nohup python3 "$STRATEGY_SCRIPT" > /home/admin/Ziwei/data/logs/soul-trader/strategy_engine_$(date +%Y%m%d).log 2>&1 &
    local PID=$!
    
    sleep 5
    
    # 验证是否启动成功
    if pgrep -f "$PROCESS_NAME" > /dev/null; then
        log "✅ 策略引擎已重启 (PID: $(pgrep -f "$PROCESS_NAME"))"
        return 0
    else
        log "❌ 策略引擎重启失败"
        handle_error "重启失败"
        return 1
    fi
}

check_and_restart() {
    rotate_log
    
    # 1. 检查 systemd 服务状态（优先）
    if systemctl is-active --quiet ziwei-strategy 2>/dev/null; then
        log "✅ 策略引擎运行中 (systemd 管理)"
        
        # 增加账户健康检查
        if ! check_account_health; then
            log "⚠️ 账户状态异常，正在重启策略引擎..."
            restart_strategy_engine
        fi
        return 0
    fi
    
    # 2. 检查进程是否存在
    if ! pgrep -f "$PROCESS_NAME" > /dev/null; then
        log "❌ 策略引擎未运行，正在重启..."
        restart_strategy_engine
    else
        local PID=$(pgrep -f "$PROCESS_NAME" | head -1)
        log "✅ 策略引擎运行中 (PID: $PID)"
        
        # 增加账户健康检查
        if ! check_account_health; then
            log "⚠️ 账户状态异常，正在重启策略引擎..."
            restart_strategy_engine
        fi
    fi
}

# 主循环
log "╔═══════════════════════════════════════════════════════════╗"
log "║       策略引擎看门狗 v2.0 启动                             ║"
log "╚═══════════════════════════════════════════════════════════╝"

while true; do
    check_and_restart || handle_error "检查失败"
    sleep 60
done
