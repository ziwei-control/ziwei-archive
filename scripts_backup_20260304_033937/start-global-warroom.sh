#!/bin/bash
# =============================================================================
# 全球战情室 - 启动脚本
# 功能：启动完整的监控和分析系统
# =============================================================================

echo "🚀 启动全球战情室系统..."

# 启动加密货币监控
python3 /home/admin/Ziwei/scripts/crypto-monitor.py &

# 启动股票市场监控  
python3 /home/admin/Ziwei/scripts/stock-analysis.py &

# 启动 Web3 智能钱包助手
python3 /home/admin/Ziwei/scripts/web3-wallet-assistant.py &

# 启动邮件通知系统
python3 /home/admin/Ziwei/scripts/email-notifier.py &

# 启动主战情室仪表盘
python3 /home/admin/Ziwei/scripts/global-warroom.py &

echo "✅ 全球战情室系统已启动！"
echo "🌐 仪表盘地址: http://your-server-ip:8080"
echo "📧 邮件通知: 19922307306@189.cn"