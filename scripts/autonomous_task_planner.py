#!/usr/bin/env python3
# =============================================================================
# 自主任务规划引擎
# 功能：AI 自主分解任务 + 智能排序 + 并行执行规划
# =============================================================================

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


class AutonomousTaskPlanner:
    """自主任务规划引擎"""
    
    def __init__(self):
        self.task_templates = {
            'cli_tool': [
                {'name': '项目结构创建', 'priority': 1, 'estimated_time': 5},
                {'name': '核心功能实现', 'priority': 2, 'estimated_time': 30},
                {'name': '命令行接口', 'priority': 3, 'estimated_time': 15},
                {'name': '错误处理', 'priority': 4, 'estimated_time': 10},
                {'name': '文档编写', 'priority': 5, 'estimated_time': 10},
                {'name': '单元测试', 'priority': 6, 'estimated_time': 15}
            ],
            'web_service': [
                {'name': '项目结构', 'priority': 1, 'estimated_time': 5},
                {'name': '路由定义', 'priority': 2, 'estimated_time': 20},
                {'name': '数据模型', 'priority': 3, 'estimated_time': 20},
                {'name': '业务逻辑', 'priority': 4, 'estimated_time': 30},
                {'name': 'API 文档', 'priority': 5, 'estimated_time': 10},
                {'name': '测试用例', 'priority': 6, 'estimated_time': 20}
            ],
            'data_processing': [
                {'name': '数据加载模块', 'priority': 1, 'estimated_time': 15},
                {'name': '数据验证', 'priority': 2, 'estimated_time': 15},
                {'name': '转换逻辑', 'priority': 3, 'estimated_time': 30},
                {'name': '输出模块', 'priority': 4, 'estimated_time': 10},
                {'name': '错误处理', 'priority': 5, 'estimated_time': 10},
                {'name': '性能优化', 'priority': 6, 'estimated_time': 15}
            ]
        }
    
    def plan(self, spec_text: str, intent_analysis: Dict) -> Dict:
        """自主规划任务"""
        print("\n📋 自主任务规划...")
        
        # 1. 选择任务模板
        intent = intent_analysis.get('intents', [{}])[0].get('intent', 'cli_tool')
        template = self.task_templates.get(intent, self.task_templates['cli_tool'])
        
        # 2. 根据复杂度调整
        complexity = intent_analysis.get('complexity_score', 5)
        adjusted_tasks = self.adjust_for_complexity(template, complexity)
        
        # 3. 添加自定义任务（基于需求分析）
        custom_tasks = self.generate_custom_tasks(spec_text, intent_analysis)
        adjusted_tasks.extend(custom_tasks)
        
        # 4. 智能排序
        sorted_tasks = self.intelligent_sort(adjusted_tasks)
        
        # 5. 并行执行规划
        parallel_plan = self.create_parallel_plan(sorted_tasks)
        
        # 6. 时间估算
        total_time = sum(t.get('estimated_time', 10) for t in sorted_tasks)
        
        plan = {
            'tasks': sorted_tasks,
            'parallel_groups': parallel_plan,
            'total_tasks': len(sorted_tasks),
            'estimated_time_minutes': total_time,
            'critical_path': self.identify_critical_path(sorted_tasks),
            'dependencies': self.extract_dependencies(sorted_tasks)
        }
        
        print(f"   任务总数：{len(sorted_tasks)}")
        print(f"   预计时间：{total_time} 分钟")
        print(f"   并行组数：{len(parallel_plan)}")
        print(f"   关键路径：{len(plan['critical_path'])} 个任务")
        
        return plan
    
    def adjust_for_complexity(self, tasks: List[Dict], complexity: int) -> List[Dict]:
        """根据复杂度调整任务"""
        adjusted = []
        
        for task in tasks:
            new_task = task.copy()
            
            # 高复杂度增加时间估算
            if complexity >= 7:
                new_task['estimated_time'] = int(task['estimated_time'] * 1.5)
            
            # 高复杂度添加额外任务
            if complexity >= 8 and task['name'] == '核心功能实现':
                adjusted.append({
                    'name': '架构设计',
                    'priority': task['priority'] - 0.5,
                    'estimated_time': 20,
                    'auto_generated': True
                })
            
            adjusted.append(new_task)
        
        return adjusted
    
    def generate_custom_tasks(self, spec_text: str, analysis: Dict) -> List[Dict]:
        """生成自定义任务"""
        custom = []
        
        # 基于功能建议生成任务
        for feature in analysis.get('feature_suggestions', [])[:3]:
            if feature['priority'] == 'high':
                custom.append({
                    'name': f"实现{feature['name']}",
                    'priority': 3.5,
                    'estimated_time': 15,
                    'description': feature['description'],
                    'auto_generated': True
                })
        
        # 基于风险生成任务
        for risk in analysis.get('risks', [])[:2]:
            if risk['severity'] == 'high':
                custom.append({
                    'name': f"处理{risk['type']}风险",
                    'priority': 2.5,
                    'estimated_time': 10,
                    'description': risk['mitigation'],
                    'auto_generated': True
                })
        
        return custom
    
    def intelligent_sort(self, tasks: List[Dict]) -> List[Dict]:
        """智能排序"""
        # 按优先级排序
        sorted_tasks = sorted(tasks, key=lambda x: x['priority'])
        
        # 调整依赖关系
        for i, task in enumerate(sorted_tasks):
            if '架构' in task['name'] or '设计' in task['name']:
                # 架构设计类任务提前
                task['priority'] = max(0.5, task['priority'] - 1)
            elif '测试' in task['name'] or '文档' in task['name']:
                # 测试和文档靠后
                task['priority'] = task['priority'] + 1
        
        # 重新排序
        sorted_tasks = sorted(sorted_tasks, key=lambda x: x['priority'])
        
        return sorted_tasks
    
    def create_parallel_plan(self, tasks: List[Dict]) -> List[List[Dict]]:
        """创建并行执行计划"""
        groups = []
        
        # 可以并行的任务组
        parallel_groups = [
            ['文档编写', '单元测试'],
            ['错误处理', '性能优化'],
            ['API 文档', '测试用例']
        ]
        
        remaining = tasks.copy()
        
        for group_template in parallel_groups:
            group = []
            for task_name in group_template:
                for task in remaining:
                    if task_name in task['name']:
                        group.append(task)
                        remaining.remove(task)
                        break
            
            if len(group) > 1:
                groups.append(group)
        
        # 剩余任务单独成组
        for task in remaining:
            groups.append([task])
        
        return groups
    
    def identify_critical_path(self, tasks: List[Dict]) -> List[str]:
        """识别关键路径"""
        # 高优先级任务是关键路径
        critical = [t['name'] for t in tasks if t['priority'] <= 3]
        return critical
    
    def extract_dependencies(self, tasks: List[Dict]) -> Dict[str, List[str]]:
        """提取依赖关系"""
        deps = {}
        
        task_names = [t['name'] for t in tasks]
        
        # 预定义依赖
        dependency_rules = {
            '核心功能实现': ['项目结构创建'],
            '业务逻辑': ['数据模型', '路由定义'],
            '单元测试': ['核心功能实现'],
            '性能优化': ['核心功能实现']
        }
        
        for task_name in task_names:
            deps[task_name] = []
            for rule_task, prerequisites in dependency_rules.items():
                if rule_task in task_name:
                    deps[task_name] = [p for p in prerequisites if any(p in t for t in task_names)]
        
        return deps
    
    def generate_execution_order(self, plan: Dict) -> List[List[str]]:
        """生成执行顺序"""
        order = []
        
        for group in plan['parallel_groups']:
            group_names = [t['name'] for t in group]
            order.append(group_names)
        
        return order


def main():
    """主函数"""
    planner = AutonomousTaskPlanner()
    
    spec = "创建一个 JSON 验证工具"
    analysis = {
        'intents': [{'intent': 'cli_tool', 'confidence': 0.8}],
        'complexity_score': 5,
        'feature_suggestions': [],
        'risks': []
    }
    
    plan = planner.plan(spec, analysis)
    
    print("\n📊 任务规划完成")
    print(f"   总任务：{plan['total_tasks']}")
    print(f"   预计时间：{plan['estimated_time_minutes']} 分钟")


if __name__ == '__main__':
    main()
