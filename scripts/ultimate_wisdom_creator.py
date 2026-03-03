#!/usr/bin/env python3
# =============================================================================
# 紫微智控 - 终极智慧创造系统 v4.0
# 功能：深度语义理解 + 自主规划 + 自我进化 + 元认知
# =============================================================================

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List

Ziwei_DIR = Path("/home/admin/Ziwei")


class UltimateWisdomCreator:
    """终极智慧创造系统 v4.0"""
    
    def __init__(self, spec_file: str):
        self.spec_file = Path(spec_file)
        self.task_id = self.spec_file.parent.name
        self.output_dir = self.spec_file.parent
        self.results = {}
    
    def step0_deep_analysis(self) -> Dict:
        """步骤 0：深度语义理解"""
        print("\n" + "=" * 70)
        print("🧠 步骤 0: 深度语义理解")
        print("=" * 70)
        
        from deep_semantic_analyzer import DeepSemanticAnalyzer
        
        with open(self.spec_file, 'r', encoding='utf-8') as f:
            spec_text = f.read()
        
        analyzer = DeepSemanticAnalyzer()
        analysis = analyzer.analyze_intent(spec_text)
        
        # 增强说明书
        enhanced_spec = analyzer.enhance_spec(spec_text, analysis)
        
        # 保存增强版
        enhanced_file = self.output_dir / "spec_enhanced.md"
        with open(enhanced_file, 'w', encoding='utf-8') as f:
            f.write(enhanced_spec)
        
        print(f"\n💾 增强版说明书：{enhanced_file}")
        
        self.results['semantic_analysis'] = analysis
        return analysis
    
    def step1_autonomous_planning(self, semantic_analysis: Dict) -> Dict:
        """步骤 1：自主任务规划"""
        print("\n" + "=" * 70)
        print("📋 步骤 1: 自主任务规划")
        print("=" * 70)
        
        from autonomous_task_planner import AutonomousTaskPlanner
        
        with open(self.spec_file, 'r', encoding='utf-8') as f:
            spec_text = f.read()
        
        planner = AutonomousTaskPlanner()
        plan = planner.plan(spec_text, semantic_analysis)
        
        # 保存任务计划
        plan_file = self.output_dir / "task_plan.json"
        with open(plan_file, 'w', encoding='utf-8') as f:
            json.dump(plan, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 任务计划：{plan_file}")
        
        self.results['task_plan'] = plan
        return plan
    
    def step2_to_8_wisdom_creation(self) -> Dict:
        """步骤 2-8：智慧创造（调用 v3.0）"""
        print("\n" + "=" * 70)
        print("🚀 步骤 2-8: 智慧创造 v3.0")
        print("=" * 70)
        
        from wisdom_creator import WisdomCreator
        
        creator = WisdomCreator(str(self.spec_file))
        result = creator.create()
        
        self.results['creation'] = result
        return result
    
    def step9_self_evolution(self, creation_result: Dict) -> Dict:
        """步骤 9：自我进化"""
        print("\n" + "=" * 70)
        print("🧬 步骤 9: 自我进化")
        print("=" * 70)
        
        from self_evolution_engine import SelfEvolutionEngine
        
        engine = SelfEvolutionEngine()
        evolution_result = engine.evolve(creation_result)
        
        self.results['evolution'] = evolution_result
        return evolution_result
    
    def step10_meta_cognition(self) -> Dict:
        """步骤 10：元认知（系统自我反思）"""
        print("\n" + "=" * 70)
        print("🤔 步骤 10: 元认知 - 系统自我反思")
        print("=" * 70)
        
        meta_report = {
            'what_worked_well': [],
            'what_could_be_better': [],
            'lessons_learned': [],
            'recommendations_for_next_time': []
        }
        
        # 分析创建过程
        creation = self.results.get('creation', {})
        evolution = self.results.get('evolution', {})
        
        # 什么做得好
        if creation.get('quality', {}).get('score', 0) >= 80:
            meta_report['what_worked_well'].append('代码质量高')
        if creation.get('tests', {}).get('passed', False):
            meta_report['what_worked_well'].append('测试通过')
        if evolution.get('applied_optimizations'):
            meta_report['what_worked_well'].append('成功应用优化')
        
        # 可以改进的地方
        if creation.get('duration', 0) > 60:
            meta_report['what_could_be_better'].append('生成速度可以提升')
        if creation.get('quality', {}).get('score', 0) < 85:
            meta_report['what_could_be_better'].append('代码质量可以继续提高')
        
        # 经验教训
        semantic = self.results.get('semantic_analysis', {})
        if semantic.get('missing_info'):
            meta_report['lessons_learned'].append('说明书应包含完整信息')
        
        # 建议
        meta_report['recommendations_for_next_time'] = [
            '提前准备完整的需求说明书',
            '明确指定技术栈偏好',
            '提供具体的使用示例'
        ]
        
        # 保存元认知报告
        meta_file = self.output_dir / "meta_cognition_report.json"
        with open(meta_file, 'w', encoding='utf-8') as f:
            json.dump(meta_report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📊 元认知报告:")
        print(f"   做得好的：{len(meta_report['what_worked_well'])} 项")
        print(f"   可改进的：{len(meta_report['what_could_be_better'])} 项")
        print(f"   经验教训：{len(meta_report['lessons_learned'])} 条")
        print(f"   建议：{len(meta_report['recommendations_for_next_time'])} 条")
        print(f"\n💾 元认知报告：{meta_file}")
        
        self.results['meta_cognition'] = meta_report
        return meta_report
    
    def create(self) -> Dict:
        """执行完整创造流程（10 步）"""
        print("\n" + "=" * 70)
        print("🌟 紫微制造 - 终极智慧创造系统 v4.0")
        print("=" * 70)
        print(f"任务：{self.task_id}")
        print(f"说明书：{self.spec_file}")
        print(f"输出：{self.output_dir}")
        print("=" * 70)
        
        start_time = datetime.now()
        
        # 步骤 0：深度语义理解
        semantic = self.step0_deep_analysis()
        
        # 步骤 1：自主任务规划
        plan = self.step1_autonomous_planning(semantic)
        
        # 步骤 2-8：智慧创造
        creation = self.step2_to_8_wisdom_creation()
        
        # 步骤 9：自我进化
        evolution = self.step9_self_evolution(creation)
        
        # 步骤 10：元认知
        meta = self.step10_meta_cognition()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # 最终报告
        print("\n" + "=" * 70)
        print("📊 终极报告 v4.0")
        print("=" * 70)
        print(f"任务 ID: {self.task_id}")
        print(f"总耗时：{duration:.2f}秒")
        print(f"语义理解：{semantic.get('intents', [{}])[0].get('intent', 'unknown')}")
        print(f"任务规划：{plan.get('total_tasks', 0)} 个任务")
        print(f"代码质量：{creation.get('quality', {}).get('score', 0)}/100")
        print(f"自我进化：{len(evolution.get('applied_optimizations', []))} 个优化")
        print(f"元认知：{len(meta.get('lessons_learned', []))} 条经验")
        print("=" * 70)
        
        return {
            'task_id': self.task_id,
            'duration': duration,
            'semantic_analysis': semantic,
            'task_plan': plan,
            'creation': creation,
            'evolution': evolution,
            'meta_cognition': meta
        }


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法：python ultimate_wisdom_creator.py <spec_file>")
        sys.exit(1)
    
    spec_file = sys.argv[1]
    
    if not Path(spec_file).exists():
        print(f"错误：文件不存在 {spec_file}")
        sys.exit(1)
    
    creator = UltimateWisdomCreator(spec_file)
    result = creator.create()
    
    # 保存终极报告
    report_file = Path(spec_file).parent / "ultimate_creation_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump({
            'task_id': result['task_id'],
            'duration': result['duration'],
            'quality_score': result['creation'].get('quality', {}).get('score', 0),
            'evolution_applied': len(result['evolution'].get('applied_optimizations', [])),
            'meta_lessons': len(result['meta_cognition'].get('lessons_learned', [])),
            'timestamp': datetime.now().isoformat()
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 终极报告：{report_file}")


if __name__ == '__main__':
    main()
