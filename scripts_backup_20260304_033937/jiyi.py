#!/usr/bin/env python3
# =============================================================================
# jiyi - 紫微智控记忆命令（增强版 - 支持知识库检索）
# 功能：分门别类、最小存储、快速搜索、知识检索
# =============================================================================

import os
import sys
import json
import time
import re
from datetime import datetime

# 配置
JIYI_DIR = "/home/admin/Ziwei/jiyi"
MEMORY_DIR = os.path.join(JIYI_DIR, "memory")
INDEX_FILE = os.path.join(JIYI_DIR, "index.json")
KNOWLEDGE_DIR = "/home/admin/Ziwei/docs/knowledge"
VERSION = "2.0.0"

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
    os.makedirs(JIYI_DIR, exist_ok=True)
    os.makedirs(MEMORY_DIR, exist_ok=True)
    if not os.path.exists(INDEX_FILE):
        index = {"categories": {}, "tags": {}, "last_update": datetime.now().isoformat()}
        save_index(index)

def load_index():
    try:
        with open(INDEX_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {"categories": {}, "tags": {}, "last_update": datetime.now().isoformat()}

def save_index(index):
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

def search_knowledge(keyword, limit=10):
    """从知识库中搜索相关内容"""
    results = []
    
    if not os.path.exists(KNOWLEDGE_DIR):
        return results
    
    # 遍历所有 Agent 的知识文件
    for agent_dir in os.listdir(KNOWLEDGE_DIR):
        agent_path = os.path.join(KNOWLEDGE_DIR, agent_dir)
        if not os.path.isdir(agent_path):
            continue
        
        # 遍历该 Agent 的所有学习文件
        for filename in sorted(os.listdir(agent_path), reverse=True)[:limit]:
            if not filename.endswith('.md'):
                continue
            
            filepath = os.path.join(agent_path, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 搜索关键词
                if keyword.lower() in content.lower():
                    # 提取相关片段
                    lines = content.split('\n')
                    relevant_lines = []
                    for i, line in enumerate(lines):
                        if keyword.lower() in line.lower():
                            # 获取上下文（前后各 2 行）
                            start = max(0, i - 2)
                            end = min(len(lines), i + 3)
                            relevant_lines.extend(lines[start:end])
                    
                    # 去重
                    relevant_lines = list(dict.fromkeys(relevant_lines))[:10]
                    
                    results.append({
                        'agent': agent_dir,
                        'file': filename,
                        'path': filepath,
                        'snippets': relevant_lines,
                        'words': len(content.split())
                    })
            except Exception as e:
                continue
    
    return results

def search_memory(keyword, limit=5):
    """从记忆中搜索相关内容"""
    results = []
    
    if not os.path.exists(MEMORY_DIR):
        return results
    
    for filename in os.listdir(MEMORY_DIR):
        if not filename.endswith('.md'):
            continue
        
        filepath = os.path.join(MEMORY_DIR, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if keyword.lower() in content.lower():
                lines = content.split('\n')
                relevant_lines = []
                for i, line in enumerate(lines):
                    if keyword.lower() in line.lower():
                        start = max(0, i - 1)
                        end = min(len(lines), i + 2)
                        relevant_lines.extend(lines[start:end])
                
                relevant_lines = list(dict.fromkeys(relevant_lines))[:5]
                results.append({
                    'file': filename,
                    'path': filepath,
                    'snippets': relevant_lines
                })
        except:
            continue
    
    return results

def cmd_search(keyword):
    """搜索命令"""
    print(Colors.CYAN + "╔════════════════════════════════════════════════════════╗" + Colors.RESET)
    print(Colors.CYAN + "║          jiyi 搜索 - " + keyword + "                      ║" + Colors.RESET)
    print(Colors.CYAN + "╚════════════════════════════════════════════════════════╝" + Colors.RESET)
    print()
    
    # 搜索知识库
    print(Colors.BLUE + "📚 知识库检索:" + Colors.RESET)
    kb_results = search_knowledge(keyword)
    
    if kb_results:
        for result in kb_results[:5]:
            print()
            print("  " + Colors.GREEN + result['agent'] + "/" + result['file'] + Colors.RESET)
            print("  字数：" + str(result['words']))
            print("  相关片段:")
            for snippet in result['snippets'][:3]:
                if snippet.strip():
                    print("    - " + snippet.strip()[:80])
    else:
        print("  未找到相关内容")
    
    print()
    
    # 搜索记忆
    print(Colors.BLUE + "🧠 记忆检索:" + Colors.RESET)
    mem_results = search_memory(keyword)
    
    if mem_results:
        for result in mem_results[:3]:
            print()
            print("  " + Colors.GREEN + result['file'] + Colors.RESET)
            for snippet in result['snippets'][:2]:
                if snippet.strip():
                    print("    - " + snippet.strip()[:80])
    else:
        print("  未找到相关内容")
    
    print()
    print(Colors.GREEN + "✅ 搜索完成 - 知识库：" + str(len(kb_results)) + " 条，记忆：" + str(len(mem_results)) + " 条" + Colors.RESET)

def cmd_list():
    """列出所有记忆"""
    print(Colors.CYAN + "╔════════════════════════════════════════════════════════╗" + Colors.RESET)
    print(Colors.CYAN + "║          jiyi 记忆列表                                  ║" + Colors.RESET)
    print(Colors.CYAN + "╚════════════════════════════════════════════════════════╝" + Colors.RESET)
    print()
    
    if not os.path.exists(MEMORY_DIR):
        print("  记忆目录不存在")
        return
    
    files = sorted(os.listdir(MEMORY_DIR), reverse=True)
    for f in files[:20]:
        filepath = os.path.join(MEMORY_DIR, f)
        size = os.path.getsize(filepath)
        print("  📄 " + f + " (" + str(size) + " 字节)")
    
    print()
    print(Colors.GREEN + "✅ 共 " + str(len(files)) + " 个记忆文件" + Colors.RESET)

def cmd_stats():
    """统计信息"""
    print(Colors.CYAN + "╔════════════════════════════════════════════════════════╗" + Colors.RESET)
    print(Colors.CYAN + "║          jiyi 统计信息                                  ║" + Colors.RESET)
    print(Colors.CYAN + "╚════════════════════════════════════════════════════════╝" + Colors.RESET)
    print()
    
    # 知识库统计
    kb_files = 0
    kb_words = 0
    if os.path.exists(KNOWLEDGE_DIR):
        for agent_dir in os.listdir(KNOWLEDGE_DIR):
            agent_path = os.path.join(KNOWLEDGE_DIR, agent_dir)
            if os.path.isdir(agent_path):
                for f in os.listdir(agent_path):
                    if f.endswith('.md'):
                        kb_files += 1
                        filepath = os.path.join(agent_path, f)
                        kb_words += len(open(filepath, 'r', encoding='utf-8').read().split())
    
    print("📚 知识库:")
    print("  文件数：" + str(kb_files))
    print("  总字数：" + str(kb_words))
    print()
    
    # 记忆统计
    mem_files = 0
    mem_words = 0
    if os.path.exists(MEMORY_DIR):
        for f in os.listdir(MEMORY_DIR):
            if f.endswith('.md'):
                mem_files += 1
                filepath = os.path.join(MEMORY_DIR, f)
                mem_words += len(open(filepath, 'r', encoding='utf-8').read().split())
    
    print("🧠 记忆:")
    print("  文件数：" + str(mem_files))
    print("  总字数：" + str(mem_words))
    print()
    
    print(Colors.GREEN + "✅ 总计：知识库 " + str(kb_files) + " 文件/" + str(kb_words) + " 字，记忆 " + str(mem_files) + " 文件/" + str(mem_words) + " 字" + Colors.RESET)

def cmd_help():
    """帮助信息"""
    print("jiyi - 紫微智控记忆命令 v" + VERSION)
    print()
    print("用法：jiyi <命令> [参数]")
    print()
    print("命令:")
    print("  search <关键词>    搜索相关知识和记忆")
    print("  list               列出所有记忆文件")
    print("  stats              显示统计信息")
    print("  help               显示帮助信息")
    print()
    print("示例:")
    print("  jiyi search 安全编码")
    print("  jiyi search 设计模式")
    print("  jiyi stats")

def main():
    if len(sys.argv) < 2:
        cmd_help()
        return
    
    cmd = sys.argv[1].lower()
    
    if cmd == "search" and len(sys.argv) > 2:
        keyword = " ".join(sys.argv[2:])
        cmd_search(keyword)
    elif cmd == "list":
        cmd_list()
    elif cmd == "stats":
        cmd_stats()
    elif cmd == "help":
        cmd_help()
    else:
        print("未知命令：" + cmd)
        cmd_help()

if __name__ == "__main__":
    main()
