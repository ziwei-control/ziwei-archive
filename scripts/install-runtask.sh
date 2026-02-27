#!/bin/bash
# =============================================================================
# 紫微智控 - 安装 runtask 命令
# =============================================================================

echo "╔════════════════════════════════════════════════════════╗"
echo "║          紫微智控 - 安装 runtask 命令                  ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# 检查 root 权限
if [ "$EUID" -ne 0 ]; then 
    echo "⚠️  请使用 sudo 运行此脚本"
    echo "  sudo bash $0"
    exit 1
fi

# 创建符号链接
echo "📦 创建快捷命令..."
ln -sf /home/admin/Ziwei/scripts/run-task.sh /usr/local/bin/runtask
chmod +x /usr/local/bin/runtask
echo "  ✓ 符号链接已创建：/usr/local/bin/runtask"

# 配置权限
echo ""
echo "🔧 配置权限..."
chmod +x /home/admin/Ziwei/scripts/run-task.sh
chmod -R 755 /home/admin/Ziwei/scripts/
chmod -R 755 /home/admin/Ziwei/docs/
chmod -R 755 /home/admin/Ziwei/config/
chmod -R 777 /home/admin/Ziwei/data/
chmod -R 777 /home/admin/Ziwei/projects/
echo "  ✓ 权限已配置"

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║              ✅ 安装完成！                             ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "使用方法:"
echo "  runtask                                    # 交互式模式"
echo "  runtask TASK-XXX \"名称\" \"描述\"           # 命令行模式"
echo ""
echo "示例:"
echo "  runtask"
echo "  runtask TASK-20250227-001 \"计算器项目\" \"Python 计算器\""
echo ""
echo "卸载命令:"
echo "  sudo bash /home/admin/Ziwei/scripts/uninstall-runtask.sh"
echo ""
