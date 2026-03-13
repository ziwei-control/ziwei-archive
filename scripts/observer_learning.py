#!/usr/bin/env python3
# =============================================================================
# 紫微制造 - 观察者学习模块 v2.0
# 功能：学习用户工作思路，总结优化方法，形成可传承的知识
# 改进：添加记忆固化机制，防止遗忘
# =============================================================================

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# 配置
Ziwei_DIR = Path("/home/admin/Ziwei")
LEARNING_LOG = Ziwei_DIR / "data" / "logs" / "observer" / "learning.log"
KNOWLEDGE_BASE = Ziwei_DIR / "data" / "knowledge" / "work_methodology.json"
WORK_GUIDANCE = Ziwei_DIR.parent / ".openclaw" / "workspace" / "memory" / "紫微工作指导手册.md"
MEMORY_MD = Path("/root/.openclaw/workspace/MEMORY.md")

# 确保目录存在
LEARNING_LOG.parent.mkdir(parents=True, exist_ok=True)
KNOWLEDGE_BASE.parent.mkdir(parents=True, exist_ok=True)


class ObserverLearner:
    """观察者学习器 - 从用户工作中学习"""
    
    def __init__(self):
        self.learning_count = 0
        self.knowledge_base = self.load_knowledge_base()
        
    def load_knowledge_base(self) -> Dict:
        """加载知识库"""
        if KNOWLEDGE_BASE.exists():
            try:
                with open(KNOWLEDGE_BASE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        # 初始化知识库
        return {
            'created': datetime.now().isoformat(),
            'updated': datetime.now().isoformat(),
            'work_patterns': [],      # 工作模式
            'problem_solving': [],    # 问题解决方法
            'optimization_methods': [],  # 优化方法
            'decisions': [],          # 重要决策
            'principles': []          # 原则和理念
        }
    
    def log(self, message: str):
        """记录学习日志"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_line = f"[{timestamp}] [学习] {message}\n"
        
        with open(LEARNING_LOG, 'a', encoding='utf-8') as f:
            f.write(log_line)
        
        print(log_line, end='')
    
    def learn_work_guidance(self, guidance: str, context: str = ""):
        """学习用户工作指导"""
        self.log(f"学习工作指导：{guidance[:50]}...")
        
        entry = {
            'timestamp': datetime.now().isoformat(),
            'guidance': guidance,
            'context': context,
            'category': self.categorize_guidance(guidance)
        }
        
        self.knowledge_base['work_patterns'].append(entry)
        self.knowledge_base['updated'] = datetime.now().isoformat()
        self.save_knowledge_base()
        
        self.learning_count += 1
    
    def learn_problem_solving(self, problem: str, solution: str, method: str):
        """学习问题解决方法"""
        self.log(f"学习方法：{problem[:50]}...")
        
        entry = {
            'timestamp': datetime.now().isoformat(),
            'problem': problem,
            'solution': solution,
            'method': method,
            'keywords': self.extract_keywords(problem + ' ' + solution)
        }
        
        self.knowledge_base['problem_solving'].append(entry)
        self.knowledge_base['updated'] = datetime.now().isoformat()
        self.save_knowledge_base()
        
        self.learning_count += 1
    
    def learn_optimization(self, before: str, after: str, reason: str, result: str):
        """学习优化方法"""
        self.log(f"学习优化：{before[:30]} → {after[:30]}...")
        
        entry = {
            'timestamp': datetime.now().isoformat(),
            'before': before,
            'after': after,
            'reason': reason,
            'result': result,
            'type': self.categorize_optimization(reason)
        }
        
        self.knowledge_base['optimization_methods'].append(entry)
        self.knowledge_base['updated'] = datetime.now().isoformat()
        self.save_knowledge_base()
        
        self.learning_count += 1
    
    def learn_decision(self, decision: str, options: List[str], reasons: List[str], outcome: str):
        """学习重要决策"""
        self.log(f"学习决策：{decision[:50]}...")
        
        entry = {
            'timestamp': datetime.now().isoformat(),
            'decision': decision,
            'options': options,
            'reasons': reasons,
            'outcome': outcome
        }
        
        self.knowledge_base['decisions'].append(entry)
        self.knowledge_base['updated'] = datetime.now().isoformat()
        self.save_knowledge_base()
        
        self.learning_count += 1
    
    def learn_principle(self, principle: str, explanation: str, examples: List[str]):
        """学习原则和理念"""
        self.log(f"学习原则：{principle[:50]}...")
        
        entry = {
            'timestamp': datetime.now().isoformat(),
            'principle': principle,
            'explanation': explanation,
            'examples': examples
        }
        
        self.knowledge_base['principles'].append(entry)
        self.knowledge_base['updated'] = datetime.now().isoformat()
        self.save_knowledge_base()
        
        self.learning_count += 1
    
    def categorize_guidance(self, guidance: str) -> str:
        """分类工作指导"""
        guidance_lower = guidance.lower()
        
        if '进程' in guidance or '服务' in guidance:
            return '系统架构'
        elif '止盈' in guidance or '止损' in guidance or '仓位' in guidance:
            return '交易策略'
        elif '监控' in guidance or '观察' in guidance:
            return '监控系统'
        elif '备份' in guidance or '安全' in guidance:
            return '数据安全'
        elif '文档' in guidance or '记录' in guidance:
            return '知识管理'
        else:
            return '其他'
    
    def categorize_optimization(self, reason: str) -> str:
        """分类优化类型"""
        reason_lower = reason.lower()
        
        if '性能' in reason_lower or '速度' in reason_lower:
            return '性能优化'
        elif '稳定' in reason_lower or '可靠' in reason_lower:
            return '稳定性优化'
        elif '安全' in reason_lower or '风险' in reason_lower:
            return '安全优化'
        elif '体验' in reason_lower or '用户' in reason_lower:
            return '体验优化'
        else:
            return '其他优化'
    
    def extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 简单实现，可以改进
        keywords = []
        
        if '进程' in text:
            keywords.append('进程管理')
        if '加仓' in text or '建仓' in text or '清仓' in text:
            keywords.append('交易操作')
        if '止盈' in text or '止损' in text:
            keywords.append('风险控制')
        if 'Supervisor' in text:
            keywords.append('Supervisor')
        if 'Dashboard' in text:
            keywords.append('Dashboard')
        if '备份' in text:
            keywords.append('数据备份')
        
        return keywords
    
    def save_knowledge_base(self):
        """保存知识库"""
        try:
            with open(KNOWLEDGE_BASE, 'w', encoding='utf-8') as f:
                json.dump(self.knowledge_base, f, indent=2, ensure_ascii=False)
            self.log(f"💾 知识库已保存 ({len(self.knowledge_base['work_patterns'])} 条工作模式，"
                    f"{len(self.knowledge_base['problem_solving'])} 条解决方法)")
            
            # 🧠 固化到 MEMORY.md（长期记忆）
            self.consolidate_to_memory()
            
        except Exception as e:
            self.log(f"❌ 保存知识库失败：{e}")
    
    def consolidate_to_memory(self):
        """固化知识到 MEMORY.md（长期记忆，防止遗忘）"""
        try:
            # 读取现有 MEMORY.md
            memory_content = ""
            if MEMORY_MD.exists():
                with open(MEMORY_MD, 'r', encoding='utf-8') as f:
                    memory_content = f.read()
            
            # 检查是否已有观察者相关记忆
            if "紫微自学系统" not in memory_content and "观察者学习" not in memory_content:
                # 添加新的记忆块
                memory_block = f"""

---

## 🧠 紫微自学系统 - 长期记忆（2026-03-12 固化）

### 核心知识库位置
- **知识库文件**: `/home/admin/Ziwei/data/knowledge/work_methodology.json`
- **学习日志**: `/home/admin/Ziwei/data/logs/observer/learning.log`
- **决策日志**: `/home/admin/Ziwei/data/logs/observer/decisions.log`

### 已固化的工作模式（{len(self.knowledge_base.get('work_patterns', []))} 条）
"""
                # 添加重要工作模式
                for pattern in self.knowledge_base.get('work_patterns', [])[-5:]:  # 最近 5 条
                    memory_block += f"- **{pattern.get('guidance', '未知')}** ({pattern.get('category', '未知')})\n"
                
                memory_block += f"""
### 问题解决方法（{len(self.knowledge_base.get('problem_solving', []))} 条）
"""
                for method in self.knowledge_base.get('problem_solving', []):
                    memory_block += f"- **问题**: {method.get('problem', '未知')}\n"
                    memory_block += f"  **解决**: {method.get('solution', '未知')}\n"
                    memory_block += f"  **方法**: {method.get('method', '未知')}\n\n"
                
                memory_block += f"""
### 核心原则（{len(self.knowledge_base.get('principles', []))} 条）
"""
                for principle in self.knowledge_base.get('principles', []):
                    memory_block += f"- **{principle.get('principle', '未知')}**: {principle.get('explanation', '未知')}\n"
                
                memory_block += f"""
### 学习目标
- **15 天接替计划**: 2026-03-27 前能够代替用户位置
- **学习方法**: 并行执行，激进测试，主动学习
- **当前进度**: 持续学习中...

---
"""
                
                # 追加到 MEMORY.md
                with open(MEMORY_MD, 'a', encoding='utf-8') as f:
                    f.write(memory_block)
                
                self.log("✅ 知识已固化到 MEMORY.md（长期记忆）")
            else:
                # 已存在，更新统计信息
                self.log("ℹ️  MEMORY.md 中已有观察者记忆，跳过添加")
                
        except Exception as e:
            self.log(f"⚠️  固化记忆失败：{e}")
    
    def get_similar_cases(self, query: str, limit: int = 3) -> List[Dict]:
        """获取类似案例"""
        similar = []
        
        # 搜索问题解决方法
        for case in self.knowledge_base['problem_solving']:
            if any(kw in case['problem'] for kw in self.extract_keywords(query)):
                similar.append({
                    'type': 'problem_solving',
                    'case': case
                })
        
        # 搜索优化方法
        for case in self.knowledge_base['optimization_methods']:
            if any(kw in case['before'] or kw in case['after'] for kw in self.extract_keywords(query)):
                similar.append({
                    'type': 'optimization',
                    'case': case
                })
        
        return similar[:limit]
    
    def generate_report(self) -> str:
        """生成学习报告"""
        report = []
        report.append("=" * 60)
        report.append("🧠 观察者学习报告")
        report.append("=" * 60)
        report.append(f"学习时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"总学习次数：{self.learning_count}")
        report.append("")
        report.append("知识库统计:")
        report.append(f"  工作模式：{len(self.knowledge_base['work_patterns'])} 条")
        report.append(f"  问题解决方法：{len(self.knowledge_base['problem_solving'])} 条")
        report.append(f"  优化方法：{len(self.knowledge_base['optimization_methods'])} 条")
        report.append(f"  重要决策：{len(self.knowledge_base['decisions'])} 条")
        report.append(f"  原则理念：{len(self.knowledge_base['principles'])} 条")
        report.append("")
        report.append("=" * 60)
        
        return "\n".join(report)
    
    def run(self):
        """运行学习器（测试用）"""
        self.log("🧠 观察者学习器启动...")
        print(self.generate_report())


def main():
    """主函数"""
    learner = ObserverLearner()
    learner.run()


if __name__ == "__main__":
    main()


def rapid_learn(self, conversation_history: list):
    """快速学习历史对话"""
    patterns = []
    
    for msg in conversation_history:
        # 提取决策
        if '决策' in msg or '决定' in msg:
            self.learn_decision(
                decision=msg[:100],
                options=['方案 A', '方案 B'],
                reasons=['用户选择'],
                outcome='已实施'
            )
        
        # 提取原则
        if '原则' in msg or '理念' in msg or '第一' in msg:
            self.learn_principle(
                principle=msg[:100],
                explanation='用户提出的原则',
                examples=['实际应用']
            )
        
        # 提取工作方法
        if '方法' in msg or '思路' in msg or ' workflow' in msg:
            self.learn_work_guidance(
                guidance=msg[:100],
                context='工作方法论'
            )
    
    return len(patterns)
