#!/bin/bash
# =============================================================================
# 紫微智控 - 双平台同步脚本（GitHub + Gitee）
# 用途：同时推送到 GitHub 和 Gitee
# =============================================================================

set -e

Ziwei_DIR="/home/admin/Ziwei"
cd "$Ziwei_DIR"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║          紫微智控 - 双平台同步 (GitHub + Gitee)         ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# =============================================================================
# 步骤 1: 加载配置
# =============================================================================
echo -e "${YELLOW}[1/5] 加载配置...${NC}"

if [ ! -f ".env" ]; then
    echo -e "${RED}✗ 错误：.env 文件不存在${NC}"
    exit 1
fi

# 读取配置
GITHUB_TOKEN=$(grep "GITHUB_TOKEN" .env | cut -d'"' -f2)
GITHUB_REPO=$(grep "GITHUB_REPO" .env | cut -d'"' -f2)
GITEE_TOKEN=$(grep "GITEE_TOKEN" .env | cut -d'"' -f2)
GITEE_REPO=$(grep "GITEE_REPO" .env | cut -d'"' -f2)

# 验证配置
if [ -z "$GITHUB_TOKEN" ] || [ "$GITHUB_TOKEN" = "your_github_token_here" ]; then
    echo -e "${RED}✗ 错误：GitHub Token 未配置${NC}"
    echo "  请编辑 .env 文件填写 GITHUB_TOKEN"
    exit 1
fi

if [ -z "$GITEE_TOKEN" ] || [ "$GITEE_TOKEN" = "your_gitee_token_here" ]; then
    echo -e "${YELLOW}! 警告：Gitee Token 未配置${NC}"
    echo "  将只推送到 GitHub"
    GITEE_ENABLED=false
else
    GITEE_ENABLED=true
fi

echo -e "  ${GREEN}✓${NC} GitHub 配置：已加载"
if [ "$GITEE_ENABLED" = true ]; then
    echo -e "  ${GREEN}✓${NC} Gitee 配置：已加载"
fi

echo ""

# =============================================================================
# 步骤 2: Git 状态检查
# =============================================================================
echo -e "${YELLOW}[2/5] 检查 Git 状态...${NC}"

# 检查是否是 git 仓库
if [ ! -d ".git" ]; then
    echo -e "${YELLOW}! 初始化 Git 仓库...${NC}"
    git init
    git config user.name "Martin"
    git config user.email "pandac00@163.com"
fi

# 检查是否有更改
CHANGED=$(git status --porcelain | wc -l)
if [ "$CHANGED" -gt 0 ]; then
    echo -e "  ${YELLOW}!${NC} 发现 $CHANGED 个文件有更改"
    read -p "  是否提交这些更改？(y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git add .
        git commit -m "自动提交：$(date '+%Y-%m-%d %H:%M:%S')"
        echo -e "  ${GREEN}✓${NC} 已提交更改"
    fi
else
    echo -e "  ${GREEN}✓${NC} 没有未提交的更改"
fi

echo ""

# =============================================================================
# 步骤 3: 推送到 GitHub
# =============================================================================
echo -e "${YELLOW}[3/5] 推送到 GitHub...${NC}"

# 设置 GitHub remote
git remote get-url github >/dev/null 2>&1 || git remote add github "$GITHUB_REPO"
git remote set-url github "https://$GITHUB_TOKEN@github.com/${GITHUB_REPO#*github.com/}"

# 确保在 main 分支
git branch -M main 2>/dev/null

# 推送
if git push -u github main 2>&1 | tee /tmp/push_github.log; then
    echo -e "  ${GREEN}✓${NC} GitHub 推送成功"
    GITHUB_SUCCESS=true
else
    echo -e "  ${RED}✗${NC} GitHub 推送失败"
    GITHUB_SUCCESS=false
fi

echo ""

# =============================================================================
# 步骤 4: 推送到 Gitee
# =============================================================================
if [ "$GITEE_ENABLED" = true ]; then
    echo -e "${YELLOW}[4/5] 推送到 Gitee...${NC}"
    
    # 设置 Gitee remote
    git remote get-url gitee >/dev/null 2>&1 || git remote add gitee "$GITEE_REPO"
    git remote set-url gitee "https://$GITEE_TOKEN@gitee.com/${GITEE_REPO#*gitee.com/}"
    
    # 推送
    if git push -u gitee main 2>&1 | tee /tmp/push_gitee.log; then
        echo -e "  ${GREEN}✓${NC} Gitee 推送成功"
        GITEE_SUCCESS=true
    else
        echo -e "  ${RED}✗${NC} Gitee 推送失败"
        GITEE_SUCCESS=false
    fi
else
    echo -e "${YELLOW}[4/5] 跳过 Gitee 推送（Token 未配置）${NC}"
    GITEE_SUCCESS=false
fi

echo ""

# =============================================================================
# 步骤 5: 生成报告
# =============================================================================
echo -e "${YELLOW}[5/5] 生成同步报告...${NC}"
echo ""

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    同步报告                            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

if [ "$GITHUB_SUCCESS" = true ]; then
    echo -e "  GitHub: ${GREEN}✓ 成功${NC}"
    echo -e "    地址：$GITHUB_REPO"
else
    echo -e "  GitHub: ${RED}✗ 失败${NC}"
fi

echo ""

if [ "$GITEE_ENABLED" = true ]; then
    if [ "$GITEE_SUCCESS" = true ]; then
        echo -e "  Gitee:  ${GREEN}✓ 成功${NC}"
        echo -e "    地址：$GITEE_REPO"
    else
        echo -e "  Gitee:  ${RED}✗ 失败${NC}"
    fi
else
    echo -e "  Gitee:  ${YELLOW}! 未配置${NC}"
fi

echo ""

# 保存报告
cat > "$Ziwei_DIR/data/logs/sync_report_$(date +%Y%m%d_%H%M%S).md" << EOF
# 紫微智控同步报告

**时间**: $(date '+%Y-%m-%d %H:%M:%S')

## 推送结果

| 平台 | 状态 | 地址 |
|------|------|------|
| GitHub | $([ "$GITHUB_SUCCESS" = true ] && echo "✅ 成功" || echo "❌ 失败") | $GITHUB_REPO |
| Gitee | $([ "$GITEE_SUCCESS" = true ] && echo "✅ 成功" || echo "❌ 失败") | $GITEE_REPO |

## 提交统计

**提交数**: $(git rev-list --count HEAD)
**最后提交**: $(git log -1 --format="%s")
**文件大小**: $(du -sh "$Ziwei_DIR/.git" | cut -f1)
EOF

echo -e "${GREEN}✓${NC} 同步报告已保存"
echo "  data/logs/sync_report_$(date +%Y%m%d_%H%M%S).md"
echo ""

# =============================================================================
# 完成
# =============================================================================
if [ "$GITHUB_SUCCESS" = true ] && { [ "$GITEE_ENABLED" = false ] || [ "$GITEE_SUCCESS" = true ]; }; then
    echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║              ✅ 双平台同步完成！                       ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
    exit 0
else
    echo -e "${RED}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║              ⚠️  部分推送失败                          ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════════════════════╝${NC}"
    exit 1
fi
