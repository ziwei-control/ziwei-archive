#!/usr/bin/env python3
# =============================================================================
# 紫微制造 - 深度代码理解引擎 v5.0
# 功能：理解代码意图 + 复杂度分析 + 风险推理
# =============================================================================

import ast
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class DeepCodeUnderstanding:
    """深度代码理解引擎"""
    
    def __init__(self):
        self.intent_patterns = {
            'data_processing': ['pandas', 'numpy', 'csv', 'json', 'process', 'transform'],
            'web_service': ['flask', 'django', 'fastapi', 'route', 'request', 'response'],
            'automation': ['schedule', 'cron', 'automation', 'batch', 'loop'],
            'file_operation': ['open', 'read', 'write', 'pathlib', 'os.path'],
            'network': ['requests', 'urllib', 'socket', 'http', 'api'],
            'security': ['encrypt', 'decrypt', 'hash', 'auth', 'token']
        }
    
    def understand(self, code: str) -> Dict:
        """深度理解代码"""
        return {
            'intent': self._identify_intent(code),
            'complexity': self._analyze_complexity(code),
            'quality': self._assess_quality(code),
            'risks': self._identify_risks(code),
            'suggestions': self._generate_suggestions(code)
        }
    
    def _identify_intent(self, code: str) -> Dict:
        """识别代码意图"""
        scores = {}
        
        for intent, keywords in self.intent_patterns.items():
            score = sum(1 for kw in keywords if kw.lower() in code.lower())
            scores[intent] = score
        
        best_match = max(scores.items(), key=lambda x: x[1]) if any(scores.values()) else ('unknown', 0)
        
        return {
            'primary': best_match[0],
            'confidence': min(best_match[1] / len(self.intent_patterns[best_match[0]]), 1.0),
            'secondary': [k for k, v in scores.items() if v > 0 and k != best_match[0]]
        }
    
    def _analyze_complexity(self, code: str) -> Dict:
        """分析复杂度"""
        try:
            tree = ast.parse(code)
            
            # 计算各种复杂度指标
            lines = len(code.split('\n'))
            functions = sum(1 for node in ast.walk(tree) if isinstance(node, ast.FunctionDef))
            classes = sum(1 for node in ast.walk(tree) if isinstance(node, ast.ClassDef))
            loops = sum(1 for node in ast.walk(tree) if isinstance(node, (ast.For, ast.While)))
            conditions = sum(1 for node in ast.walk(tree) if isinstance(node, ast.If))
            
            # 计算圈复杂度
            cyclomatic = 1 + loops + conditions
            
            # 计算嵌套深度
            max_depth = self._calculate_max_depth(tree)
            
            return {
                'lines': lines,
                'functions': functions,
                'classes': classes,
                'loops': loops,
                'conditions': conditions,
                'cyclomatic_complexity': cyclomatic,
                'max_nesting_depth': max_depth,
                'overall_score': self._calculate_complexity_score(cyclomatic, max_depth, lines)
            }
        except:
            return {'overall_score': 5, 'reason': '无法解析'}
    
    def _calculate_max_depth(self, tree: ast.AST, current_depth: int = 0) -> int:
        """计算最大嵌套深度"""
        max_depth = current_depth
        
        for child in ast.iter_child_nodes(tree):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                child_depth = self._calculate_max_depth(child, current_depth + 1)
                max_depth = max(max_depth, child_depth)
            else:
                child_depth = self._calculate_max_depth(child, current_depth)
                max_depth = max(max_depth, child_depth)
        
        return max_depth
    
    def _calculate_complexity_score(self, cyclomatic: int, max_depth: int, lines: int) -> int:
        """计算复杂度评分 (1-10)"""
        score = 10
        
        if cyclomatic > 20:
            score -= 3
        elif cyclomatic > 10:
            score -= 2
        elif cyclomatic > 5:
            score -= 1
        
        if max_depth > 5:
            score -= 2
        elif max_depth > 3:
            score -= 1
        
        if lines > 500:
            score -= 2
        elif lines > 200:
            score -= 1
        
        return max(1, score)
    
    def _assess_quality(self, code: str) -> Dict:
        """评估代码质量"""
        quality_aspects = {
            'documentation': self._check_documentation(code),
            'naming': self._check_naming(code),
            'structure': self._check_structure(code),
            'best_practices': self._check_best_practices(code)
        }
        
        overall = sum(aspects['score'] for aspects in quality_aspects.values()) / len(quality_aspects)
        
        return {
            'aspects': quality_aspects,
            'overall_score': overall,
            'grade': self._score_to_grade(overall)
        }
    
    def _check_documentation(self, code: str) -> Dict:
        """检查文档"""
        has_module_doc = '"""' in code or "'''" in code
        has_function_docs = code.count('"""') >= 4 or code.count("'''") >= 4
        
        score = 0
        if has_module_doc:
            score += 5
        if has_function_docs:
            score += 5
        
        return {
            'score': min(10, score),
            'has_module_doc': has_module_doc,
            'has_function_docs': has_function_docs
        }
    
    def _check_naming(self, code: str) -> Dict:
        """检查命名规范"""
        # 检查变量命名
        snake_case = len(re.findall(r'[a-z_][a-z0-9_]*\s*=', code))
        camel_case = len(re.findall(r'[a-z][A-Z][a-zA-Z]*\s*=', code))
        
        score = 10
        if camel_case > snake_case:
            score -= 3  # Python 推荐 snake_case
        
        return {
            'score': score,
            'snake_case_count': snake_case,
            'camel_case_count': camel_case
        }
    
    def _check_structure(self, code: str) -> Dict:
        """检查代码结构"""
        try:
            tree = ast.parse(code)
            
            # 检查函数长度
            long_functions = 0
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_lines = node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 20
                    if func_lines > 50:
                        long_functions += 1
            
            score = 10 - min(long_functions * 2, 6)
            
            return {
                'score': score,
                'long_functions': long_functions
            }
        except:
            return {'score': 5, 'long_functions': 0}
    
    def _check_best_practices(self, code: str) -> Dict:
        """检查最佳实践"""
        score = 10
        
        # 检查是否有 try-except
        if 'try:' not in code:
            score -= 2
        
        # 检查是否有类型提示
        if '->' not in code and ': str' not in code and ': int' not in code:
            score -= 1
        
        # 检查是否有 context manager
        if 'with ' not in code and 'open(' in code:
            score -= 2
        
        return {'score': max(1, score)}
    
    def _score_to_grade(self, score: float) -> str:
        """评分转等级"""
        if score >= 9:
            return 'A+'
        elif score >= 8:
            return 'A'
        elif score >= 7:
            return 'B'
        elif score >= 6:
            return 'C'
        else:
            return 'D'
    
    def _identify_risks(self, code: str) -> List[Dict]:
        """识别风险"""
        risks = []
        
        # 检查全局变量
        if re.search(r'^[A-Z_]+\s*=', code, re.MULTILINE):
            risks.append({
                'type': 'global_variable',
                'severity': 'low',
                'description': '使用全局变量'
            })
        
        # 检查魔法数字
        magic_numbers = re.findall(r'(?<!["\'])(\b\d{4,}\b)(?!["\'])', code)
        if len(magic_numbers) > 3:
            risks.append({
                'type': 'magic_numbers',
                'severity': 'low',
                'description': '过多魔法数字，建议使用常量'
            })
        
        # 检查重复代码
        lines = code.split('\n')
        line_counts = {}
        for line in lines:
            line = line.strip()
            if line and len(line) > 20:
                line_counts[line] = line_counts.get(line, 0) + 1
        
        duplicates = sum(1 for count in line_counts.values() if count > 2)
        if duplicates > 3:
            risks.append({
                'type': 'duplicate_code',
                'severity': 'medium',
                'description': '发现重复代码，建议重构'
            })
        
        return risks
    
    def _generate_suggestions(self, code: str) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        # 基于复杂度
        complexity = self._analyze_complexity(code)
        if complexity.get('overall_score', 10) < 6:
            suggestions.append('代码复杂度过高，建议拆分函数')
        
        # 基于质量
        quality = self._assess_quality(code)
        if quality['aspects']['documentation']['score'] < 5:
            suggestions.append('添加更多文档字符串')
        
        if quality['aspects']['best_practices']['score'] < 8:
            suggestions.append('使用更多最佳实践（context manager、类型提示等）')
        
        # 基于风险
        risks = self._identify_risks(code)
        for risk in risks:
            if risk['severity'] == 'medium':
                suggestions.append(f"修复问题：{risk['description']}")
        
        return suggestions


def main():
    """测试函数"""
    analyzer = DeepCodeUnderstanding()
    
    test_code = '''
def process_data(data):
    result = []
    for item in data:
        if item > 100:
            result.append(item * 2)
        else:
            result.append(item)
    return result
'''
    
    understanding = analyzer.understand(test_code)
    
    print("=" * 70)
    print("🧠 深度代码理解报告")
    print("=" * 70)
    print(f"主要意图：{understanding['intent']['primary']} (置信度：{understanding['intent']['confidence']:.0%})")
    print(f"复杂度评分：{understanding['complexity'].get('overall_score', 'N/A')}/10")
    print(f"质量等级：{understanding['quality']['grade']} ({understanding['quality']['overall_score']:.1f}/10)")
    print()
    
    if understanding['risks']:
        print("⚠️  发现风险:")
        for risk in understanding['risks']:
            print(f"  - {risk['severity'].upper()}: {risk['description']}")
    
    if understanding['suggestions']:
        print("\n💡 改进建议:")
        for sug in understanding['suggestions']:
            print(f"  - {sug}")


if __name__ == '__main__':
    main()
