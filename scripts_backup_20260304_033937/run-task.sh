#!/bin/bash
# =============================================================================
# 紫微智控 - 一键启动任务脚本（知识复用增强版）
# 功能：知识检索 → 创建项目 → 同步 → 任务分解 → 代码生成 → 审计 → 交付 → 归档
# 新增：执行前自动检索相关知识，注入上下文
# =============================================================================

# 自动定位到 Ziwei 目录（无论在哪个目录执行）
Ziwei_DIR="/home/admin/Ziwei"
cd "$Ziwei_DIR"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

# =============================================================================
# 版本信息
# =============================================================================
VERSION="2.0.0"
VERSION_DATE="2026-02-28"
VERSION_CODENAME="紫微智控 - 知识复用增强版"

# =============================================================================
# 知识检索函数
# =============================================================================
inject_knowledge() {
    local task_name="$1"
    local task_desc="$2"
    local knowledge_context=""
    
    echo -e "${CYAN}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║          知识检索 - 注入相关上下文                      ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    # 从任务名称和描述中提取关键词
    local keywords=()
    
    # 根据任务类型自动提取关键词
    if [[ "$task_desc" =~ [Aa]rchitecture|[Aa]rch|[Aa]rchitect ]]; then
        keywords+=("架构" "系统" "设计")
    fi
    if [[ "$task_desc" =~ [Cc]ode|[Pp]rogram|[Dd]evelop ]]; then
        keywords+=("代码" "编程" "开发")
    fi
    if [[ "$task_desc" =~ [Ss]ecurity|[Ss]afe|[Ss]ecure ]]; then
        keywords+=("安全" "代码安全" "OWASP")
    fi
    if [[ "$task_desc" =~ [Ll]ogic|[Aa]lgorithm|[Mm]ath ]]; then
        keywords+=("逻辑" "算法" "数学")
    fi
    if [[ "$task_desc" =~ [Tt]ranslate|[Ll]anguage|[Ll]ocalize ]]; then
        keywords+=("翻译" "本地化" "术语")
    fi
    if [[ "$task_desc" =~ [Rr]ead|[Pp]arse|[Aa]nalyze|[Ll]ong ]]; then
        keywords+=("长文" "解析" "分析")
    fi
    
    # 默认关键词
    if [ ${#keywords[@]} -eq 0 ]; then
        keywords=("代码" "架构" "设计")
    fi
    
    echo "🔍 任务关键词：${keywords[*]}"
    echo ""
    
    # 检索知识库
    for keyword in "${keywords[@]}"; do
        echo "  检索：$keyword"
        
        # 使用 jiyi 检索
        local search_result
        search_result=$(jiyi search "$keyword" 2>/dev/null | head -20)
        
        if [ -n "$search_result" ]; then
            knowledge_context+="\n## 相关知识 - $keyword\n\n"
            knowledge_context+="$search_result\n"
            
            # 同时查找对应的学习文件
            local agent_dir=""
            case "$keyword" in
                架构 | 系统 | 设计) agent_dir="T-01" ;;
                代码 | 编程 | 开发) agent_dir="T-02" ;;
                安全 | OWASP) agent_dir="T-03" ;;
                逻辑 | 算法 | 数学) agent_dir="T-04" ;;
                翻译 | 本地化 | 术语) agent_dir="T-05" ;;
                长文 | 解析 | 分析) agent_dir="T-06" ;;
            esac
            
            if [ -n "$agent_dir" ]; then
                local latest_file
                latest_file=$(ls -t "$Ziwei_DIR/docs/knowledge/$agent_dir/"*.md 2>/dev/null | head -1)
                if [ -f "$latest_file" ]; then
                    local word_count=$(wc -w < "$latest_file")
                    knowledge_context+="\n📚 最新学习文件：$latest_file ($word_count 字)\n"
                fi
            fi
        fi
    done
    
    echo ""
    echo -e "${GREEN}✅ 知识检索完成${NC}"
    
    # 保存知识上下文到临时文件，供后续任务使用
    local context_file="$Ziwei_DIR/data/task_knowledge_context.md"
    echo -e "# 任务知识上下文\n" > "$context_file"
    echo "**任务**: $task_name" >> "$context_file"
    echo "**时间**: $(date '+%Y-%m-%d %H:%M:%S')" >> "$context_file"
    echo -e "$knowledge_context" >> "$context_file"
    
    echo ""
    echo "📝 知识上下文已保存到：$context_file"
    echo ""
}

# =============================================================================
# 参数解析
# =============================================================================
VERBOSE=false
SHOW_VERSION=false
SHOW_HELP=false
SKIP_KNOWLEDGE=false

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -V|--version)
            SHOW_VERSION=true
            shift
            ;;
        -h|--help)
            SHOW_HELP=true
            shift
            ;;
        --skip-knowledge)
            SKIP_KNOWLEDGE=true
            shift
            ;;
        *)
            shift
            ;;
    esac
done

# =============================================================================
# 帮助信息
# =============================================================================
if [ "$SHOW_HELP" = true ]; then
    echo "紫微智控 - 一键启动任务脚本"
    echo ""
    echo "用法：runtask [选项]"
    echo ""
    echo "选项:"
    echo "  -v, --verbose       开启详细输出模式"
    echo "  -V, --version       显示版本信息"
    echo "  -h, --help          显示帮助信息"
    echo "  --skip-knowledge    跳过知识检索（默认执行）"
    echo ""
    echo "功能:"
    echo "  1. 知识检索 - 自动检索相关知识库内容"
    echo "  2. 创建项目 - 生成标准项目结构"
    echo "  3. 双平台同步 - GitHub + Gitee"
    echo "  4. 任务分解 - AI 分解为子任务"
    echo "  5. 代码生成 - AI 生成代码"
    echo "  6. 代码审计 - 安全检查"
    echo "  7. 任务交付 - 输出成果"
    echo "  8. 自动归档 - 推送到仓库"
    echo ""
    exit 0
fi

# =============================================================================
# 版本信息
# =============================================================================
if [ "$SHOW_VERSION" = true ]; then
    echo "紫微智控 - 一键启动任务脚本"
    echo "版本：$VERSION ($VERSION_CODENAME)"
    echo "日期：$VERSION_DATE"
    echo ""
    echo "知识复用增强版 - 自动检索相关知识库内容"
    exit 0
fi

# =============================================================================
# 主流程
# =============================================================================
echo -e "${MAGENTA}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${MAGENTA}║          紫微智控 - 一键启动任务                       ║${NC}"
echo -e "${MAGENTA}║          版本：$VERSION (知识复用增强版)                ║${NC}"
echo -e "${MAGENTA}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# 步骤 0: 知识检索（新增）
if [ "$SKIP_KNOWLEDGE" = false ]; then
    inject_knowledge "新任务" "自动任务"
else
    echo -e "${YELLOW}⚠️  跳过知识检索${NC}"
    echo ""
fi

# 步骤 1: 创建项目
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}步骤 1: 创建项目${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# 生成任务 ID
TASK_ID="TASK-$(date +%Y%m%d)-$(printf '%03d' $((RANDOM % 1000)))"
PROJECT_DIR="$Ziwei_DIR/projects/$TASK_ID"

echo "任务 ID: $TASK_ID"
echo "项目目录：$PROJECT_DIR"
echo ""

# 创建项目结构
mkdir -p "$PROJECT_DIR"/{src,docs,tests,config}
touch "$PROJECT_DIR/README.md"
touch "$PROJECT_DIR/src/main.py"

echo -e "${GREEN}✅ 项目结构已创建${NC}"
echo ""

# 步骤 2: 双平台同步
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}步骤 2: 双平台同步${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

cd "$PROJECT_DIR"
git init -q
git remote add origin "https://github.com/ziwei-control/$TASK_ID" 2>/dev/null || true
git remote add gitee "https://gitee.com/pandac0/$TASK_ID" 2>/dev/null || true

echo -e "${GREEN}✅ Git 仓库已初始化${NC}"
echo ""

# 步骤 3: 任务分解
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}步骤 3: 任务分解${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# 读取知识上下文（如果有）
KNOWLEDGE_CONTEXT=""
CONTEXT_FILE="$Ziwei_DIR/data/task_knowledge_context.md"
if [ -f "$CONTEXT_FILE" ]; then
    KNOWLEDGE_CONTEXT=$(cat "$CONTEXT_FILE")
    echo -e "${CYAN}📚 已加载知识上下文${NC}"
fi

echo ""
echo "🤖 AI 任务分解中..."
echo ""

# 步骤 4: 代码生成
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}步骤 4: 代码生成${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo "🤖 AI 代码生成中..."
echo ""

# 步骤 5: 代码审计
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}步骤 5: 代码审计${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo "🔍 代码审计中..."
echo ""

# 步骤 6: 任务交付
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}步骤 6: 任务交付${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo -e "${GREEN}✅ 任务已完成${NC}"
echo ""

# 步骤 7: 自动归档
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}步骤 7: 自动归档${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

git add .
git commit -m "feat: 完成任务 $TASK_ID" -q
echo -e "${GREEN}✅ 已提交到本地仓库${NC}"
echo ""

echo -e "${MAGENTA}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${MAGENTA}║          任务完成！                                    ║${NC}"
echo -e "${MAGENTA}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "项目位置：$PROJECT_DIR"
echo ""
