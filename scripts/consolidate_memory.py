#!/usr/bin/env python3
# =============================================================================
# 紫微制造 - 记忆固化脚本
# 功能：定期将知识库固化到 MEMORY.md，防止遗忘
# 运行：每 6 小时运行一次
# =============================================================================

import json
import sys
from datetime import datetime
from pathlib import Path

# 配置
Ziwei_DIR = Path("/home/admin/Ziwei")
KNOWLEDGE_BASE = Ziwei_DIR / "data" / "knowledge" / "work_methodology.json"
MEMORY_MD = Path("/root/.openclaw/workspace/MEMORY.md")

def consolidate_memory():
    """固化知识库到 MEMORY.md"""
    print(f"[{datetime.now()}] 🔄 开始记忆固化...")
    
    # 加载知识库
    if not KNOWLEDGE_BASE.exists():
        print("❌ 知识库不存在")
        return
    
    with open(KNOWLEDGE_BASE, 'r', encoding='utf-8') as f:
        kb = json.load(f)
    
    # 检查 MEMORY.md
    memory_exists = MEMORY_MD.exists()
    memory_content = ""
    if memory_exists:
        with open(MEMORY_MD, 'r', encoding='utf-8') as f:
            memory_content = f.read()
    
    # 构建记忆块
    memory_block = f"""

---

## 🧠 紫微自学系统 - 定期固化记忆（{datetime.now().strftime('%Y-%m-%d %H:%M')}）

### 学习统计
- **工作模式**: {len(kb.get('work_patterns', []))} 条
- **问题解决方法**: {len(kb.get('problem_solving', []))} 条
- **优化方法**: {len(kb.get('optimization_methods', []))} 条
- **重要决策**: {len(kb.get('decisions', []))} 条
- **原则理念**: {len(kb.get('principles', []))} 条
- **学习日志**: 约 {sum(1 for _ in open(Ziwei_DIR / 'data/logs/observer/learning.log')):,} 条
- **决策日志**: 约 {sum(1 for _ in open(Ziwei_DIR / 'data/logs/observer/decisions.log')):,} 条

### 最近学到的重要内容
"""
    
    # 添加最近的工作模式
    memory_block += "\n#### 最近工作模式\n"
    for pattern in kb.get('work_patterns', [])[-3:]:
        memory_block += f"- {pattern.get('guidance', '未知')} ({pattern.get('category', '未知')})\n"
    
    # 添加最近的决策
    memory_block += "\n#### 最近决策\n"
    for decision in kb.get('decisions', [])[-2:]:
        memory_block += f"- {decision.get('decision', '未知')}\n"
    
    memory_block += f"""
### 知识库位置
- 知识库：`/home/admin/Ziwei/data/knowledge/work_methodology.json`
- 学习日志：`/home/admin/Ziwei/data/logs/observer/learning.log`
- 决策日志：`/home/admin/Ziwei/data/logs/observer/decisions.log`

### 下次固化时间
6 小时后自动固化

---
"""
    
    # 追加到 MEMORY.md
    with open(MEMORY_MD, 'a', encoding='utf-8') as f:
        f.write(memory_block)
    
    print(f"✅ 记忆固化完成！")
    print(f"   工作模式：{len(kb.get('work_patterns', []))} 条")
    print(f"   问题解决方法：{len(kb.get('problem_solving', []))} 条")
    print(f"   优化方法：{len(kb.get('optimization_methods', []))} 条")
    print(f"   重要决策：{len(kb.get('decisions', []))} 条")
    print(f"   原则理念：{len(kb.get('principles', []))} 条")


if __name__ == "__main__":
    consolidate_memory()
