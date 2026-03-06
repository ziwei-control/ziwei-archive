#!/usr/bin/env python3
# =============================================================================
# jiyi - 紫微智控记忆命令（Python 版本）
# 功能：分门别类、最小存储、快速搜索
# =============================================================================

import os
import sys
import json
import time
from datetime import datetime

# 配置
JIYI_DIR = "/home/admin/Ziwei/jiyi"
MEMORY_DIR = os.path.join(JIYI_DIR, "memory")
INDEX_FILE = os.path.join(JIYI_DIR, "index.json")
VERSION = "1.0.0"

# 颜色定义
class Colors:
    RESET = "\033[0m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    PURPLE = "\033[35m"
    CYAN = "\033[36m"

def init_jiyi():
    """初始化记忆目录"""
    os.makedirs(JIYI_DIR, exist_ok=True)
    os.makedirs(MEMORY_DIR, exist_ok=True)
    
    if not os.path.exists(INDEX_FILE):
        index = {
            "categories": {},
            "tags": {},
            "last_update": datetime.now().isoformat()
        }
        save_index(index)

def load_index():
    """加载索引"""
    try:
        with open(INDEX_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {"categories": {}, "tags": {}, "last_update": datetime.now().isoformat()}

def save_index(index):
    """保存索引"""
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

def load_memory(memory_id):
    """加载记忆"""
    try:
        with open(os.path.join(MEMORY_DIR, f"{memory_id}.json"), 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return None

def save_memory(memory):
    """保存记忆"""
    with open(os.path.join(MEMORY_DIR, f"{memory['id']}.json"), 'w', encoding='utf-8') as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)

def generate_id():
    """生成记忆 ID"""
    return f"m_{int(time.time() * 1000000)}"

def auto_category(content):
    """自动分类"""
    content_lower = content.lower()
    
    categories = {
        "命令": ["命令", "runtask", "look", "jiyi", "执行"],
        "项目": ["项目", "仓库", "github", "gitee"],
        "配置": ["配置", "config", "env", "token"],
        "流程": ["流程", "步骤", "自动", "同步"],
        "错误": ["错误", "失败", "问题", "bug"],
        "系统": ["系统", "服务", "监控", "进程"],
        "文档": ["文档", "说明", "readme", "sop"],
    }
    
    for cat, keywords in categories.items():
        for kw in keywords:
            if kw.lower() in content_lower:
                return cat
    
    return "其他"

def add_memory(args):
    """添加记忆"""
    if len(args) < 1:
        print(f"{Colors.RED}✗ 请提供记忆内容{Colors.RESET}")
        print("用法：jiyi add <内容> [分类] [标签...]")
        return
    
    init_jiyi()
    
    content = args[0]
    category = args[1] if len(args) > 1 else auto_category(content)
    tags = args[2:] if len(args) > 2 else []
    
    memory = {
        "id": generate_id(),
        "category": category,
        "content": content,
        "tags": tags,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "is_new": True
    }
    
    save_memory(memory)
    
    # 更新索引
    index = load_index()
    if category not in index["categories"]:
        index["categories"][category] = []
    index["categories"][category].append(memory["id"])
    
    for tag in tags:
        if tag not in index["tags"]:
            index["tags"][tag] = []
        index["tags"][tag].append(memory["id"])
    
    index["last_update"] = datetime.now().isoformat()
    save_index(index)
    
    print(f"{Colors.GREEN}✓ 记忆已添加{Colors.RESET}")
    print(f"  ID: {memory['id']}")
    print(f"  分类：{memory['category']}")
    print(f"  标签：{memory['tags']}")
    print(f"  时间：{memory['created_at']}")

def search_memory(args):
    """搜索记忆"""
    init_jiyi()
    
    if len(args) < 1:
        # 交互模式
        interactive_search()
        return
    
    keyword = " ".join(args).lower()
    
    print(f"{Colors.BLUE}╔════════════════════════════════════════════════════════╗{Colors.RESET}")
    print(f"{Colors.BLUE}║          搜索结果：{Colors.CYAN}{keyword:<40}{Colors.BLUE}{Colors.RESET}")
    print(f"{Colors.BLUE}╚════════════════════════════════════════════════════════╝{Colors.RESET}")
    print()
    
    count = 0
    index = load_index()
    
    for cat, ids in index["categories"].items():
        for memory_id in ids:
            memory = load_memory(memory_id)
            if not memory:
                continue
            
            content = memory["content"].lower()
            tags = " ".join(memory["tags"]).lower()
            category = memory["category"].lower()
            
            if keyword in content or keyword in tags or keyword in category:
                count += 1
                print_memory(memory, count)
    
    if count == 0:
        print(f"{Colors.YELLOW}✗ 未找到相关记忆{Colors.RESET}")
        print()
        print(f"{Colors.CYAN}建议:{Colors.RESET}")
        print("  1. 检查关键词是否正确")
        print("  2. 尝试其他关键词")
        print("  3. 添加新记忆：jiyi add \"内容\" 分类 标签")
        print()
        
        # 询问是否添加
        response = input(f"{Colors.CYAN}是否添加为新记忆？(y/n): {Colors.RESET}")
        if response.lower() == 'y':
            content = input("输入记忆内容：")
            if content:
                category = auto_category(content)
                print(f"自动分类：{category}")
                tags_input = input("输入标签（空格分隔）：")
                tags = tags_input.split()
                add_memory([content, category] + tags)
    else:
        print(f"{Colors.GREEN}找到 {count} 条记忆{Colors.RESET}")

def interactive_search():
    """交互搜索"""
    print(f"{Colors.BLUE}╔════════════════════════════════════════════════════════╗{Colors.RESET}")
    print(f"{Colors.BLUE}║          jiyi - 交互式搜索                             ║{Colors.RESET}")
    print(f"{Colors.BLUE}╚════════════════════════════════════════════════════════╝{Colors.RESET}")
    print()
    print(f"{Colors.CYAN}输入关键词搜索（输入 q 退出）:{Colors.RESET}")
    
    while True:
        try:
            query = input(f"\n{Colors.GREEN}> {Colors.RESET}")
            if query.lower() in ['q', 'quit']:
                break
            if query:
                search_memory([query])
        except EOFError:
            break

def list_memories(args):
    """列出记忆"""
    init_jiyi()
    
    category = args[0] if len(args) > 0 else None
    
    print(f"{Colors.BLUE}╔════════════════════════════════════════════════════════╗{Colors.RESET}")
    if category:
        print(f"{Colors.BLUE}║          记忆列表 - {Colors.CYAN}{category:<34}{Colors.BLUE}{Colors.RESET}")
    else:
        print(f"{Colors.BLUE}║          记忆列表 - 全部{Colors.BLUE}{Colors.RESET}")
    print(f"{Colors.BLUE}╚════════════════════════════════════════════════════════╝{Colors.RESET}")
    print()
    
    index = load_index()
    count = 0
    
    if category:
        ids = index["categories"].get(category, [])
        for memory_id in ids:
            memory = load_memory(memory_id)
            if memory:
                count += 1
                print(f"  {memory['content']}")
                if memory.get('is_new'):
                    print(f"    {Colors.GREEN}[NEW]{Colors.RESET}")
                print()
    else:
        for cat, ids in index["categories"].items():
            print(f"{Colors.PURPLE}【{cat}】{Colors.RESET}")
            for memory_id in ids:
                memory = load_memory(memory_id)
                if memory:
                    count += 1
                    print(f"  {memory['content']}")
                    if memory.get('is_new'):
                        print(f"    {Colors.GREEN}[NEW]{Colors.RESET}")
            print()
    
    if count == 0:
        print(f"{Colors.YELLOW}✗ 没有记忆{Colors.RESET}")
    else:
        print(f"{Colors.GREEN}共 {count} 条记忆{Colors.RESET}")

def show_categories():
    """显示分类"""
    init_jiyi()
    index = load_index()
    
    print(f"{Colors.BLUE}╔════════════════════════════════════════════════════════╗{Colors.RESET}")
    print(f"{Colors.BLUE}║          记忆分类                                      ║{Colors.RESET}")
    print(f"{Colors.BLUE}╚════════════════════════════════════════════════════════╝{Colors.RESET}")
    print()
    
    for cat, ids in index["categories"].items():
        print(f"  {Colors.PURPLE}{cat:<15}{Colors.RESET} {len(ids)} 条记忆")
    
    print()
    print(f"总计：{len(index['categories'])} 个分类")

def show_tags():
    """显示标签"""
    init_jiyi()
    index = load_index()
    
    print(f"{Colors.BLUE}╔════════════════════════════════════════════════════════╗{Colors.RESET}")
    print(f"{Colors.BLUE}║          记忆标签                                      ║{Colors.RESET}")
    print(f"{Colors.BLUE}╚════════════════════════════════════════════════════════╝{Colors.RESET}")
    print()
    
    for tag, ids in index["tags"].items():
        print(f"  {Colors.CYAN}#{tag:<15}{Colors.RESET} {len(ids)} 条记忆")
    
    print()
    print(f"总计：{len(index['tags'])} 个标签")

def show_version():
    """显示版本"""
    print(f"{Colors.BLUE}╔════════════════════════════════════════════════════════╗{Colors.RESET}")
    print(f"{Colors.BLUE}║          jiyi - 紫微智控记忆命令                        ║{Colors.RESET}")
    print(f"{Colors.BLUE}╚════════════════════════════════════════════════════════╝{Colors.RESET}")
    print()
    print(f"{Colors.CYAN}版本:{Colors.RESET} v{VERSION}")
    print(f"{Colors.CYAN}日期:{Colors.RESET} 2026-02-28")
    print(f"{Colors.CYAN}代号:{Colors.RESET} 紫微智控 - 记忆命令")
    print()
    print(f"{Colors.CYAN}功能:{Colors.RESET}")
    print("  ✅ 分门别类存储")
    print("  ✅ 最小存储空间")
    print("  ✅ 快速搜索")
    print("  ✅ 自动分类")
    print("  ✅ 新旧记忆分离")
    print()

def show_help():
    """显示帮助"""
    print(f"{Colors.BLUE}╔════════════════════════════════════════════════════════╗{Colors.RESET}")
    print(f"{Colors.BLUE}║          jiyi - 紫微智控记忆命令                        ║{Colors.RESET}")
    print(f"{Colors.BLUE}╚════════════════════════════════════════════════════════╝{Colors.RESET}")
    print()
    print(f"{Colors.CYAN}用法:{Colors.RESET}")
    print("  jiyi <命令> [参数]")
    print()
    print(f"{Colors.CYAN}命令:{Colors.RESET}")
    print("  add, a <内容> [分类] [标签...]  - 添加记忆")
    print("  search, s, find <关键词>       - 搜索记忆")
    print("  list, ls [分类]                - 列出记忆")
    print("  categories, cat                - 显示所有分类")
    print("  tags                           - 显示所有标签")
    print("  version, v                     - 显示版本")
    print("  help, h                        - 显示帮助")
    print()
    print(f"{Colors.CYAN}示例:{Colors.RESET}")
    print('  jiyi add "runtask 命令用于启动任务" 命令 runtask 自动化')
    print("  jiyi search runtask")
    print("  jiyi list 命令")
    print("  jiyi")
    print()

def print_memory(memory, index):
    """打印记忆"""
    print(f"{Colors.PURPLE}【记忆 #{index}】{Colors.RESET}")
    print(f"  内容：{memory['content']}")
    print(f"  分类：{memory['category']}")
    if memory['tags']:
        print(f"  标签：{memory['tags']}")
    print(f"  时间：{memory['created_at']}")
    if memory.get('is_new'):
        print(f"  {Colors.GREEN}[新记忆]{Colors.RESET}")
    print(f"  文件：{memory['id']}.json")
    print()

def main():
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1]
    args = sys.argv[2:]
    
    if command in ['add', 'a']:
        add_memory(args)
    elif command in ['search', 's', 'find']:
        search_memory(args)
    elif command in ['list', 'ls']:
        list_memories(args)
    elif command in ['categories', 'cat']:
        show_categories()
    elif command == 'tags':
        show_tags()
    elif command in ['version', 'v', '-v', '--version']:
        show_version()
    elif command in ['help', 'h', '-h', '--help']:
        show_help()
    else:
        # 默认搜索
        search_memory(sys.argv[1:])

if __name__ == "__main__":
    main()
