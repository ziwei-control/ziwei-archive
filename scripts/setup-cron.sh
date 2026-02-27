#!/bin/bash
# =============================================================================
# 紫微智控 - Cron 定时任务配置脚本
# 功能：
#   1. 配置每日 23:40 自动同步
#   2. 配置每 30 分钟巡查
# =============================================================================

set -e

Ziwei_DIR="/home/admin/Ziwei"
SCRIPTS_DIR="$Ziwei_DIR/scripts"
CRON_FILE="/etc/cron.d/ziwei-sync"

echo "╔════════════════════════════════════════════════════════╗"
echo "║          紫微智控 - Cron 定时任务配置                   ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# 检查是否 root
if [ "$EUID" -ne 0 ]; then 
    echo "⚠️  请使用 sudo 运行此脚本"
    echo "  sudo bash $0"
    exit 1
fi

# 检查 cron 是否安装
echo "1️⃣ 检查 Cron 服务..."
if ! command -v crontab &> /dev/null; then
    echo "  ✗ Cron 未安装"
    echo "  请运行：yum install -y cronie"
    exit 1
fi

echo "  ✓ Cron 已安装"

# 检查 cron 服务状态
if systemctl is-active --quiet crond 2>/dev/null || systemctl is-active --quiet cron 2>/dev/null; then
    echo "  ✓ Cron 服务运行中"
else
    echo "  ! Cron 服务未运行，尝试启动..."
    systemctl start crond 2>/dev/null || systemctl start cron 2>/dev/null || echo "  ⚠️  启动失败"
fi

echo ""

# 创建 cron 配置文件
echo "2️⃣ 创建 Cron 配置文件..."

cat > "$CRON_FILE" << EOF
# 紫微智控 - 自动同步定时任务（容错版）
# 创建时间：$(date '+%Y-%m-%d %H:%M:%S')

SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
MAILTO=""

# 每 30 分钟巡查一次（发现更改自动同步）
*/30 * * * * root cd $Ziwei_DIR && /usr/bin/python3 $SCRIPTS_DIR/auto-sync-watchdog.py >> $Ziwei_DIR/data/logs/cron_watchdog.log 2>&1

# 每 10 分钟重试失败的同步
*/10 * * * * root cd $Ziwei_DIR && /usr/bin/bash $SCRIPTS_DIR/retry-failed-sync.sh >> $Ziwei_DIR/data/logs/cron_retry.log 2>&1

# 每日 23:40 强制同步（确保最终一致性）
40 23 * * * root cd $Ziwei_DIR && /usr/bin/bash $SCRIPTS_DIR/sync-to-both.sh >> $Ziwei_DIR/data/logs/cron_daily_sync.log 2>&1
EOF

echo "  ✓ Cron 配置文件已创建：$CRON_FILE"
echo ""
echo "  配置内容:"
cat "$CRON_FILE"
echo ""

# 设置权限
echo "3️⃣ 设置权限..."
chmod 644 "$CRON_FILE"
echo "  ✓ 权限已设置 (644)"

# 重启 cron 服务
echo "4️⃣ 重启 Cron 服务..."
systemctl restart crond 2>/dev/null || systemctl restart cron 2>/dev/null || echo "  ⚠️  重启失败"
systemctl enable crond 2>/dev/null || systemctl enable cron 2>/dev/null || echo "  ⚠️  启用失败"
echo "  ✓ Cron 服务已重启"

echo ""

# 验证
echo "5️⃣ 验证配置..."
echo ""
echo "  当前 Cron 任务:"
crontab -l 2>/dev/null || echo "  (系统 crontab)"
echo ""
echo "  Cron 服务状态:"
systemctl status crond --no-pager 2>/dev/null | grep -E "Active|Loaded" || systemctl status cron --no-pager 2>/dev/null | grep -E "Active|Loaded" || echo "  无法获取状态"

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║          ✅ Cron 定时任务配置完成！                    ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "📋 定时任务说明:"
echo ""
echo "  1. 每 30 分钟巡查"
echo "     - 检查文件更改"
echo "     - 自动同步到 GitHub + Gitee"
echo "     - 日志：data/logs/cron_watchdog.log"
echo ""
echo "  2. 每日 23:40 强制同步"
echo "     - 无论有无更改都同步"
echo "     - 日志：data/logs/cron_daily_sync.log"
echo ""
echo "🔧 管理命令:"
echo ""
echo "  # 查看日志"
echo "  tail -f $Ziwei_DIR/data/logs/cron_watchdog.log"
echo "  tail -f $Ziwei_DIR/data/logs/cron_daily_sync.log"
echo ""
echo "  # 查看 Cron 状态"
echo "  systemctl status crond"
echo ""
echo "  # 重启 Cron"
echo "  systemctl restart crond"
echo ""
echo "  # 禁用定时任务"
echo "  rm $CRON_FILE"
echo "  systemctl restart crond"
echo ""
