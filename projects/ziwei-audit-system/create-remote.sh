#!/bin/bash
# 自动创建 GitHub 和 Gitee 仓库并推送

REPO_NAME="ziwei-audit-system"
REPO_DESC="紫微智控 - 全面自动化审计系统"
LOCAL_PATH="/home/admin/Ziwei/projects/ziwei-audit-system"

echo "=========================================="
echo "🚀 自动创建远程仓库并推送"
echo "=========================================="
echo

# 检查是否在正确的目录
cd "$LOCAL_PATH" || exit 1

echo "📂 本地项目路径：$LOCAL_PATH"
echo

# 尝试使用 gh CLI 创建 GitHub 仓库
if command -v gh &> /dev/null; then
    echo "✅ 检测到 GitHub CLI"
    echo "📦 创建 GitHub 仓库..."
    gh repo create "$REPO_NAME" --public --description "$REPO_DESC" --source=. --remote=github --push
    echo "✅ GitHub 仓库创建成功"
else
    echo "⚠️  未安装 GitHub CLI"
    echo "   请手动创建：https://github.com/new"
    echo "   仓库名：$REPO_NAME"
fi

echo

# 尝试使用 gitee CLI 创建 Gitee 仓库
if command -v gitee &> /dev/null; then
    echo "✅ 检测到 Gitee CLI"
    echo "📦 创建 Gitee 仓库..."
    gitee create repo "$REPO_NAME" --description "$REPO_DESC" --public
    git remote add gitee git@gitee.com:ziwei-control/$REPO_NAME.git 2>/dev/null || true
    git push -u gitee main
    echo "✅ Gitee 仓库创建成功"
else
    echo "⚠️  未安装 Gitee CLI"
    echo "   请手动创建：https://gitee.com/new"
    echo "   仓库名：$REPO_NAME"
fi

echo
echo "=========================================="
echo "✅ 完成"
echo "=========================================="
echo
echo "📍 仓库地址:"
echo "  GitHub: https://github.com/ziwei-control/$REPO_NAME"
echo "  Gitee:  https://gitee.com/ziwei-control/$REPO_NAME"
echo
