#!/usr/bin/env python3
# =============================================================================
# 紫微智控 - 智能自动创造系统 v2.0
# 功能：知识检索 → AI 代码生成 → 自动测试 → 质量评估 → 学习反馈
# =============================================================================

import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List

Ziwei_DIR = Path("/home/admin/Ziwei")
SCRIPTS_DIR = Ziwei_DIR / "scripts"


class IntelligentCreator:
    """智能自动创造系统"""
    
    def __init__(self, spec_file: str):
        self.spec_file = Path(spec_file)
        self.task_id = self.spec_file.parent.name
        self.output_dir = self.spec_file.parent
        self.results = {
            "knowledge": None,
            "code": None,
            "tests": None,
            "quality": None,
            "feedback": None
        }
        
    def step1_knowledge_retrieval(self) -> Dict:
        """步骤 1：智能知识检索"""
        print("\n" + "=" * 70)
        print("📚 步骤 1: 智能知识检索")
        print("=" * 70)
        
        # 调用智能检索器
        from smart_retriever import SmartKnowledgeRetriever
        
        retriever = SmartKnowledgeRetriever()
        results = retriever.retrieve(str(self.spec_file))
        
        self.results["knowledge"] = results
        return results
    
    def step2_ai_code_generation(self, knowledge: Dict) -> Dict:
        """步骤 2：AI 代码生成（增强版：模板+AI 模型）"""
        print("\n" + "=" * 70)
        print("🤖 步骤 2: AI 代码生成（增强版）")
        print("=" * 70)
        
        # 1. 先应用模板
        print("\n📋 应用项目模板...")
        from template_engine import ProjectTemplateEngine
        
        with open(self.spec_file, 'r', encoding='utf-8') as f:
            spec_text = f.read()
        
        # 解析说明书
        spec = {
            'name': self.task_id,
            'description': '项目描述',
            'spec_text': spec_text
        }
        
        if '任务名称' in spec_text:
            spec['name'] = spec_text.split('任务名称')[1].split('\n')[1].strip()
        if '任务描述' in spec_text:
            spec['description'] = spec_text.split('任务描述')[1].split('\n')[1].strip()
        
        engine = ProjectTemplateEngine()
        template_name = engine.select_template(spec_text)
        engine.apply_template(template_name, str(self.output_dir), spec)
        
        # 2. 再调用 AI 增强
        print("\n🤖 AI 模型增强...")
        from ai_code_generator import AICodeGenerator
        
        generator = AICodeGenerator(str(self.spec_file), knowledge)
        results = generator.generate(str(self.output_dir))
        
        self.results["code"] = results
        return results
    
    def step3_auto_test(self, code: str) -> Dict:
        """步骤 3：自动测试"""
        print("\n" + "=" * 70)
        print("🧪 步骤 3: 自动测试")
        print("=" * 70)
        
        test_file = self.output_dir / "tests" / f"test_{self.spec_file.stem}.py"
        
        if not test_file.exists():
            print("   ⚠️ 测试文件不存在")
            return {"passed": False, "error": "测试文件不存在"}
        
        # 运行测试
        try:
            result = os.system(f"cd {self.output_dir} && python3 -m pytest tests/ -v --tb=short 2>/dev/null || python3 tests/{test_file.name}")
            
            if result == 0:
                print("   ✅ 所有测试通过")
                test_result = {"passed": True, "result": "success"}
            else:
                print("   ⚠️ 部分测试失败")
                test_result = {"passed": False, "result": "failed"}
        except Exception as e:
            print(f"   ⚠️ 测试执行失败：{e}")
            test_result = {"passed": False, "error": str(e)}
        
        self.results["tests"] = test_result
        return test_result
    
    def step4_quality_assessment(self) -> Dict:
        """步骤 4：质量评估"""
        print("\n" + "=" * 70)
        print("⭐ 步骤 4: 质量评估")
        print("=" * 70)
        
        quality_file = self.output_dir / "quality_report.json"
        
        if quality_file.exists():
            with open(quality_file, 'r', encoding='utf-8') as f:
                quality = json.load(f)
            
            print(f"   质量评分：{quality.get('score', 0)}/100")
            print(f"   等级：{quality.get('level', 'Unknown')}")
            
            self.results["quality"] = quality
            return quality
        else:
            print("   ⚠️ 质量报告不存在")
            return {"score": 0, "level": "Unknown"}
    
    def step5_learning_feedback(self) -> Dict:
        """步骤 5：学习反馈（增强版：持续学习）"""
        print("\n" + "=" * 70)
        print("📖 步骤 5: 学习反馈（持续学习）")
        print("=" * 70)
        
        feedback = {
            "task_id": self.task_id,
            "timestamp": datetime.now().isoformat(),
            "success": self.results["quality"].get("score", 0) >= 80,
            "quality_score": self.results["quality"].get("score", 0),
            "iterations": self.results["code"].get("iterations", 0) if self.results["code"] else 0,
            "tests_passed": self.results["tests"].get("passed", False) if self.results["tests"] else False
        }
        
        # 保存反馈
        feedback_file = self.output_dir / "feedback.json"
        with open(feedback_file, 'w', encoding='utf-8') as f:
            json.dump(feedback, f, indent=2, ensure_ascii=False)
        
        print(f"   任务 ID: {feedback['task_id']}")
        print(f"   成功：{'✅' if feedback['success'] else '❌'}")
        print(f"   质量评分：{feedback['quality_score']}/100")
        print(f"   迭代次数：{feedback['iterations']}")
        print(f"   测试通过：{'✅' if feedback['tests_passed'] else '❌'}")
        print(f"\n   💾 反馈已保存：{feedback_file}")
        
        # 持续学习
        print("\n🧠 持续学习...")
        try:
            from continuous_learner import ContinuousLearner
            learner = ContinuousLearner()
            
            # 读取代码
            code_file = self.output_dir / "src" / f"{self.spec_file.stem}.py"
            if code_file.exists():
                with open(code_file, 'r', encoding='utf-8') as f:
                    code = f.read()
                
                # 从成功/失败中学习
                if feedback['success']:
                    learner.learn_from_success(feedback, code, str(self.spec_file))
                else:
                    learner.learn_from_failure(feedback, code, str(self.spec_file), [])
                
                # 获取推荐
                with open(self.spec_file, 'r', encoding='utf-8') as f:
                    spec_text = f.read()
                recommendations = learner.get_recommendations(spec_text)
                
                if recommendations:
                    print(f"   💡 推荐实践：{', '.join(recommendations[:3])}")
            
        except Exception as e:
            print(f"   ⚠️ 持续学习失败：{e}")
        
        self.results["feedback"] = feedback
        return feedback
    
    def create(self) -> Dict:
        """执行完整创造流程"""
        print("\n" + "=" * 70)
        print("🚀 紫微智控 - 智能自动创造系统 v2.0")
        print("=" * 70)
        print(f"任务：{self.task_id}")
        print(f"说明书：{self.spec_file}")
        print(f"输出：{self.output_dir}")
        print("=" * 70)
        
        start_time = datetime.now()
        
        # 步骤 1：知识检索
        knowledge = self.step1_knowledge_retrieval()
        
        # 步骤 2：AI 代码生成
        code = self.step2_ai_code_generation(knowledge)
        
        # 步骤 3：自动测试
        tests = self.step3_auto_test(code.get("code", "") if code else "")
        
        # 步骤 4：质量评估
        quality = self.step4_quality_assessment()
        
        # 步骤 5：学习反馈
        feedback = self.step5_learning_feedback()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # 最终报告
        print("\n" + "=" * 70)
        print("📊 最终报告")
        print("=" * 70)
        print(f"任务 ID: {self.task_id}")
        print(f"总耗时：{duration:.2f}秒")
        print(f"知识检索：{len(knowledge.get('local_knowledge', []))} 个本地资源")
        print(f"代码生成：{len(code.get('code', ''))} 字节")
        print(f"测试状态：{'✅ 通过' if tests.get('passed') else '❌ 失败'}")
        print(f"质量评分：{quality.get('score', 0)}/100 ({quality.get('level', 'Unknown')})")
        print(f"学习反馈：{'✅ 已记录' if feedback.get('success') else '⚠️ 需改进'}")
        print("=" * 70)
        
        return {
            "task_id": self.task_id,
            "duration": duration,
            "knowledge": knowledge,
            "code": code,
            "tests": tests,
            "quality": quality,
            "feedback": feedback
        }


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法：python intelligent_creator.py <spec_file>")
        print("示例：python intelligent_creator.py /home/admin/Ziwei/tasks/TASK-001/spec.md")
        sys.exit(1)
    
    spec_file = sys.argv[1]
    
    if not Path(spec_file).exists():
        print(f"错误：文件不存在 {spec_file}")
        sys.exit(1)
    
    creator = IntelligentCreator(spec_file)
    result = creator.create()
    
    # 保存总报告
    report_file = Path(spec_file).parent / "creation_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump({
            "task_id": result["task_id"],
            "duration": result["duration"],
            "success": result["quality"].get("score", 0) >= 80,
            "quality_score": result["quality"].get("score", 0),
            "timestamp": datetime.now().isoformat()
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 总报告已保存：{report_file}")


if __name__ == '__main__':
    main()
