#!/bin/bash
# 打开仓库创建页面

REPO_NAME="ziwei-audit-system"
REPO_DESC="紫微智控 - 全面自动化审计系统"
LOCAL_PATH="/home/admin/Ziwei/projects/ziwei-audit-system"

echo "=========================================="
echo "🌐 打开仓库创建页面"
echo "=========================================="
echo

# 检查是否有浏览器
if command -v xdg-open &> /dev/null; then
    echo "📱 正在打开 GitHub 创建页面..."
    xdg-open "https://github.com/new?name=$REPO_NAME&description=$REPO_DESC" &
    
    sleep 2
    
    echo "📱 正在打开 Gitee 创建页面..."
    xdg-open "https://gitee.com/new?name=$REPO_NAME&description=$REPO_DESC" &
    
    echo
    echo "✅ 已在浏览器中打开创建页面"
    echo
    echo "📝 填写说明:"
    echo "  1. 仓库名：$REPO_NAME"
    echo "  2. 描述：$REPO_DESC"
    echo "  3. 可见性：Public ✅"
    echo "  4. 点击创建"
    echo
    echo "🚀 创建完成后执行:"
    echo "  cd $LOCAL_PATH"
    echo "  git push github main"
    echo "  git push gitee main"
    echo
elif command -v curl &> /dev/null; then
    echo "⚠️  无图形界面，请手动访问:"
    echo
    echo "  GitHub: https://github.com/new?name=$REPO_NAME"
    echo "  Gitee:  https://gitee.com/new?name=$REPO_NAME"
    echo
else
    echo "📍 请手动访问:"
    echo "  GitHub: https://github.com/new"
    echo "  Gitee:  https://gitee.com/new"
    echo
fi
