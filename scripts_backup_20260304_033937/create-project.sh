#!/bin/bash
# =============================================================================
# 紫微智控 - 自动创建项目脚本
# 功能：为每个新任务在 GitHub 和 Gitee 创建新项目
# =============================================================================

set -e

Ziwei_DIR="/home/admin/Ziwei"
cd "$Ziwei_DIR"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║          紫微智控 - 自动创建项目                       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# =============================================================================
# 参数解析
# =============================================================================
TASK_ID="$1"
TASK_NAME="$2"
TASK_DESC="$3"

if [ -z "$TASK_ID" ]; then
    echo -e "${RED}✗ 错误：缺少任务 ID${NC}"
    echo "  用法：$0 <任务 ID> <任务名称> [任务描述]"
    echo "  示例：$0 TASK-20250227-001 \"计算器项目\" \"创建一个 Python 计算器\""
    exit 1
fi

if [ -z "$TASK_NAME" ]; then
    TASK_NAME="紫微智控-$TASK_ID"
fi

if [ -z "$TASK_DESC" ]; then
    TASK_DESC="紫微智控项目：$TASK_NAME"
fi

echo -e "${YELLOW}[信息] 任务信息:${NC}"
echo "  ID: $TASK_ID"
echo "  名称：$TASK_NAME"
echo "  描述：$TASK_DESC"
echo ""

# =============================================================================
# 加载配置
# =============================================================================
echo -e "${YELLOW}[1/4] 加载配置...${NC}"

# 读取 Token
GITHUB_TOKEN=$(grep "^GITHUB_TOKEN" .env | grep -v "^#" | cut -d'"' -f2)
GITEE_TOKEN=$(grep "^GITEE_TOKEN" .env | grep -v "^#" | cut -d'"' -f2)

# 读取用户名
GITHUB_USER="ziwei-control"
GITEE_USER="pandac0"

if [ -z "$GITHUB_TOKEN" ]; then
    echo -e "${RED}✗ 错误：GitHub Token 未配置${NC}"
    exit 1
fi

echo -e "  ${GREEN}✓${NC} 配置已加载"
echo ""

# =============================================================================
# 创建 GitHub 仓库
# =============================================================================
echo -e "${YELLOW}[2/4] 创建 GitHub 仓库...${NC}"

# 仓库名称（替换特殊字符）
REPO_NAME=$(echo "$TASK_ID" | tr '[:upper:]' '[:lower:]' | tr -cd 'a-z0-9-')

# 调用 GitHub API 创建仓库
CREATE_RESPONSE=$(curl -s -X POST \
  "https://api.github.com/user/repos" \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  -d "{
    \"name\": \"$REPO_NAME\",
    \"description\": \"$TASK_DESC\",
    \"private\": true,
    \"auto_init\": true
  }")

# 检查是否成功
if echo "$CREATE_RESPONSE" | grep -q "\"full_name\""; then
    REPO_FULL_NAME=$(echo "$CREATE_RESPONSE" | grep -o "\"full_name\": \"[^\"]*\"" | cut -d'"' -f4)
    REPO_URL=$(echo "$CREATE_RESPONSE" | grep -o "\"html_url\": \"[^\"]*\"" | cut -d'"' -f4)
    echo -e "  ${GREEN}✓${NC} GitHub 仓库创建成功"
    echo "    名称：$REPO_FULL_NAME"
    echo "    地址：$REPO_URL"
    GITHUB_SUCCESS=true
elif echo "$CREATE_RESPONSE" | grep -q "already exists"; then
    echo -e "  ${YELLOW}!${NC} GitHub 仓库已存在"
    REPO_URL="https://github.com/$GITHUB_USER/$REPO_NAME"
    echo "    地址：$REPO_URL"
    GITHUB_SUCCESS=true
else
    echo -e "  ${RED}✗${NC} GitHub 仓库创建失败"
    echo "    响应：$CREATE_RESPONSE"
    GITHUB_SUCCESS=false
fi

echo ""

# =============================================================================
# 创建 Gitee 仓库
# =============================================================================
echo -e "${YELLOW}[3/4] 创建 Gitee 仓库...${NC}"

if [ -n "$GITEE_TOKEN" ]; then
    # 调用 Gitee API 创建仓库
    GITEE_RESPONSE=$(curl -s -X POST \
      "https://gitee.com/api/v5/user/repos" \
      -H "Content-Type: application/json" \
      -d "{
        \"access_token\": \"$GITEE_TOKEN\",
        \"name\": \"$REPO_NAME\",
        \"description\": \"$TASK_DESC\",
        \"private\": true,
        \"auto_init\": true
      }")
    
    # 检查是否成功
    if echo "$GITEE_RESPONSE" | grep -q "\"full_name\""; then
        GITEE_REPO_NAME=$(echo "$GITEE_RESPONSE" | grep -o "\"full_name\": \"[^\"]*\"" | cut -d'"' -f4)
        GITEE_URL=$(echo "$GITEE_RESPONSE" | grep -o "\"html_url\": \"[^\"]*\"" | cut -d'"' -f4)
        echo -e "  ${GREEN}✓${NC} Gitee 仓库创建成功"
        echo "    名称：$GITEE_REPO_NAME"
        echo "    地址：$GITEE_URL"
        GITEE_SUCCESS=true
    elif echo "$GITEE_RESPONSE" | grep -q "already exists"; then
        echo -e "  ${YELLOW}!${NC} Gitee 仓库已存在"
        GITEE_URL="https://gitee.com/$GITEE_USER/$REPO_NAME"
        echo "    地址：$GITEE_URL"
        GITEE_SUCCESS=true
    else
        echo -e "  ${RED}✗${NC} Gitee 仓库创建失败"
        echo "    响应：$GITEE_RESPONSE"
        GITEE_SUCCESS=false
    fi
else
    echo -e "  ${YELLOW}!${NC} Gitee Token 未配置，跳过 Gitee 创建"
    GITEE_SUCCESS=false
fi

echo ""

# =============================================================================
# 生成本地项目文档
# =============================================================================
echo -e "${YELLOW}[4/4] 生成本地项目文档...${NC}"

# 创建项目目录
PROJECT_DIR="$Ziwei_DIR/projects/$TASK_ID"
mkdir -p "$PROJECT_DIR"

# 创建项目说明文档
cat > "$PROJECT_DIR/README.md" << EOF
# $TASK_NAME

**任务 ID**: $TASK_ID

**创建时间**: $(date '+%Y-%m-%d %H:%M:%S')

**描述**: $TASK_DESC

---

## 仓库地址

- **GitHub**: $REPO_URL
- **Gitee**: ${GITEE_URL:-"待配置"}

---

## 项目结构

\`\`\`
$PROJECT_DIR/
├── README.md          # 项目说明
├── docs/              # 文档
├── src/               # 源代码
├── tests/             # 测试
└── output/            # 输出
\`\`\`

---

## 任务状态

- [ ] 任务接入
- [ ] 任务分解
- [ ] 代码生成
- [ ] 代码审计
- [ ] 交付
- [ ] 归档

---

## 同步记录

| 时间 | 操作 | 状态 |
|------|------|------|
| $(date '+%Y-%m-%d %H:%M:%S') | 项目创建 | ✅ |

---

*此文档由紫微智控自动生成*
EOF

echo -e "  ${GREEN}✓${NC} 项目文档已生成"
echo "    路径：$PROJECT_DIR/README.md"
echo ""

# =============================================================================
# 生成报告
# =============================================================================
echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    项目创建报告                        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

echo "📦 任务信息:"
echo "  ID: $TASK_ID"
echo "  名称：$TASK_NAME"
echo ""

echo "🌐 仓库地址:"
if [ "$GITHUB_SUCCESS" = true ]; then
    echo -e "  GitHub: ${GREEN}✓${NC} $REPO_URL"
else
    echo -e "  GitHub: ${RED}✗${NC} 创建失败"
fi

if [ "$GITEE_SUCCESS" = true ]; then
    echo -e "  Gitee:  ${GREEN}✓${NC} $GITEE_URL"
else
    echo -e "  Gitee:  ${YELLOW}!${NC} 未创建"
fi

echo ""

echo "📁 本地目录:"
echo "  $PROJECT_DIR/"
echo ""

# 保存报告
REPORT_FILE="$Ziwei_DIR/data/logs/project_create_$(date +%Y%m%d_%H%M%S).md"
cat > "$REPORT_FILE" << EOF
# 项目创建报告

**时间**: $(date '+%Y-%m-%d %H:%M:%S')

## 任务信息

- **任务 ID**: $TASK_ID
- **任务名称**: $TASK_NAME
- **任务描述**: $TASK_DESC

## 仓库地址

| 平台 | 状态 | 地址 |
|------|------|------|
| GitHub | $([ "$GITHUB_SUCCESS" = true ] && echo "✅ 成功" || echo "❌ 失败") | $REPO_URL |
| Gitee | $([ "$GITEE_SUCCESS" = true ] && echo "✅ 成功" || echo "❌ 未创建") | ${GITEE_URL:-"N/A"} |

## 本地目录

$PROJECT_DIR/

## 下一步

1. 在本地目录创建项目文件
2. 提交代码到仓库
3. 紫微智控自动处理任务
EOF

echo -e "${GREEN}✓${NC} 报告已保存：$REPORT_FILE"
echo ""

# =============================================================================
# 完成
# =============================================================================
if [ "$GITHUB_SUCCESS" = true ]; then
    echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║              ✅ 项目创建完成！                         ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
    exit 0
else
    echo -e "${RED}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║              ⚠️  部分创建失败                          ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════════════════════╝${NC}"
    exit 1
fi
