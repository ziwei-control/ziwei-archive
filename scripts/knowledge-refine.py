#!/usr/bin/env python3
# =============================================================================
# knowledge-refine - 知识提炼脚本
# 功能：学习后自动提炼核心要点，更新 SOP，建立知识→行动闭环
# =============================================================================

import os
import sys
import json
from datetime import datetime

# 配置
Ziwei_DIR = "/home/admin/Ziwei"
KNOWLEDGE_DIR = os.path.join(Ziwei_DIR, "docs", "knowledge")
SOP_DIR = os.path.join(Ziwei_DIR, "SOP")
MEMORY_FILE = "/root/.openclaw/workspace/MEMORY.md"
REFINE_LOG = os.path.join(Ziwei_DIR, "data", "logs", "knowledge_refine.log")

def log(message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_line = "[" + timestamp + "] " + message
    print(log_line)
    os.makedirs(os.path.dirname(REFINE_LOG), exist_ok=True)
    with open(REFINE_LOG, 'a', encoding='utf-8') as f:
        f.write(log_line + '\n')

def get_latest_knowledge(agent_id):
    """获取指定 Agent 的最新学习文件"""
    agent_dir = os.path.join(KNOWLEDGE_DIR, agent_id)
    if not os.path.exists(agent_dir):
        return None
    
    files = sorted([f for f in os.listdir(agent_dir) if f.endswith('.md')], reverse=True)
    if files:
        return os.path.join(agent_dir, files[0])
    return None

def extract_key_points(filepath):
    """从学习文件中提取核心要点"""
    if not os.path.exists(filepath):
        return []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    key_points = []
    
    # 提取章节标题
    import re
    headings = re.findall(r'^## (.+)$', content, re.MULTILINE)
    
    # 提取待办事项
    todos = re.findall(r'^- \[ \] (.+)$', content, re.MULTILINE)
    
    # 提取关键概念
    concepts = re.findall(r'\*\*(.+?)\*\*', content)
    
    return {
        'headings': headings[:10],  # 最多 10 个章节
        'todos': todos[:10],  # 最多 10 个待办
        'concepts': concepts[:20],  # 最多 20 个关键概念
        'word_count': len(content.split()),
        'file': filepath
    }

def update_sop(agent_id, key_points):
    """更新对应 Agent 的 SOP 文档"""
    sop_file = os.path.join(SOP_DIR, "01_岗位说明书.md")
    
    if not os.path.exists(sop_file):
        log("⚠️  SOP 文件不存在：" + sop_file)
        return False
    
    with open(sop_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 添加知识更新记录
    update_section = "\n\n### 📚 最新知识更新\n\n"
    update_section += "**更新时间**: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\n\n"
    update_section += "**学习文件**: " + key_points['file'] + "\n\n"
    update_section += "**核心概念**:\n\n"
    
    for concept in key_points['concepts'][:5]:
        update_section += "- " + concept + "\n"
    
    update_section += "\n**待实践**:\n\n"
    for todo in key_points['todos'][:5]:
        update_section += "- [ ] " + todo + "\n"
    
    # 检查是否已存在更新记录，避免重复
    if "最新知识更新" not in content:
        content += update_section
        with open(sop_file, 'w', encoding='utf-8') as f:
            f.write(content)
        log("✅ SOP 已更新：" + sop_file)
        return True
    else:
        log("⏭️  SOP 已有更新记录，跳过")
        return False

def update_memory(agent_id, key_points):
    """提炼核心要点到 MEMORY.md"""
    if not os.path.exists(MEMORY_FILE):
        log("⚠️  MEMORY.md 不存在：" + MEMORY_FILE)
        return False
    
    with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 添加知识摘要
    summary_section = "\n\n### 🧠 知识沉淀 - " + agent_id + " (" + datetime.now().strftime('%Y-%m-%d') + ")\n\n"
    summary_section += "**来源**: " + key_points['file'] + "\n\n"
    summary_section += "**核心收获**:\n\n"
    
    # 提炼最有价值的 3-5 个点
    valuable_points = key_points['concepts'][:5] if key_points['concepts'] else ["待提炼"]
    
    for point in valuable_points:
        summary_section += "- " + point + "\n"
    
    summary_section += "\n**行动项**:\n\n"
    for todo in key_points['todos'][:3]:
        summary_section += "- [ ] " + todo + "\n"
    
    # 检查是否已存在，避免重复
    if key_points['file'] not in content:
        content += summary_section
        with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
            f.write(content)
        log("✅ MEMORY.md 已更新")
        return True
    else:
        log("⏭️  MEMORY.md 已有此记录，跳过")
        return False

def create_knowledge_index():
    """创建知识索引文件，方便检索"""
    index_file = os.path.join(KNOWLEDGE_DIR, "INDEX.md")
    
    index_content = "# 知识库索引\n\n"
    index_content += "**更新时间**: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\n\n"
    index_content += "---\n\n"
    
    agents = ["T-01", "T-02", "T-03", "T-04", "T-05", "T-06"]
    agent_names = {
        "T-01": "首席架构师",
        "T-02": "代码特种兵",
        "T-03": "代码审计员",
        "T-04": "逻辑推理机",
        "T-05": "跨域翻译家",
        "T-06": "长文解析器"
    }
    
    for agent_id in agents:
        agent_dir = os.path.join(KNOWLEDGE_DIR, agent_id)
        if os.path.exists(agent_dir):
            files = sorted([f for f in os.listdir(agent_dir) if f.endswith('.md')], reverse=True)
            index_content += "## " + agent_id + " " + agent_names.get(agent_id, "") + "\n\n"
            index_content += "| 文件 | 字数 | 日期 |\n"
            index_content += "|------|------|------|\n"
            
            for f in files[:10]:  # 只显示最近 10 个
                filepath = os.path.join(agent_dir, f)
                words = len(open(filepath, 'r', encoding='utf-8').read().split())
                date = f.split('_')[2] if '_' in f else "未知"
                index_content += "| " + f + " | " + str(words) + " | " + date + " |\n"
            
            index_content += "\n"
    
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(index_content)
    
    log("✅ 知识索引已创建：" + index_file)

def run_refine(agent_id=None):
    """执行知识提炼"""
    log("╔════════════════════════════════════════════════════════╗")
    log("║          知识提炼 - 建立知识→行动闭环                   ║")
    log("╚════════════════════════════════════════════════════════╝")
    
    agents = [agent_id] if agent_id else ["T-01", "T-02", "T-03", "T-04", "T-05", "T-06"]
    
    for agent in agents:
        log("")
        log("📚 处理 " + agent + "...")
        
        # 获取最新学习文件
        latest_file = get_latest_knowledge(agent)
        if not latest_file:
            log("⚠️  未找到学习文件：" + agent)
            continue
        
        log("  学习文件：" + latest_file)
        
        # 提取核心要点
        key_points = extract_key_points(latest_file)
        log("  核心概念：" + str(len(key_points['concepts'])) + "个")
        log("  待办事项：" + str(len(key_points['todos'])) + "个")
        log("  总字数：" + str(key_points['word_count']))
        
        # 更新 SOP
        update_sop(agent, key_points)
        
        # 更新 MEMORY.md
        update_memory(agent, key_points)
    
    # 创建知识索引
    create_knowledge_index()
    
    log("")
    log("✅ 知识提炼完成！")
    log("")

if __name__ == "__main__":
    agent_id = sys.argv[1] if len(sys.argv) > 1 else None
    run_refine(agent_id)
