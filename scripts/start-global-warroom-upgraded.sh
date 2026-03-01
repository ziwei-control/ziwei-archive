#!/bin/bash
# =============================================================================
# 全球战情室 - 升级版启动脚本
# 功能：启动全市场智能监控与精准推送系统
# =============================================================================

echo "🚀 启动全球战情室 - 升级版"
echo "📊 系统功能："
echo "   • 全市场加密货币监控（自主爬虫）"
echo "   • 全球股市动态捕获（SEC/港交所/证监会）"
echo "   • 社交媒体热度探针（DOM监控）"
echo "   • 双信源交叉验证机制"
echo "   • 内容指纹去重算法"
echo "   • Ignis专项监控（0.01美元阈值）"
echo ""

# 创建数据目录
mkdir -p /home/admin/Ziwei/data/warroom_v2

# 启动主程序（后台运行）
nohup python3 /home/admin/Ziwei/scripts/global-warroom-upgraded.py > /home/admin/Ziwei/data/logs/global-warroom-v2.log 2>&1 &

echo "✅ 全球战情室升级版已启动！"
echo "📄 日志文件: /home/admin/Ziwei/data/logs/global-warroom-v2.log"
echo "📧 警报邮箱: 19922307306@189.cn"
echo "🌐 监控范围: 全市场（不再局限于IGNIS/ARDR）"