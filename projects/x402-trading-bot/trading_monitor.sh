#!/bin/bash
# =============================================================================
# 交易机器人监控系统 v1.0
# 功能：定期检查系统健康状态，发送告警
# =============================================================================

# 配置
LOG_FILE="/home/admin/Ziwei/data/logs/soul-trader/trading_monitor.log"
ACCOUNT_FILE="/home/admin/Ziwei/data/strategy/account_status.json"
INTEL_DIR="/home/admin/Ziwei/data/intel"
SIGNAL_DIR="/home/admin/Ziwei/data/strategy"
TELEGRAM_CHAT_ID="8456624830"  # Martin 的 Telegram ID

# 告警阈值
BALANCE_MIN=100        # 最低余额告警线
INTEL_MAX_AGE=300      # 情报文件最大年龄（秒）
SIGNAL_MAX_AGE=180     # 信号文件最大年龄（秒）

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] $1" | tee -a "$LOG_FILE"
}

send_telegram_alert() {
    local message="$1"
    local bot_token_file="/home/admin/Ziwei/.telegram_bot_token"
    
    if [ -f "$bot_token_file" ]; then
        local BOT_TOKEN=$(cat "$bot_token_file")
        curl -s -X POST "https://api.telegram.org/bot$BOT_TOKEN/sendMessage" \
            -d "chat_id=$TELEGRAM_CHAT_ID" \
            -d "text=$message" \
            -d "parse_mode=Markdown" > /dev/null
    fi
}

check_account_status() {
    log "📊 检查账户状态..."
    
    if [ ! -f "$ACCOUNT_FILE" ]; then
        log "❌ 账户状态文件不存在"
        return 1
    fi
    
    # 读取余额
    local balance=$(jq -r '.balance // 0' "$ACCOUNT_FILE" 2>/dev/null)
    local positions=$(jq -r '.portfolio | length' "$ACCOUNT_FILE" 2>/dev/null)
    local total_trades=$(jq -r '.total_trades // 0' "$ACCOUNT_FILE" 2>/dev/null)
    
    if [ "$balance" = "null" ] || [ -z "$balance" ]; then
        log "❌ 无法读取账户余额"
        return 1
    fi
    
    # 检查余额是否过低
    local is_low=$(echo "$balance < $BALANCE_MIN" | bc -l 2>/dev/null || echo "0")
    if [ "$is_low" = "1" ]; then
        log "❌ 账户余额过低：$balance USDC (< $BALANCE_MIN)"
        send_telegram_alert "⚠️ *账户余额告警*\n\n余额：$balance USDC\n低于阈值：$BALANCE_MIN USDC\n\n请检查策略引擎状态。"
        return 1
    fi
    
    # 检查是否是科学计数法极小值
    if echo "$balance" | grep -qiE 'e-[0-9]{2,}'; then
        log "❌ 账户余额为科学计数法极小值：$balance"
        send_telegram_alert "🚨 *账户状态异常*\n\n余额：$balance\n检测到科学计数法极小值，可能是状态损坏。\n\n策略引擎将自动重启。"
        return 1
    fi
    
    log "✅ 账户状态正常 (余额：$balance USDC, 持仓：$positions 个，交易：$total_trades 次)"
    return 0
}

check_intel_files() {
    log "📡 检查情报文件..."
    
    local latest_intel=$(ls -t "$INTEL_DIR"/intel_*.json 2>/dev/null | head -1)
    
    if [ -z "$latest_intel" ]; then
        log "❌ 未找到情报文件"
        return 1
    fi
    
    local file_age=$(($(date +%s) - $(stat -c %Y "$latest_intel")))
    
    if [ "$file_age" -gt "$INTEL_MAX_AGE" ]; then
        log "❌ 情报文件过旧：${file_age}秒 (> ${INTEL_MAX_AGE}秒)"
        send_telegram_alert "⚠️ *情报收集器异常*\n\n最新情报文件：$latest_intel\n更新时间：${file_age}秒前\n\n阈值：${INTEL_MAX_AGE}秒"
        return 1
    fi
    
    log "✅ 情报文件正常 (最新：$(basename "$latest_intel"), ${file_age}秒前)"
    return 0
}

check_signal_files() {
    log "📈 检查信号文件..."
    
    local latest_signal=$(ls -t "$SIGNAL_DIR"/signals_*.json 2>/dev/null | head -1)
    
    if [ -z "$latest_signal" ]; then
        log "❌ 未找到信号文件"
        return 1
    fi
    
    local file_age=$(($(date +%s) - $(stat -c %Y "$latest_signal")))
    
    if [ "$file_age" -gt "$SIGNAL_MAX_AGE" ]; then
        log "❌ 信号文件过旧：${file_age}秒 (> ${SIGNAL_MAX_AGE}秒)"
        send_telegram_alert "⚠️ *策略引擎异常*\n\n最新信号文件：$latest_signal\n更新时间：${file_age}秒前\n\n阈值：${SIGNAL_MAX_AGE}秒"
        return 1
    fi
    
    log "✅ 信号文件正常 (最新：$(basename "$latest_signal"), ${file_age}秒前)"
    return 0
}

check_processes() {
    log "🔄 检查进程状态..."
    
    local intel_running=0
    local strategy_running=0
    local watchdog_running=0
    
    if pgrep -f "intel_collector.py" > /dev/null; then
        intel_running=1
        log "✅ 情报收集器运行中 (PID: $(pgrep -f intel_collector.py | head -1))"
    else
        log "❌ 情报收集器未运行"
    fi
    
    if pgrep -f "strategy_engine_v3.py" > /dev/null; then
        strategy_running=1
        log "✅ 策略引擎运行中 (PID: $(pgrep -f strategy_engine_v3.py | head -1))"
    else
        log "❌ 策略引擎未运行"
    fi
    
    if pgrep -f "strategy_watchdog.sh" > /dev/null; then
        watchdog_running=1
        log "✅ 看门狗运行中 (PID: $(pgrep -f strategy_watchdog.sh | head -1))"
    else
        log "❌ 看门狗未运行"
    fi
    
    if [ $intel_running -eq 0 ] || [ $strategy_running -eq 0 ]; then
        send_telegram_alert "🚨 *进程异常告警*\n\n情报收集器：$([ $intel_running -eq 1 ] && echo "✅" || echo "❌")\n策略引擎：$([ $strategy_running -eq 1 ] && echo "✅" || echo "❌")\n看门狗：$([ $watchdog_running -eq 1 ] && echo "✅" || echo "❌")\n\n请检查系统状态。"
        return 1
    fi
    
    return 0
}

generate_report() {
    local balance=$(jq -r '.balance // "N/A"' "$ACCOUNT_FILE" 2>/dev/null)
    local positions=$(jq -r '.portfolio | length' "$ACCOUNT_FILE" 2>/dev/null)
    local latest_intel=$(ls -t "$INTEL_DIR"/intel_*.json 2>/dev/null | head -1 | xargs basename 2>/dev/null || echo "N/A")
    local latest_signal=$(ls -t "$SIGNAL_DIR"/signals_*.json 2>/dev/null | head -1 | xargs basename 2>/dev/null || echo "N/A")
    
    log ""
    log "═══════════════════════════════════════════════════════"
    log "📊 交易系统健康报告 ($(date '+%Y-%m-%d %H:%M:%S'))"
    log "═══════════════════════════════════════════════════════"
    log "💰 账户余额：$balance USDC"
    log "📦 持仓数量：$positions 个"
    log "📡 最新情报：$latest_intel"
    log "📈 最新信号：$latest_signal"
    log "═══════════════════════════════════════════════════════"
}

# 主函数
main() {
    log "╔═══════════════════════════════════════════════════════╗"
    log "║       交易系统健康检查启动                             ║"
    log "╚═══════════════════════════════════════════════════════╝"
    
    local errors=0
    
    check_processes || ((errors++))
    check_account_status || ((errors++))
    check_intel_files || ((errors++))
    check_signal_files || ((errors++))
    
    if [ $errors -eq 0 ]; then
        log "✅ 所有检查通过，系统运行正常"
    else
        log "⚠️ 发现 $errors 个问题，已发送告警"
    fi
    
    generate_report
    
    return $errors
}

# 执行
main
