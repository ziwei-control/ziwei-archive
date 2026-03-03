#!/bin/bash
# =============================================================================
# look - 紫微智控项目监控程序
# 功能：24 小时监控项目，项目结束后自动将脚本转为系统命令
# 特点：低占用、低能耗、持续监控
# =============================================================================

# 配置
Ziwei_DIR="/home/admin/Ziwei"
PROJECTS_DIR="$Ziwei_DIR/projects"
COMMANDS_DIR="$Ziwei_DIR/commands"
LOG_FILE="$Ziwei_DIR/data/logs/look.log"
STATE_FILE="$Ziwei_DIR/data/logs/look.state"
CHECK_INTERVAL=60  # 检查间隔（秒）

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# =============================================================================
# 日志函数
# =============================================================================
log() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] $1" >> "$LOG_FILE"
    if [ "$VERBOSE" = true ]; then
        echo -e "${BLUE}[look]${NC} $1"
    fi
}

log_action() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] ACTION: $1" >> "$LOG_FILE"
    echo -e "${YELLOW}[look]${NC} $1"
}

log_success() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] SUCCESS: $1" >> "$LOG_FILE"
    echo -e "${GREEN}[look]${NC} $1"
}

log_error() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] ERROR: $1" >> "$LOG_FILE"
    echo -e "${RED}[look]${NC} $1"
}

# =============================================================================
# 初始化
# =============================================================================
init() {
    log "初始化 look 监控程序..."
    
    # 创建命令目录
    mkdir -p "$COMMANDS_DIR"
    
    # 创建日志文件
    touch "$LOG_FILE"
    
    # 初始化状态文件
    if [ ! -f "$STATE_FILE" ]; then
        echo "last_check=$(date -Iseconds)" > "$STATE_FILE"
        echo "processed_projects=" >> "$STATE_FILE"
    fi
    
    log_success "初始化完成"
}

# =============================================================================
# 加载状态
# =============================================================================
load_state() {
    if [ -f "$STATE_FILE" ]; then
        source "$STATE_FILE"
    else
        last_check=""
        processed_projects=""
    fi
}

# =============================================================================
# 保存状态
# =============================================================================
save_state() {
    cat > "$STATE_FILE" << EOF
last_check=$(date -Iseconds)
processed_projects=$processed_projects
EOF
}

# =============================================================================
# 获取项目列表
# =============================================================================
get_projects() {
    local projects=""
    for dir in "$PROJECTS_DIR"/*/; do
        if [ -d "$dir" ]; then
            local project_name=$(basename "$dir")
            # 跳过特殊目录
            if [[ "$project_name" != "." && "$project_name" != ".." ]]; then
                projects="$projects $project_name"
            fi
        fi
    done
    echo "$projects"
}

# =============================================================================
# 检查项目是否已完成
# =============================================================================
is_project_completed() {
    local project_dir="$PROJECTS_DIR/$1"
    local task_file="$project_dir/TASK.md"
    
    if [ -f "$task_file" ]; then
        # 检查 TASK.md 中状态是否为 Done
        if grep -q "状态：Done" "$task_file" 2>/dev/null; then
            return 0
        fi
    fi
    return 1
}

# =============================================================================
# 获取项目中的可执行脚本
# =============================================================================
get_executable_scripts() {
    local project_dir="$PROJECTS_DIR/$1"
    local scripts=""
    
    # 查找项目目录中的可执行脚本
    for file in "$project_dir"/*.sh "$project_dir"/*.py; do
        if [ -f "$file" ]; then
            # 检查是否是脚本文件
            if file "$file" | grep -qE "script|executable"; then
                scripts="$scripts $file"
            fi
        fi
    done
    
    echo "$scripts"
}

# =============================================================================
# 创建系统命令
# =============================================================================
create_command() {
    local project_name="$1"
    local script_path="$2"
    local command_name="$project_name"
    local command_path="$COMMANDS_DIR/$command_name"
    
    log_action "为项目 $project_name 创建命令：$command_name"
    
    # 创建命令包装脚本
    cat > "$command_path" << EOF
#!/bin/bash
# 紫微智控 - $project_name 项目命令
# 自动生成时间：$(date '+%Y-%m-%d %H:%M:%S')

exec bash "$script_path" "\$@"
EOF
    
    # 赋予执行权限
    chmod +x "$command_path"
    
    # 创建符号链接到 /usr/local/bin
    if [ -w "/usr/local/bin" ]; then
        ln -sf "$command_path" "/usr/local/bin/$command_name" 2>/dev/null
        log_success "已创建系统命令：$command_name -> /usr/local/bin/$command_name"
    else
        log_success "已创建命令：$command_path"
        log_action "需要手动创建符号链接：sudo ln -sf $command_path /usr/local/bin/$command_name"
    fi
    
    # 自动推送到双平台
    log_action "自动推送到双平台..."
    bash "$Ziwei_DIR/scripts/auto-push-dual.sh" "$PROJECTS_DIR/$project_name"
    
    # 输出给 agent 的命令
    echo ""
    echo "╔════════════════════════════════════════════════════════╗"
    echo "║          新命令已创建                                  ║"
    echo "╚════════════════════════════════════════════════════════╝"
    echo ""
    echo "命令名称：$command_name"
    echo "命令路径：$command_path"
    echo "源脚本：$script_path"
    echo ""
    echo "使用方法:"
    echo "  $command_name [参数]"
    echo ""
    if [ ! -w "/usr/local/bin" ]; then
        echo "需要执行:"
        echo "  sudo ln -sf $command_path /usr/local/bin/$command_name"
        echo ""
    fi
}

# =============================================================================
# 处理项目
# =============================================================================
process_project() {
    local project_name="$1"
    local project_dir="$PROJECTS_DIR/$project_name"
    
    log "检查项目：$project_name"
    
    # 检查项目是否已完成
    if is_project_completed "$project_name"; then
        log "项目 $project_name 已完成"
        
        # 检查是否已处理过
        if [[ "$processed_projects" == *"$project_name"* ]]; then
            log "项目 $project_name 已处理过，跳过"
            return
        fi
        
        # 获取可执行脚本
        local scripts=$(get_executable_scripts "$project_name")
        
        if [ -n "$scripts" ]; then
            log_action "发现可执行脚本：$scripts"
            
            # 为每个脚本创建命令
            for script in $scripts; do
                create_command "$project_name" "$script"
            done
            
            # 标记为已处理
            processed_projects="$processed_projects $project_name"
            save_state
        else
            log "项目 $project_name 没有可执行脚本"
        fi
    fi
}

# =============================================================================
# 主循环
# =============================================================================
main_loop() {
    log "╔════════════════════════════════════════════════════════╗"
    log "║          look 监控程序启动                              ║"
    log "╚════════════════════════════════════════════════════════╝"
    log "检查间隔：${CHECK_INTERVAL}秒"
    log "项目目录：$PROJECTS_DIR"
    log "命令目录：$COMMANDS_DIR"
    log ""
    
    echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║          look - 紫微智控项目监控程序                    ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${GREEN}✓${NC} look 监控程序已启动"
    echo -e "${GREEN}✓${NC} 检查间隔：${CHECK_INTERVAL}秒"
    echo -e "${GREEN}✓${NC} 项目目录：$PROJECTS_DIR"
    echo -e "${GREEN}✓${NC} 命令目录：$COMMANDS_DIR"
    echo ""
    echo -e "${YELLOW}按 Ctrl+C 停止监控${NC}"
    echo ""
    
    # 主循环
    while true; do
        load_state
        
        # 获取所有项目
        local projects=$(get_projects)
        
        # 处理每个项目
        for project in $projects; do
            process_project "$project"
        done
        
        # 等待下次检查
        sleep $CHECK_INTERVAL
    done
}

# =============================================================================
# 参数解析
# =============================================================================
VERBOSE=false
RUN_AS_DAEMON=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -d|--daemon)
            RUN_AS_DAEMON=true
            shift
            ;;
        -s|--status)
            echo "look 监控程序状态:"
            ps aux | grep "look.sh" | grep -v grep
            exit 0
            ;;
        -h|--help)
            echo "用法：look [选项]"
            echo ""
            echo "选项:"
            echo "  -v, --verbose     详细输出"
            echo "  -d, --daemon      后台运行"
            echo "  -s, --status      显示状态"
            echo "  -h, --help        显示帮助"
            exit 0
            ;;
        *)
            shift
            ;;
    esac
done

# =============================================================================
# 自动创建系统命令
# =============================================================================
create_self_command() {
    local command_path="$COMMANDS_DIR/look"
    
    # 创建命令包装脚本
    cat > "$command_path" << 'CMDEOF'
#!/bin/bash
# 紫微智控 - look 监控程序命令
exec bash "/home/admin/Ziwei/scripts/look.sh" "$@"
CMDEOF
    
    # 赋予执行权限
    chmod +x "$command_path"
    
    # 创建符号链接到 /usr/local/bin
    if [ -w "/usr/local/bin" ]; then
        ln -sf "$command_path" "/usr/local/bin/look" 2>/dev/null
        log_success "已创建系统命令：look -> /usr/local/bin/look"
    else
        log_success "已创建命令：$command_path"
        log_action "需要手动创建符号链接：sudo ln -sf $command_path /usr/local/bin/look"
    fi
}

# =============================================================================
# 启动
# =============================================================================
init

# 自动创建系统命令
create_self_command

if [ "$RUN_AS_DAEMON" = true ]; then
    # 后台运行
    nohup "$0" --verbose > /dev/null 2>&1 &
    echo "look 监控程序已在后台运行 (PID: $!)"
else
    # 前台运行
    main_loop
fi
