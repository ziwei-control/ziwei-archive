#!/bin/bash
# 紫微智控 - 服务管理脚本

SERVICES=(
    "ziwei-warroom"
    "ziwei-x402-api"
    "ziwei-trading-bot"
    "ziwei-sync-watchdog"
    "ziwei-log-trim"
)

case "$1" in
    start)
        echo "🚀 启动所有紫微智控服务..."
        systemctl start ${SERVICES[@]}
        ;;
    stop)
        echo "🛑 停止所有紫微智控服务..."
        systemctl stop ${SERVICES[@]}
        ;;
    restart)
        echo "🔄 重启所有紫微智控服务..."
        systemctl restart ${SERVICES[@]}
        ;;
    status)
        echo "📊 服务状态:"
        systemctl status ${SERVICES[@]} --no-pager | grep -E "●|Active:"
        ;;
    enable)
        echo "✅ 设置开机自启..."
        systemctl enable ${SERVICES[@]}
        ;;
    disable)
        echo "❌ 禁用开机自启..."
        systemctl disable ${SERVICES[@]}
        ;;
    logs)
        echo "📋 查看日志:"
        journalctl -u ${SERVICES[@]} -f --no-pager
        ;;
    *)
        echo "紫微智控 - 服务管理脚本"
        echo ""
        echo "用法：$0 {start|stop|restart|status|enable|disable|logs}"
        echo ""
        echo "命令说明:"
        echo "  start   - 启动所有服务"
        echo "  stop    - 停止所有服务"
        echo "  restart - 重启所有服务"
        echo "  status  - 查看服务状态"
        echo "  enable  - 设置开机自启"
        echo "  disable - 禁用开机自启"
        echo "  logs    - 查看日志 (实时)"
        ;;
esac
