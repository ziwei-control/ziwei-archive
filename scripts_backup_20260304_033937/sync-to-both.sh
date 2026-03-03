#!/bin/bash
# =============================================================================
# 紫微智控 - 双平台同步脚本（容错版）
# 策略：即使一个平台失败也不阻塞，定时自动重试
# =============================================================================

Ziwei_DIR="/home/admin/Ziwei"
cd "$Ziwei_DIR"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║          紫微智控 - 双平台同步 (容错版)                ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# 初始化状态
GITHUB_SUCCESS=false
GITEE_SUCCESS=false

# =============================================================================
# 步骤 1: 加载配置
# =============================================================================
echo -e "${YELLOW}[1/5] 加载配置...${NC}"

if [ ! -f ".env" ]; then
    echo -e "${RED}✗ 错误：.env 文件不存在${NC}"
    exit 1
fi

# 读取配置（纯 SSH 方式）
GITHUB_REPO=$(grep "^GITHUB_REPO" .env 2>/dev/null | grep -v "^#" | cut -d'"' -f2)
GITEE_REPO_SSH=$(grep "^GITEE_REPO_SSH" .env 2>/dev/null | grep -v "^#" | cut -d'"' -f2)

# 检测认证方式（仅 SSH）
GITHUB_USE_SSH=false
GITEE_USE_SSH=false
GITEE_ENABLED=false

# 检查 GitHub
if [[ "$GITHUB_REPO" == *"git@github.com"* ]]; then
    GITHUB_USE_SSH=true
    echo -e "  ${GREEN}✓${NC} GitHub 认证方式：SSH"
else
    echo -e "  ${YELLOW}!${NC} GitHub SSH：未配置"
fi

# 检查 Gitee（仅 SSH）
if [[ "$GITEE_REPO_SSH" == *"git@gitee.com"* ]]; then
    GITEE_USE_SSH=true
    GITEE_ENABLED=true
    echo -e "  ${GREEN}✓${NC} Gitee 认证方式：SSH"
else
    echo -e "  ${YELLOW}!${NC} Gitee SSH：未配置"
fi

echo ""

# =============================================================================
# 步骤 2: Git 状态检查
# =============================================================================
echo -e "${YELLOW}[2/5] 检查 Git 状态...${NC}"

if [ ! -d ".git" ]; then
    echo -e "${YELLOW}! 初始化 Git 仓库...${NC}"
    git init -q
    git config user.name "Martin"
    git config user.email "pandac00@163.com"
fi

CHANGED=$(git status --porcelain 2>/dev/null | wc -l)
if [ "$CHANGED" -gt 0 ]; then
    echo -e "  ${YELLOW}!${NC} 发现 $CHANGED 个文件有更改"
    git add .
    git commit -q -m "自动提交：$(date '+%Y-%m-%d %H:%M:%S')"
    echo -e "  ${GREEN}✓${NC} 已提交更改"
else
    echo -e "  ${GREEN}✓${NC} 没有未提交的更改"
fi

echo ""

# =============================================================================
# 步骤 3: 推送到 GitHub（容错）
# =============================================================================
echo -e "${YELLOW}[3/5] 推送到 GitHub...${NC}"

if [[ "$GITHUB_REPO" == *"git@github.com"* ]] || [ -n "$GITHUB_TOKEN" ]; then
    # 设置 remote
    git remote get-url github >/dev/null 2>&1 || git remote add github "$GITHUB_REPO"
    
    if [[ "$GITHUB_REPO" == *"git@github.com"* ]]; then
        git remote set-url github "$GITHUB_REPO"
    else
        git remote set-url github "https://$GITHUB_TOKEN@github.com/${GITHUB_REPO#*github.com/}"
    fi
    
    git branch -M main 2>/dev/null
    
    # 推送（超时 30 秒，失败不退出）
    if timeout 30 git push -u github main >/dev/null 2>&1; then
        echo -e "  ${GREEN}✓${NC} GitHub 推送成功"
        GITHUB_SUCCESS=true
    else
        echo -e "  ${YELLOW}!${NC} GitHub 推送失败（将继续执行，稍后重试）"
        GITHUB_SUCCESS=false
        # 记录失败
        echo "$(date -Iseconds) GITHUB_PUSH_FAILED" >> "$Ziwei_DIR/data/logs/sync_failures.log"
    fi
else
    echo -e "  ${YELLOW}!${NC} GitHub 未配置，跳过"
fi

echo ""

# =============================================================================
# 步骤 4: 推送到 Gitee（容错）
# =============================================================================
echo -e "${YELLOW}[4/5] 推送到 Gitee...${NC}"

if [ "$GITEE_ENABLED" = true ]; then
    # 仅使用 SSH 方式
    git remote get-url gitee >/dev/null 2>&1 || git remote add gitee "$GITEE_REPO_SSH"
    git remote set-url gitee "$GITEE_REPO_SSH"
    
    # 推送（超时 30 秒，失败不退出）
    if timeout 30 git push -u gitee main >/dev/null 2>&1; then
        echo -e "  ${GREEN}✓${NC} Gitee 推送成功"
        GITEE_SUCCESS=true
    else
        echo -e "  ${YELLOW}!${NC} Gitee 推送失败（将继续执行，稍后重试）"
        GITEE_SUCCESS=false
        # 记录失败
        echo "$(date -Iseconds) GITEE_PUSH_FAILED" >> "$Ziwei_DIR/data/logs/sync_failures.log"
    fi
else
    echo -e "  ${YELLOW}!${NC} Gitee SSH 未配置，跳过"
fi

echo ""

# =============================================================================
# 步骤 5: 生成报告
# =============================================================================
echo -e "${YELLOW}[5/5] 生成同步报告...${NC}"

# 确定整体状态
if [ "$GITHUB_SUCCESS" = true ] && [ "$GITEE_SUCCESS" = true ]; then
    STATUS="完全成功"
    EXIT_CODE=0
elif [ "$GITHUB_SUCCESS" = true ] || [ "$GITEE_SUCCESS" = true ]; then
    STATUS="部分成功（已继续执行）"
    EXIT_CODE=0  # 部分成功也返回成功，不阻塞流程
else
    STATUS="全部失败"
    EXIT_CODE=1
fi

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    同步报告                            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "状态：${STATUS}"
echo ""

if [ "$GITHUB_SUCCESS" = true ]; then
    echo -e "  GitHub: ${GREEN}✓ 成功${NC}"
else
    echo -e "  GitHub: ${YELLOW}! 失败（将在下次定时同步重试）${NC}"
fi

if [ "$GITEE_ENABLED" = true ]; then
    if [ "$GITEE_SUCCESS" = true ]; then
        echo -e "  Gitee:  ${GREEN}✓ 成功${NC}"
    else
        echo -e "  Gitee:  ${YELLOW}! 失败（将在下次定时同步重试）${NC}"
    fi
else
    echo -e "  Gitee:  ${YELLOW}- 未配置${NC}"
fi

echo ""

# 保存报告
REPORT_FILE="$Ziwei_DIR/data/logs/sync_report_$(date +%Y%m%d_%H%M%S).md"
cat > "$REPORT_FILE" << EOF
# 紫微智控同步报告

**时间**: $(date '+%Y-%m-%d %H:%M:%S')

## 同步状态

**整体状态**: $STATUS

## 平台状态

| 平台 | 状态 | 说明 |
|------|------|------|
| GitHub | $([ "$GITHUB_SUCCESS" = true ] && echo "✅ 成功" || echo "⚠️ 失败（待重试）") | $( [ "$GITHUB_SUCCESS" = true ] && echo "已推送" || echo "推送失败，将在下次定时同步重试") |
| Gitee | $([ "$GITEE_SUCCESS" = true ] && echo "✅ 成功" || echo "⚠️ 失败（待重试）") | $( [ "$GITEE_SUCCESS" = true ] && echo "已推送" || echo "推送失败，将在下次定时同步重试") |

## 重试机制

- **失败记录**: \`data/logs/sync_failures.log\`
- **下次重试**: 每 30 分钟自动巡查
- **强制重试**: 每日 23:40 强制同步

## 策略说明

✅ **即使一个平台失败也不阻塞流程**
- 成功的平台立即推送
- 失败的平台记录到失败日志
- 定时巡查自动重试失败的平台
- 每日 23:40 强制同步确保最终一致性
EOF

echo -e "${GREEN}✓${NC} 报告已保存：$REPORT_FILE"
echo ""

# =============================================================================
# 完成
# =============================================================================
if [ "$EXIT_CODE" -eq 0 ]; then
    echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║              ✅ 同步完成（容错模式）                   ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
    echo ""
    if [ "$GITHUB_SUCCESS" = false ] || [ "$GITEE_SUCCESS" = false ]; then
        echo -e "${YELLOW}⚠️  部分平台失败，将在下次定时同步时自动重试${NC}"
        echo ""
    fi
    exit 0
else
    echo -e "${RED}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║              ⚠️  全部失败，但不会阻塞流程              ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${YELLOW}将在下次定时同步时自动重试${NC}"
    echo ""
    exit 0  # 即使全部失败也返回 0，不阻塞流程
fi
