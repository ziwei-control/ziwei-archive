#!/usr/bin/env python3
# =============================================================================
# 持续学习系统
# 功能：从每次生成中学习，不断优化
# =============================================================================

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List

Ziwei_DIR = Path("/home/admin/Ziwei")
LEARNING_DIR = Ziwei_DIR / "learning"
LEARNING_DIR.mkdir(parents=True, exist_ok=True)


class ContinuousLearner:
    """持续学习系统"""
    
    def __init__(self):
        self.knowledge_base = LEARNING_DIR / "knowledge_base.json"
        self.success_patterns = LEARNING_DIR / "success_patterns.json"
        self.failure_cases = LEARNING_DIR / "failure_cases.json"
        self.best_practices = LEARNING_DIR / "best_practices.json"
        
    def load_data(self, file: Path) -> Dict:
        """加载学习数据"""
        if file.exists():
            with open(file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"entries": [], "count": 0}
    
    def save_data(self, file: Path, data: Dict):
        """保存学习数据"""
        with open(file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def learn_from_success(self, feedback: Dict, code: str, spec: str):
        """从成功中学习"""
        print("\n📚 从成功中学习...")
        
        patterns = self.load_data(self.success_patterns)
        
        # 提取成功模式
        pattern = {
            "id": len(patterns["entries"]) + 1,
            "timestamp": datetime.now().isoformat(),
            "task_id": feedback.get("task_id", "unknown"),
            "quality_score": feedback.get("quality_score", 0),
            "spec_keywords": self.extract_keywords(spec),
            "code_features": self.extract_code_features(code),
            "success_factors": self.analyze_success_factors(feedback, code)
        }
        
        patterns["entries"].append(pattern)
        patterns["count"] += 1
        
        self.save_data(self.success_patterns, patterns)
        print(f"   ✅ 已记录成功模式 #{pattern['id']}")
        
        # 更新最佳实践
        self.update_best_practices(pattern)
    
    def learn_from_failure(self, feedback: Dict, code: str, spec: str, errors: List[str]):
        """从失败中学习"""
        print("\n📚 从失败中学习...")
        
        failures = self.load_data(self.failure_cases)
        
        # 记录失败案例
        case = {
            "id": len(failures["entries"]) + 1,
            "timestamp": datetime.now().isoformat(),
            "task_id": feedback.get("task_id", "unknown"),
            "quality_score": feedback.get("quality_score", 0),
            "errors": errors,
            "root_cause": self.analyze_root_cause(errors),
            "avoid_patterns": self.extract_avoid_patterns(code, errors),
            "lessons": self.generate_lessons(errors)
        }
        
        failures["entries"].append(case)
        failures["count"] += 1
        
        self.save_data(self.failure_cases, failures)
        print(f"   ✅ 已记录失败案例 #{case['id']}")
        
        # 更新避免列表
        self.update_avoid_list(case)
    
    def extract_keywords(self, spec: str) -> List[str]:
        """提取说明书关键词"""
        keywords = []
        
        # 技术关键词
        tech_words = ["python", "API", "web", "database", "file", "CLI", "bot"]
        for word in tech_words:
            if word.lower() in spec.lower():
                keywords.append(word)
        
        return keywords
    
    def extract_code_features(self, code: str) -> Dict:
        """提取代码特征"""
        features = {
            "lines": len(code.split('\n')),
            "functions": code.count('def '),
            "classes": code.count('class '),
            "imports": code.count('import '),
            "has_docstring": '"""' in code or "'''" in code,
            "has_error_handling": 'try:' in code and 'except:' in code,
            "has_type_hints": '->' in code or ': str' in code or ': int' in code
        }
        return features
    
    def analyze_success_factors(self, feedback: Dict, code: str) -> List[str]:
        """分析成功因素"""
        factors = []
        
        if feedback.get("quality_score", 0) >= 90:
            factors.append("高质量代码")
        
        features = self.extract_code_features(code)
        if features["has_docstring"]:
            factors.append("完整文档")
        if features["has_error_handling"]:
            factors.append("错误处理完善")
        if features["has_type_hints"]:
            factors.append("类型提示")
        
        return factors
    
    def analyze_root_cause(self, errors: List[str]) -> str:
        """分析根本原因"""
        if not errors:
            return "未知"
        
        error_categories = {
            "syntax": ["SyntaxError", "invalid syntax"],
            "import": ["ImportError", "ModuleNotFoundError"],
            "runtime": ["NameError", "TypeError", "AttributeError"],
            "logic": ["AssertionError", "incorrect", "wrong"]
        }
        
        for category, keywords in error_categories.items():
            if any(kw.lower() in str(errors).lower() for kw in keywords):
                return category
        
        return "other"
    
    def extract_avoid_patterns(self, code: str, errors: List[str]) -> List[str]:
        """提取避免模式"""
        patterns = []
        
        if "eval(" in code:
            patterns.append("避免使用 eval()")
        if "exec(" in code:
            patterns.append("避免使用 exec()")
        if "import *" in code:
            patterns.append("避免使用 import *")
        
        return patterns
    
    def generate_lessons(self, errors: List[str]) -> List[str]:
        """生成经验教训"""
        lessons = []
        
        for error in errors:
            if "eval" in error.lower():
                lessons.append("不要使用 eval()，存在安全风险")
            if "import" in error.lower():
                lessons.append("确保所有依赖都已安装")
            if "file" in error.lower() or "path" in error.lower():
                lessons.append("使用 pathlib 处理文件路径")
        
        return lessons
    
    def update_best_practices(self, pattern: Dict):
        """更新最佳实践"""
        practices = self.load_data(self.best_practices)
        
        # 提取最佳实践
        for factor in pattern.get("success_factors", []):
            if factor not in [p.get("practice") for p in practices["entries"]]:
                practices["entries"].append({
                    "practice": factor,
                    "count": 1,
                    "first_seen": pattern["timestamp"]
                })
            else:
                # 增加计数
                for p in practices["entries"]:
                    if p["practice"] == factor:
                        p["count"] += 1
        
        self.save_data(self.best_practices, practices)
    
    def update_avoid_list(self, case: Dict):
        """更新避免列表"""
        avoid_file = LEARNING_DIR / "avoid_list.json"
        avoid = self.load_data(avoid_file)
        
        for pattern in case.get("avoid_patterns", []):
            if pattern not in [a.get("pattern") for a in avoid["entries"]]:
                avoid["entries"].append({
                    "pattern": pattern,
                    "reason": case.get("root_cause", "unknown"),
                    "first_seen": case["timestamp"]
                })
        
        self.save_data(avoid_file, avoid)
    
    def get_recommendations(self, spec: str) -> List[str]:
        """基于历史学习给出推荐"""
        recommendations = []
        
        # 从成功案例中学习
        patterns = self.load_data(self.success_patterns)
        keywords = self.extract_keywords(spec)
        
        for pattern in patterns.get("entries", [])[-10:]:  # 最近 10 个
            if any(kw in pattern.get("spec_keywords", []) for kw in keywords):
                recommendations.extend(pattern.get("success_factors", []))
        
        # 从最佳实践中学习
        practices = self.load_data(self.best_practices)
        top_practices = sorted(
            practices.get("entries", []),
            key=lambda x: x.get("count", 0),
            reverse=True
        )[:5]
        
        for practice in top_practices:
            recommendations.append(practice.get("practice", ""))
        
        return list(set(recommendations))  # 去重


def main():
    """主函数"""
    learner = ContinuousLearner()
    
    # 示例：从成功中学习
    feedback = {
        "task_id": "TASK-001",
        "quality_score": 90,
        "success": True
    }
    
    code = '''
def hello():
    """Say hello"""
    print("Hello, World!")
'''
    
    spec = "创建一个 Hello World 程序"
    
    learner.learn_from_success(feedback, code, spec)
    
    # 获取推荐
    recommendations = learner.get_recommendations(spec)
    print(f"\n💡 推荐实践：{recommendations}")


if __name__ == '__main__':
    main()
