#!/bin/bash
# =============================================================================
# log-trim 安装脚本
# 功能：安装日志修剪工具到系统
# =============================================================================

set -e

Ziwei_DIR="/home/admin/Ziwei"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "╔════════════════════════════════════════════════════════╗"
echo "║          log-trim 安装脚本                             ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# 1. 复制脚本
echo "📦 复制脚本..."
cp "$SCRIPT_DIR/log-trim.py" "$Ziwei_DIR/scripts/log-trim.py"
chmod +x "$Ziwei_DIR/scripts/log-trim.py"
echo "  ✅ 脚本已复制到：$Ziwei_DIR/scripts/log-trim.py"
echo ""

# 2. 创建系统命令
echo "🔧 创建系统命令..."
cat > /usr/local/bin/log-trim << 'EOF'
#!/bin/bash
exec python3 /home/admin/Ziwei/scripts/log-trim.py "$@"
EOF
chmod +x /usr/local/bin/log-trim
echo "  ✅ 命令已安装：/usr/local/bin/log-trim"
echo ""

# 3. 安装 systemd 服务
echo "📋 安装 systemd 服务..."
cp "$SCRIPT_DIR/log-trim.service" /etc/systemd/system/log-trim.service
systemctl daemon-reload
echo "  ✅ 服务已安装：log-trim.service"
echo ""

# 4. 启动服务
echo "🚀 启动服务..."
systemctl enable log-trim
systemctl restart log-trim
echo "  ✅ 服务已启动"
echo ""

# 5. 验证
echo "📊 验证安装..."
sleep 2
systemctl status log-trim --no-pager | head -10
echo ""

# 6. 测试命令
echo "🧪 测试命令..."
log-trim status
echo ""

echo "╔════════════════════════════════════════════════════════╗"
echo "║          ✅ log-trim 安装完成！                        ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "📋 常用命令:"
echo "  log-trim status   - 查看状态"
echo "  log-trim check    - 检查并修剪"
echo "  log-trim watch    - 监控模式"
echo "  log-trim trim     - 立即修剪"
echo ""
echo "🔧 服务管理:"
echo "  systemctl status log-trim   - 查看服务状态"
echo "  systemctl stop log-trim     - 停止服务"
echo "  systemctl start log-trim    - 启动服务"
echo "  systemctl restart log-trim  - 重启服务"
echo ""
echo "📝 日志查看:"
echo "  journalctl -u log-trim -f   - 实时查看服务日志"
echo "  cat /home/admin/Ziwei/data/logs/log_trim.log"
echo ""
