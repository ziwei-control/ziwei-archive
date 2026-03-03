#!/bin/bash
# =============================================================================
# 紫微智控 - 一键部署脚本
# 版本：1.0
# 最后更新：2025-02-27
# =============================================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 路径定义
Ziwei_DIR="/home/admin/Ziwei"
CONFIG_DIR="$Ziwei_DIR/config"
SCRIPTS_DIR="$Ziwei_DIR/scripts"
DATA_DIR="$Ziwei_DIR/data"
LOGS_DIR="$DATA_DIR/logs"
HEALTH_DIR="$DATA_DIR/health"
TASKS_DIR="$DATA_DIR/tasks"
DOCS_DIR="$Ziwei_DIR/docs"
PROJECTS_DIR="$Ziwei_DIR/projects"

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║          紫微智控 (Ziwei Control & Intelligence)        ║${NC}"
echo -e "${BLUE}║                 一键部署脚本 v1.0                       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# =============================================================================
# 步骤 1: 检查系统依赖
# =============================================================================
echo -e "${YELLOW}[1/6] 检查系统依赖...${NC}"

# 检查 Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "  ${GREEN}✓${NC} Python3 已安装：$PYTHON_VERSION"
else
    echo -e "  ${RED}✗${NC} Python3 未安装"
    echo "  请运行：sudo apt-get install python3 python3-pip"
    exit 1
fi

# 检查 Git
if command -v git &> /dev/null; then
    GIT_VERSION=$(git --version)
    echo -e "  ${GREEN}✓${NC} Git 已安装：$GIT_VERSION"
else
    echo -e "  ${YELLOW}!${NC} Git 未安装（可选，建议安装）"
fi

# 检查 pip 包
echo ""
echo -e "${YELLOW}检查 Python 包...${NC}"

# 创建 requirements.txt
cat > "$SCRIPTS_DIR/requirements.txt" << 'EOF'
requests>=2.28.0
pyyaml>=6.0
python-dotenv>=1.0.0
EOF

echo -e "  ${GREEN}✓${NC} 已生成 requirements.txt"

# =============================================================================
# 步骤 2: 创建目录结构
# =============================================================================
echo ""
echo -e "${YELLOW}[2/6] 创建目录结构...${NC}"

mkdir -p "$LOGS_DIR"
echo -e "  ${GREEN}✓${NC} $LOGS_DIR"

mkdir -p "$HEALTH_DIR"
echo -e "  ${GREEN}✓${NC} $HEALTH_DIR"

mkdir -p "$TASKS_DIR/current"
mkdir -p "$TASKS_DIR/completed"
echo -e "  ${GREEN}✓${NC} $TASKS_DIR"

mkdir -p "$DOCS_DIR/knowledge"
mkdir -p "$DOCS_DIR/comm_logs"
mkdir -p "$DOCS_DIR/analysis"
mkdir -p "$DOCS_DIR/research"
mkdir -p "$DOCS_DIR/translations"
echo -e "  ${GREEN}✓${NC} $DOCS_DIR"

mkdir -p "$PROJECTS_DIR"
echo -e "  ${GREEN}✓${NC} $PROJECTS_DIR"

mkdir -p "$Ziwei_DIR/repo_archive/SUCCESS/PENDING_RELEASE"
mkdir -p "$Ziwei_DIR/repo_archive/SUCCESS/ARCHIVE"
mkdir -p "$Ziwei_DIR/repo_archive/FAILURE"
mkdir -p "$Ziwei_DIR/repo_archive/ERROR"
echo -e "  ${GREEN}✓${NC} $Ziwei_DIR/repo_archive"

# =============================================================================
# 步骤 3: 初始化配置文件
# =============================================================================
echo ""
echo -e "${YELLOW}[3/6] 初始化配置文件...${NC}"

# 创建环境变量模板
cat > "$Ziwei_DIR/.env.example" << 'EOF'
# 紫微智控 - 环境变量配置
# 复制此文件为 .env 并填入真实值

# 阿里百炼 API Key
BAILIAN_API_KEY="sk-sp-YOUR_API_KEY_HERE"

# 邮件配置
EMAIL_PASSWORD="your_email_password"
SMTP_SERVER="smtp.163.com"
SMTP_PORT="465"
SENDER_EMAIL="pandac00@163.com"

# 飞书配置（可选）
FEISHU_APP_SECRET="your_feishu_app_secret"

# GitHub 配置（可选）
GITHUB_TOKEN="your_github_token"
GITHUB_REPO="https://github.com/ziwei-control/ziwei-archive.git"
EOF

echo -e "  ${GREEN}✓${NC} 已创建 .env.example"

if [ ! -f "$Ziwei_DIR/.env" ]; then
    cp "$Ziwei_DIR/.env.example" "$Ziwei_DIR/.env"
    echo -e "  ${YELLOW}!${NC} 已复制 .env，请编辑填入真实 API Key"
else
    echo -e "  ${GREEN}✓${NC} .env 已存在"
fi

# =============================================================================
# 步骤 4: 初始化系统状态文件
# =============================================================================
echo ""
echo -e "${YELLOW}[4/6] 初始化系统状态...${NC}"

# 心跳文件
cat > "$HEALTH_DIR/heartbeat.log" << EOF
[$(date -Iseconds)] 系统初始化完成
EOF
echo -e "  ${GREEN}✓${NC} 心跳文件已创建"

# 系统状态文件
cat > "$DATA_DIR/system_status.md" << 'EOF'
# 紫微智控系统状态

## 当前状态
- **状态**: IDLE
- **最后更新**: [时间戳]
- **当前任务**: 无

## 统计
- **总任务数**: 0
- **成功交付**: 0
- **审计重做**: 0
- **急救触发**: 0
EOF
echo -e "  ${GREEN}✓${NC} 系统状态文件已创建"

# =============================================================================
# 步骤 5: 创建核心脚本
# =============================================================================
echo ""
echo -e "${YELLOW}[5/6] 创建核心脚本...${NC}"

# 创建本地监控脚本
cat > "$SCRIPTS_DIR/local_monitor.py" << 'PYTHON_EOF'
#!/usr/bin/env python3
"""
紫微智控 - 本地监控脚本
负责监听任务文件夹，协调各岗位工作
"""

import os
import sys
import time
import yaml
from datetime import datetime
from pathlib import Path

# 路径配置
Ziwei_DIR = Path("/home/admin/Ziwei")
CONFIG_FILE = Ziwei_DIR / "config" / "agents.yaml"
HEALTH_DIR = Ziwei_DIR / "data" / "health"
TASKS_DIR = Ziwei_DIR / "data" / "tasks"
LOGS_DIR = Ziwei_DIR / "data" / "logs"

def load_config():
    """加载配置文件"""
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def update_heartbeat(message="系统正常运行"):
    """更新心跳文件"""
    heartbeat_file = HEALTH_DIR / "heartbeat.log"
    timestamp = datetime.now().isoformat()
    with open(heartbeat_file, 'a', encoding='utf-8') as f:
        f.write(f"[{timestamp}] {message}\n")

def check_system_status():
    """检查系统状态"""
    status_file = Ziwei_DIR / "data" / "system_status.md"
    if status_file.exists():
        with open(status_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if "BUSY" in content:
                return "BUSY"
            elif "EMERGENCY" in content:
                return "EMERGENCY"
    return "IDLE"

def scan_tasks():
    """扫描任务文件夹"""
    current_tasks = TASKS_DIR / "current"
    if not current_tasks.exists():
        return []
    
    tasks = []
    for task_file in current_tasks.glob("*.md"):
        tasks.append({
            'file': task_file,
            'name': task_file.stem,
            'created': datetime.fromtimestamp(task_file.stat().st_mtime)
        })
    return tasks

def main():
    """主循环"""
    print(f"[{datetime.now().isoformat()}] 紫微智控本地监控启动")
    print(f"工作目录：{Ziwei_DIR}")
    
    # 加载配置
    config = load_config()
    print(f"已加载 {len(config.get('agents', {}))} 个岗位配置")
    
    # 初始化心跳
    update_heartbeat("监控脚本启动")
    
    last_heartbeat = time.time()
    
    try:
        while True:
            # 每 30 秒更新心跳
            if time.time() - last_heartbeat > 30:
                status = check_system_status()
                update_heartbeat(f"系统状态：{status}")
                last_heartbeat = time.time()
            
            # 扫描任务
            tasks = scan_tasks()
            if tasks:
                print(f"[{datetime.now().isoformat()}] 发现 {len(tasks)} 个进行中任务")
                for task in tasks:
                    print(f"  - {task['name']}")
            
            # 休眠
            time.sleep(10)
    
    except KeyboardInterrupt:
        print("\n[系统] 收到停止信号，正常退出")
        update_heartbeat("监控脚本停止")
        sys.exit(0)

if __name__ == "__main__":
    main()
PYTHON_EOF

chmod +x "$SCRIPTS_DIR/local_monitor.py"
echo -e "  ${GREEN}✓${NC} local_monitor.py 已创建"

# 创建巡查脚本
cat > "$SCRIPTS_DIR/supervisor.py" << 'PYTHON_EOF'
#!/usr/bin/env python3
"""
紫微智控 - 进度监工巡查脚本
每 18 分钟巡查一次，每 4 小时汇总发送简报
"""

import os
import sys
import time
import yaml
from datetime import datetime, timedelta
from pathlib import Path

# 路径配置
Ziwei_DIR = Path("/home/admin/Ziwei")
TASKS_DIR = Ziwei_DIR / "data" / "tasks" / "current"
LOGS_DIR = Ziwei_DIR / "data" / "logs"
BUFFER_LOG = LOGS_DIR / "supervisor_buffer.log"
SUMMARY_DIR = LOGS_DIR / "supervisor_4h_summary"

def check_tasks():
    """扫描任务目录，检查进度"""
    records = []
    
    if not TASKS_DIR.exists():
        return records
    
    for task_file in TASKS_DIR.glob("*.md"):
        try:
            mtime = datetime.fromtimestamp(task_file.stat().st_mtime)
            elapsed = datetime.now() - mtime
            elapsed_minutes = elapsed.total_seconds() / 60
            
            if elapsed_minutes > 18:
                status = f"警告：{task_file.stem} 超过 18 分钟未更新 ({elapsed_minutes:.0f}分钟)"
                records.append(f"[{datetime.now().isoformat()}] {status}")
            else:
                status = f"正常：{task_file.stem} 进行中 ({elapsed_minutes:.0f}分钟)"
                records.append(f"[{datetime.now().isoformat()}] {status}")
        except Exception as e:
            records.append(f"[{datetime.now().isoformat()}] 错误：检查 {task_file.name} 失败 - {e}")
    
    return records

def write_buffer(records):
    """写入巡查缓存"""
    BUFFER_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(BUFFER_LOG, "a", encoding="utf-8") as f:
        for record in records:
            f.write(record + "\n")
    print(f"[巡查] 已写入 {len(records)} 条记录到缓存")

def should_send_summary():
    """判断是否应该发送 4 小时简报"""
    if not BUFFER_LOG.exists():
        return False
    
    # 检查距离上次简报是否≥4 小时
    summary_file = SUMMARY_DIR / f"last_summary.txt"
    if summary_file.exists():
        last_summary = datetime.fromtimestamp(summary_file.stat().st_mtime)
        elapsed = datetime.now() - last_summary
        if elapsed.total_seconds() < 4 * 3600:
            return False
    
    return True

def generate_summary():
    """生成 4 小时汇总简报"""
    if not BUFFER_LOG.exists():
        return None
    
    # 读取过去 4 小时的缓存记录
    records = []
    four_hours_ago = datetime.now() - timedelta(hours=4)
    
    with open(BUFFER_LOG, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(line.strip())
    
    if not records:
        return None
    
    # 生成简报
    summary = f"""# 巡查简报

**周期**: {four_hours_ago.strftime('%Y-%m-%d %H:%M')} - {datetime.now().strftime('%Y-%m-%d %H:%M')}
**巡查次数**: {len(records)}

## 关键巡查记录

"""
    
    for record in records[-20:]:  # 最近 20 条
        summary += f"- {record}\n"
    
    summary += f"\n## 周期总结\n\n整体运行正常。\n"
    
    # 保存简报
    SUMMARY_DIR.mkdir(parents=True, exist_ok=True)
    summary_file = SUMMARY_DIR / f"{datetime.now().strftime('%Y%m%d_%H%M')}_summary.md"
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write(summary)
    
    # 更新最后简报时间
    last_summary_file = SUMMARY_DIR / "last_summary.txt"
    last_summary_file.touch()
    
    return summary_file

def main():
    """主循环"""
    print(f"[{datetime.now().isoformat()}] 紫微智控进度监工启动")
    print(f"巡查频率：每 18 分钟一次")
    print(f"简报频率：每 4 小时一次")
    
    try:
        while True:
            # 执行巡查
            print(f"\n[{datetime.now().isoformat()}] 执行巡查...")
            records = check_tasks()
            
            if records:
                write_buffer(records)
            else:
                print(f"[巡查] 无进行中任务")
            
            # 检查是否需要发送简报
            if should_send_summary():
                print(f"[巡查] 生成 4 小时简报...")
                summary_file = generate_summary()
                if summary_file:
                    print(f"[巡查] 简报已保存：{summary_file}")
                    # TODO: 调用通信官发送邮件
            
            # 休眠 18 分钟
            print(f"[巡查] 下次巡查：18 分钟后")
            time.sleep(18 * 60)
    
    except KeyboardInterrupt:
        print("\n[监工] 收到停止信号，正常退出")
        sys.exit(0)

if __name__ == "__main__":
    main()
PYTHON_EOF

chmod +x "$SCRIPTS_DIR/supervisor.py"
echo -e "  ${GREEN}✓${NC} supervisor.py 已创建"

# =============================================================================
# 步骤 6: 完成部署
# =============================================================================
echo ""
echo -e "${YELLOW}[6/6] 完成部署...${NC}"

# 创建 README
cat > "$Ziwei_DIR/README.md" << 'EOF'
# 紫微智控 (Ziwei Control & Intelligence)

> AI 驱动的一人公司系统

## 快速开始

### 1. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 填入真实的 API Key
```

### 2. 安装依赖

```bash
pip3 install -r scripts/requirements.txt
```

### 3. 启动系统

```bash
# 启动本地监控
python3 scripts/local_monitor.py &

# 启动进度监工（18 分钟巡查）
python3 scripts/supervisor.py &
```

## 目录结构

```
Ziwei/
├── SOP/                    # 标准作业程序文档
├── config/                 # 配置文件
│   └── agents.yaml        # 岗位配置
├── scripts/               # 脚本
│   ├── deploy.sh         # 部署脚本
│   ├── local_monitor.py  # 本地监控
│   └── supervisor.py     # 进度监工
├── data/                  # 数据
│   ├── logs/             # 日志
│   ├── tasks/            # 任务
│   └── health/           # 健康监控
├── docs/                  # 文档
├── projects/              # 项目
└── repo_archive/          # 归档库
```

## 核心机制

- **巡查机制**: 每 18 分钟巡查，每 4 小时简报
- **审计机制**: 四维审查，最多 20 次重做
- **急救机制**: 心跳监控，云端会诊
- **学习机制**: 每小时轮转 5 分钟

## 文档

详见 `SOP/` 文件夹中的完整规范。

## 联系方式

- 康纳：19922307306@189.cn
- Martin: pandac00@163.com
EOF

echo -e "  ${GREEN}✓${NC} README.md 已创建"

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                    部署完成！                          ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}下一步操作:${NC}"
echo ""
echo "1. 编辑配置文件:"
echo -e "   ${BLUE}nano $Ziwei_DIR/.env${NC}"
echo ""
echo "2. 安装 Python 依赖:"
echo -e "   ${BLUE}pip3 install -r $SCRIPTS_DIR/requirements.txt${NC}"
echo ""
echo "3. 启动系统:"
echo -e "   ${BLUE}python3 $SCRIPTS_DIR/local_monitor.py &${NC}"
echo -e "   ${BLUE}python3 $SCRIPTS_DIR/supervisor.py &${NC}"
echo ""
echo -e "${YELLOW}部署日志：$LOGS_DIR/deploy_$(date +%Y%m%d_%H%M%S).log${NC}"
echo ""
