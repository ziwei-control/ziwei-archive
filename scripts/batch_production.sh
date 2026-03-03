#!/bin/bash
# 紫微制造 - 批量生产脚本
# 自动生产 5 个变现项目

echo "========================================"
echo "🏭 紫微制造 - 批量生产"
echo "========================================"

TASKS=(
    "CRYPTO-WALLET-TRACKER-001"
    "SOCIAL-AUTO-POST-001"
    "AI-CODE-ASSISTANT-001"
    "DATA-CONVERTER-PRO-001"
    "FILE-BATCH-PROCESSOR-001"
)

cd /home/admin/Ziwei

for i in "${!TASKS[@]}"; do
    task="${TASKS[$i]}"
    num=$((i+1))
    
    echo ""
    echo "========================================"
    echo "📦 生产进度：$num/5"
    echo "项目：$task"
    echo "========================================"
    
    # 运行紫微制造
    python3 scripts/wisdom_creator.py "tasks/$task/spec.md"
    
    if [ $? -eq 0 ]; then
        echo "✅ $task 生产完成"
    else
        echo "❌ $task 生产失败"
    fi
    
    # 等待 5 秒
    sleep 5
done

echo ""
echo "========================================"
echo "🎉 批量生产完成"
echo "========================================"
echo ""
echo "生产的项目:"
for task in "${TASKS[@]}"; do
    echo "  ✅ tasks/$task/"
done
echo ""
echo "下一步:"
echo "  1. 测试每个项目"
echo "  2. 优化和定制"
echo "  3. 准备上架材料"
echo "  4. 发布到 CodeCanyon 等平台"
