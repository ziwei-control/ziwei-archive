#!/bin/bash
# =============================================================================
# 紫微智控 - 失败同步重试脚本
# 功能：检查失败记录，自动重试失败的同步
# =============================================================================

Ziwei_DIR="/home/admin/Ziwei"
cd "$Ziwei_DIR"

FAIL_LOG="$Ziwei_DIR/data/logs/sync_failures.log"

echo "╔════════════════════════════════════════════════════════╗"
echo "║          紫微智控 - 失败同步重试                       ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# 检查失败日志
if [ ! -f "$FAIL_LOG" ]; then
    echo "✅ 没有失败记录"
    exit 0
fi

# 读取失败记录
FAILED_LINES=$(wc -l < "$FAIL_LOG")
if [ "$FAILED_LINES" -eq 0 ]; then
    echo "✅ 没有失败记录"
    exit 0
fi

echo "📋 发现 $FAILED_LINES 条失败记录"
echo ""

# 统计失败类型
GITHUB_FAILS=$(grep -c "GITHUB_PUSH_FAILED" "$FAIL_LOG" 2>/dev/null || echo 0)
GITEE_FAILS=$(grep -c "GITEE_PUSH_FAILED" "$FAIL_LOG" 2>/dev/null || echo 0)

echo "失败统计:"
echo "  GitHub: $GITHUB_FAILS 次"
echo "  Gitee:  $GITEE_FAILS 次"
echo ""

# 重试同步
echo "🔄 开始重试同步..."
echo ""

bash scripts/sync-to-both.sh

# 如果重试成功，清理失败日志
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 重试成功，清理失败日志..."
    > "$FAIL_LOG"
    echo "✓ 失败日志已清空"
else
    echo ""
    echo "⚠️  重试仍有失败，保留失败日志"
    echo "   将在下次定时同步时继续重试"
fi

echo ""
echo "✅ 失败重试完成"
