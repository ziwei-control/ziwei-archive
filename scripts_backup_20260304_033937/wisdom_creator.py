#!/usr/bin/env python3
# =============================================================================
# 紫微智控 - 智慧创造系统 v3.0
# 功能：知识检索 + AI 代码生成 + 模板 + 多语言 + 自动修复 + 知识图谱 + 自动部署 + 持续学习
# =============================================================================

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List

Ziwei_DIR = Path("/home/admin/Ziwei")
SCRIPTS_DIR = Ziwei_DIR / "scripts"


class WisdomCreator:
    """智慧创造系统 v3.0"""
    
    def __init__(self, spec_file: str):
        self.spec_file = Path(spec_file)
        self.task_id = self.spec_file.parent.name
        self.output_dir = self.spec_file.parent
        self.results = {}
        
    def step1_knowledge_retrieval(self) -> Dict:
        """步骤 1：智能知识检索（增强版）"""
        print("\n" + "=" * 70)
        print("📚 步骤 1: 智能知识检索（增强版）")
        print("=" * 70)
        
        # 使用增强版 web_search
        from enhanced_web_search import EnhancedWebSearch
        
        with open(self.spec_file, 'r', encoding='utf-8') as f:
            spec_text = f.read()
        
        # 提取关键词
        keywords = self._extract_keywords(spec_text)
        
        # 执行搜索
        searcher = EnhancedWebSearch()
        web_results = []
        
        for keyword in keywords[:3]:  # 最多 3 个关键词
            results = searcher.search(keyword, count=5)
            web_results.extend(results)
        
        # 整合结果
        knowledge = {
            'local': [],  # 本地知识
            'web': web_results,
            'github': [],
            'keywords': keywords
        }
        
        print(f"\n📊 知识检索完成:")
        print(f"   关键词：{', '.join(keywords)}")
        print(f"   网络资源：{len(web_results)} 个")
        
        self.results['knowledge'] = knowledge
        return knowledge
    
    def step2_template_selection(self, knowledge: Dict) -> str:
        """步骤 2：模板选择"""
        print("\n" + "=" * 70)
        print("📋 步骤 2: 模板选择")
        print("=" * 70)
        
        from template_engine import ProjectTemplateEngine
        
        with open(self.spec_file, 'r', encoding='utf-8') as f:
            spec_text = f.read()
        
        engine = ProjectTemplateEngine()
        template_name = engine.select_template(spec_text)
        
        self.results['template'] = template_name
        return template_name
    
    def step3_language_selection(self) -> str:
        """步骤 3：语言选择"""
        print("\n" + "=" * 70)
        print("🌐 步骤 3: 语言选择")
        print("=" * 70)
        
        from multi_language_generator import MultiLanguageGenerator
        
        with open(self.spec_file, 'r', encoding='utf-8') as f:
            spec_text = f.read()
        
        generator = MultiLanguageGenerator()
        language = generator.select_language(spec_text)
        
        self.results['language'] = language
        return language
    
    def step4_ai_code_generation(self, knowledge: Dict, template: str, language: str) -> Dict:
        """步骤 4：AI 代码生成（增强版）"""
        print("\n" + "=" * 70)
        print("🤖 步骤 4: AI 代码生成（增强版）")
        print("=" * 70)
        
        # 1. 应用模板
        from template_engine import ProjectTemplateEngine
        
        with open(self.spec_file, 'r', encoding='utf-8') as f:
            spec_text = f.read()
        
        spec = {
            'name': self.task_id,
            'description': spec_text.split('任务描述')[1].split('\n')[1].strip() if '任务描述' in spec_text else '项目',
            'spec_text': spec_text
        }
        
        engine = ProjectTemplateEngine()
        engine.apply_template(template, str(self.output_dir), spec)
        
        # 2. AI 生成
        from ai_code_generator import AICodeGenerator
        
        generator = AICodeGenerator(str(self.spec_file), knowledge)
        code_result = generator.generate(str(self.output_dir))
        
        # 3. 自动修复
        from auto_code_fixer import AutoCodeFixer
        
        if code_result.get('code'):
            fixer = AutoCodeFixer()
            fixed_code, fix_analysis = fixer.fix_all(code_result['code'])
            
            # 保存修复后的代码
            code_file = self.output_dir / "src" / f"{self.spec_file.stem}.py"
            if code_file.exists():
                with open(code_file, 'w', encoding='utf-8') as f:
                    f.write(fixed_code)
            
            code_result['fix_analysis'] = fix_analysis
            code_result['fixes_applied'] = len(fixer.fixes_applied)
        
        self.results['code'] = code_result
        return code_result
    
    def step5_knowledge_graph(self, knowledge: Dict) -> Dict:
        """步骤 5：知识图谱构建"""
        print("\n" + "=" * 70)
        print("🕸️ 步骤 5: 知识图谱")
        print("=" * 70)
        
        try:
            from knowledge_graph import KnowledgeGraph
            
            kg = KnowledgeGraph()
            
            # 构建图谱
            graph = kg.build_from_knowledge(knowledge)
            
            # 推理
            inferences = kg.infer_new_knowledge()
            
            # 保存
            graph_file = self.output_dir / "knowledge_graph.json"
            kg.visualize(str(graph_file))
            
            kg_result = {
                'nodes': graph.number_of_nodes(),
                'edges': graph.number_of_edges(),
                'inferences': len(inferences)
            }
            
            self.results['knowledge_graph'] = kg_result
            return kg_result
            
        except Exception as e:
            print(f"   ⚠️ 知识图谱失败：{e}")
            return {'error': str(e)}
    
    def step6_auto_test(self) -> Dict:
        """步骤 6：自动测试"""
        print("\n" + "=" * 70)
        print("🧪 步骤 6: 自动测试")
        print("=" * 70)
        
        test_file = self.output_dir / "tests" / f"test_{self.spec_file.stem}.py"
        
        if not test_file.exists():
            return {'passed': False, 'error': '测试文件不存在'}
        
        try:
            import subprocess
            
            result = subprocess.run(
                ['python3', '-m', 'pytest', str(test_file), '-v'],
                cwd=str(self.output_dir),
                capture_output=True,
                text=True,
                timeout=60
            )
            
            passed = result.returncode == 0
            
            print(f"   {'✅' if passed else '❌'} 测试结果：{'通过' if passed else '失败'}")
            
            test_result = {
                'passed': passed,
                'output': result.stdout[:500] if result.stdout else ''
            }
            
            self.results['tests'] = test_result
            return test_result
            
        except Exception as e:
            print(f"   ❌ 测试失败：{e}")
            return {'passed': False, 'error': str(e)}
    
    def step7_quality_assessment(self) -> Dict:
        """步骤 7：质量评估"""
        print("\n" + "=" * 70)
        print("⭐ 步骤 7: 质量评估")
        print("=" * 70)
        
        quality_file = self.output_dir / "quality_report.json"
        
        if quality_file.exists():
            with open(quality_file, 'r', encoding='utf-8') as f:
                quality = json.load(f)
            
            print(f"   质量评分：{quality.get('score', 0)}/100")
            print(f"   等级：{quality.get('level', 'Unknown')}")
            
            self.results['quality'] = quality
            return quality
        
        return {'score': 0, 'level': 'Unknown'}
    
    def step8_auto_deploy(self) -> Dict:
        """步骤 8：自动部署"""
        print("\n" + "=" * 70)
        print("🚀 步骤 8: 自动部署")
        print("=" * 70)
        
        try:
            from auto_deployer import AutoDeployer
            
            deployer = AutoDeployer(str(self.output_dir))
            result = deployer.deploy(test=True)  # 测试模式
            
            self.results['deploy'] = result
            return result
            
        except Exception as e:
            print(f"   ⚠️ 部署失败：{e}")
            return {'error': str(e)}
    
    def step9_learning_feedback(self) -> Dict:
        """步骤 9：学习反馈"""
        print("\n" + "=" * 70)
        print("📖 步骤 9: 学习反馈（持续学习）")
        print("=" * 70)
        
        try:
            from continuous_learner import ContinuousLearner
            
            learner = ContinuousLearner()
            
            # 读取代码
            code_file = self.output_dir / "src" / f"{self.spec_file.stem}.py"
            if code_file.exists():
                with open(code_file, 'r', encoding='utf-8') as f:
                    code = f.read()
                
                # 从成功中学习
                quality = self.results.get('quality', {})
                feedback = {
                    'task_id': self.task_id,
                    'quality_score': quality.get('score', 0),
                    'success': quality.get('score', 0) >= 80
                }
                
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
            
            self.results['learning'] = {'success': True}
            return {'success': True}
            
        except Exception as e:
            print(f"   ⚠️ 学习失败：{e}")
            return {'error': str(e)}
    
    def _extract_keywords(self, spec_text: str) -> List[str]:
        """提取关键词"""
        keywords = []
        
        tech_words = {
            'python': ['python', 'py', '脚本'],
            'file': ['文件', 'file', 'batch', '批量'],
            'web': ['web', '网站', 'API', 'Flask'],
            'data': ['数据', 'data', '分析', '统计'],
            'ai': ['AI', '智能', '机器学习'],
            'cli': ['命令行', 'CLI', '工具']
        }
        
        for category, words in tech_words.items():
            if any(word.lower() in spec_text.lower() for word in words):
                keywords.append(category)
        
        return keywords[:5]
    
    def create(self) -> Dict:
        """执行完整创造流程"""
        print("\n" + "=" * 70)
        print("🚀 紫微制造 - 智慧创造系统 v3.0")
        print("=" * 70)
        print(f"任务：{self.task_id}")
        print(f"说明书：{self.spec_file}")
        print(f"输出：{self.output_dir}")
        print("=" * 70)
        
        start_time = datetime.now()
        
        # 步骤 1：知识检索
        knowledge = self.step1_knowledge_retrieval()
        
        # 步骤 2：模板选择
        template = self.step2_template_selection(knowledge)
        
        # 步骤 3：语言选择
        language = self.step3_language_selection()
        
        # 步骤 4：AI 代码生成
        code = self.step4_ai_code_generation(knowledge, template, language)
        
        # 步骤 5：知识图谱
        kg = self.step5_knowledge_graph(knowledge)
        
        # 步骤 6：自动测试
        tests = self.step6_auto_test()
        
        # 步骤 7：质量评估
        quality = self.step7_quality_assessment()
        
        # 步骤 8：自动部署
        deploy = self.step8_auto_deploy()
        
        # 步骤 9：学习反馈
        learning = self.step9_learning_feedback()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # 最终报告
        print("\n" + "=" * 70)
        print("📊 最终报告")
        print("=" * 70)
        print(f"任务 ID: {self.task_id}")
        print(f"总耗时：{duration:.2f}秒")
        print(f"知识检索：{len(knowledge.get('web', []))} 个网络资源")
        print(f"模板：{template}")
        print(f"语言：{language}")
        if isinstance(code, dict):
            print(f"代码生成：{code.get('code', {}).get('iterations', 0) if isinstance(code.get('code'), dict) else 0} 次迭代")
        else:
            print(f"代码生成：完成")
        print(f"知识图谱：{kg.get('nodes', 0)} 节点，{kg.get('edges', 0)} 边")
        print(f"测试：{'✅ 通过' if tests.get('passed') else '❌ 失败'}")
        print(f"质量：{quality.get('score', 0)}/100 ({quality.get('level', 'Unknown')})")
        print(f"部署：{'✅ 完成' if deploy.get('success') else '⚠️ 跳过'}")
        print(f"学习：{'✅ 已记录' if learning.get('success') else '⚠️ 失败'}")
        print("=" * 70)
        
        return {
            "task_id": self.task_id,
            "duration": duration,
            "knowledge": knowledge,
            "template": template,
            "language": language,
            "code": code,
            "knowledge_graph": kg,
            "tests": tests,
            "quality": quality,
            "deploy": deploy,
            "learning": learning
        }


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法：python wisdom_creator.py <spec_file>")
        sys.exit(1)
    
    spec_file = sys.argv[1]
    
    if not Path(spec_file).exists():
        print(f"错误：文件不存在 {spec_file}")
        sys.exit(1)
    
    creator = WisdomCreator(spec_file)
    result = creator.create()
    
    # 保存总报告
    report_file = Path(spec_file).parent / "wisdom_creation_report.json"
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
