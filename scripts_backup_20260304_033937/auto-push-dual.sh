#!/bin/bash
# =============================================================================
# auto-push-dual - 紫微智控双平台自动推送脚本
# 功能：自动检测项目变化，自动推送到 GitHub 和 Gitee
# 使用：在项目目录运行，或作为 look 的子程序
# =============================================================================

# 配置
Ziwei_DIR="/home/admin/Ziwei"
LOG_FILE="$Ziwei_DIR/data/logs/auto-push.log"

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# 日志函数
log() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] $1" >> "$LOG_FILE"
    echo -e "${BLUE}[auto-push]${NC} $1"
}

log_success() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] SUCCESS: $1" >> "$LOG_FILE"
    echo -e "${GREEN}[auto-push]${NC} $1"
}

log_error() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] ERROR: $1" >> "$LOG_FILE"
    echo -e "${RED}[auto-push]${NC} $1"
}

# =============================================================================
# 自动推送到双平台
# =============================================================================
auto_push_dual() {
    local project_dir="$1"
    local project_name=$(basename "$project_dir")
    
    log "检查项目：$project_name"
    
    # 检查是否是 Git 仓库
    if [ ! -d "$project_dir/.git" ]; then
        log "项目 $project_name 不是 Git 仓库，跳过"
        return
    fi
    
    cd "$project_dir"
    
    # 检查是否有更改
    local changes=$(git status --porcelain 2>/dev/null | wc -l)
    if [ "$changes" -eq 0 ]; then
        log "项目 $project_name 没有更改，跳过"
        return
    fi
    
    log "项目 $project_name 有 $changes 个更改"
    
    # 添加并提交更改
    git add .
    git commit -m "自动提交：$(date '+%Y-%m-%d %H:%M:%S')" >/dev/null 2>&1
    
    # 推送到 GitHub
    log "推送到 GitHub..."
    if git push origin main 2>&1 | grep -q "error\|fatal"; then
        log_error "GitHub 推送失败，尝试强制推送..."
        git push -f origin main 2>&1 | tail -1
    else
        log_success "GitHub 推送成功"
    fi
    
    # 推送到 Gitee
    log "推送到 Gitee..."
    if git push gitee main 2>&1 | grep -q "error\|fatal"; then
        log_error "Gitee 推送失败"
    else
        log_success "Gitee 推送成功"
    fi
    
    log "项目 $project_name 推送完成"
}

# =============================================================================
# 主程序
# =============================================================================
if [ -n "$1" ]; then
    # 指定项目目录
    auto_push_dual "$1"
else
    # 扫描所有项目
    log "╔════════════════════════════════════════════════════════╗"
    log "║          双平台自动推送                                 ║"
    log "╚════════════════════════════════════════════════════════╝"
    
    for dir in "$Ziwei_DIR/projects"/*/; do
        if [ -d "$dir" ]; then
            auto_push_dual "$dir"
        fi
    done
    
    log "所有项目推送完成"
fi
