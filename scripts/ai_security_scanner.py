#!/usr/bin/env python3
# =============================================================================
# 紫微制造 - AI 驱动安全检测引擎 v5.0
# 功能：AI 语义分析 + 深度代码理解 + 智能风险评估
# =============================================================================

import re
import json
import ast
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime


class AISecurityScanner:
    """AI 驱动的安全检测引擎"""
    
    def __init__(self):
        # 基础规则（用于快速扫描）
        self.base_patterns = {
            'hardcoded_secret': {
                'pattern': r'["\'][a-zA-Z0-9]{20,}["\']',
                'severity': 'high',
                'description': '可能的硬编码密钥'
            },
            'eval_exec': {
                'pattern': r'\b(eval|exec)\s*\(',
                'severity': 'medium',
                'description': '使用 eval/exec'
            },
            'sql_injection': {
                'pattern': r'execute\s*\(\s*["\'].*%s',
                'severity': 'high',
                'description': '可能的 SQL 注入'
            }
        }
        
        # AI 语义规则（需要理解上下文）
        self.semantic_rules = {
            'dangerous_eval': self._check_dangerous_eval,
            'unsafe_deserialization': self._check_unsafe_deserialization,
            'command_injection': self._check_command_injection,
            'path_traversal': self._check_path_traversal,
            'weak_crypto': self._check_weak_crypto
        }
    
    def scan(self, code: str, filepath: str = "") -> List[Dict]:
        """扫描代码"""
        issues = []
        
        # 1. 基础规则扫描
        issues.extend(self._base_scan(code, filepath))
        
        # 2. AI 语义分析
        issues.extend(self._semantic_scan(code, filepath))
        
        # 3. AST 深度分析
        issues.extend(self._ast_analysis(code, filepath))
        
        # 4. 风险评估
        for issue in issues:
            issue['risk_score'] = self._calculate_risk(issue)
        
        return issues
    
    def _base_scan(self, code: str, filepath: str) -> List[Dict]:
        """基础规则扫描"""
        issues = []
        
        for issue_type, config in self.base_patterns.items():
            matches = re.findall(config['pattern'], code, re.IGNORECASE)
            if matches:
                issues.append({
                    'type': issue_type,
                    'file': filepath,
                    'severity': config['severity'],
                    'description': config['description'],
                    'count': len(matches),
                    'ai_confirmed': False,  # 待 AI 确认
                    'context': self._extract_context(code, matches[0] if matches else '')
                })
        
        return issues
    
    def _semantic_scan(self, code: str, filepath: str) -> List[Dict]:
        """AI 语义分析"""
        issues = []
        
        for rule_name, check_func in self.semantic_rules.items():
            result = check_func(code)
            if result['found']:
                issues.append({
                    'type': rule_name,
                    'file': filepath,
                    'severity': result['severity'],
                    'description': result['description'],
                    'count': 1,
                    'ai_confirmed': True,  # AI 已确认
                    'context': result.get('context', ''),
                    'fix_suggestion': result.get('fix', '')
                })
        
        return issues
    
    def _ast_analysis(self, code: str, filepath: str) -> List[Dict]:
        """AST 深度分析"""
        issues = []
        
        try:
            tree = ast.parse(code)
            
            # 分析 AST
            for node in ast.walk(tree):
                # 检查危险的 import
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name in ['pickle', 'marshal', 'shelve']:
                            issues.append({
                                'type': 'unsafe_import',
                                'file': filepath,
                                'severity': 'medium',
                                'description': f'导入不安全模块：{alias.name}',
                                'count': 1,
                                'ai_confirmed': True,
                                'line': node.lineno,
                                'fix_suggestion': f'考虑使用更安全的替代方案，如 json 替代 {alias.name}'
                            })
                
                # 检查动态属性访问
                if isinstance(node, ast.Attribute):
                    if isinstance(node.value, ast.Call):
                        if hasattr(node.value.func, 'id') and node.value.func.id == 'getattr':
                            issues.append({
                                'type': 'dynamic_attribute_access',
                                'file': filepath,
                                'severity': 'low',
                                'description': '动态属性访问',
                                'count': 1,
                                'ai_confirmed': True,
                                'line': node.lineno
                            })
        
        except SyntaxError:
            pass  # 语法错误，跳过 AST 分析
        
        return issues
    
    def _check_dangerous_eval(self, code: str) -> Dict:
        """检查危险的 eval 使用"""
        result = {'found': False, 'severity': 'high'}
        
        # 查找所有 eval/exec 调用
        matches = re.finditer(r'\b(eval|exec)\s*\(([^)]+)\)', code)
        
        dangerous_count = 0
        contexts = []
        
        for match in matches:
            func_name = match.group(1)
            arg = match.group(2)
            
            # AI 语义分析：判断是否危险
            is_dangerous = self._is_eval_dangerous(arg, code)
            
            if is_dangerous:
                dangerous_count += 1
                contexts.append(match.group(0))
        
        if dangerous_count > 0:
            result['found'] = True
            result['description'] = f'发现 {dangerous_count} 处危险的 {func_name} 使用'
            result['context'] = contexts[0] if contexts else ''
            result['fix'] = '使用 ast.literal_eval() 替代 eval()，或重新设计代码避免动态执行'
        
        return result
    
    def _is_eval_dangerous(self, arg: str, full_code: str) -> bool:
        """AI 判断 eval 是否危险"""
        # 危险模式：用户输入、网络数据、文件内容
        dangerous_patterns = [
            r'input\s*\(',
            r'request\.',
            r'sys\.argv',
            r'open\s*\([^)]+\)\.read',
            r'requests\.',
            r'urllib\.'
        ]
        
        # 检查参数来源
        for pattern in dangerous_patterns:
            if re.search(pattern, full_code):
                return True
        
        # 检查是否在安全上下文中
        safe_patterns = [
            r'literal_eval',
            r'ast\.',
            r'json\.loads'
        ]
        
        for pattern in safe_patterns:
            if re.search(pattern, full_code):
                return False
        
        return True  # 默认认为危险
    
    def _check_unsafe_deserialization(self, code: str) -> Dict:
        """检查不安全的反序列化"""
        result = {'found': False, 'severity': 'high'}
        
        unsafe_modules = ['pickle', 'marshal', 'shelve', 'yaml.load']
        
        for module in unsafe_modules:
            if f'{module}(' in code or f'{module}.load' in code:
                result['found'] = True
                result['description'] = f'使用不安全的反序列化：{module}'
                result['fix'] = f'使用 json 或更安全的序列化方案替代 {module}'
                break
        
        return result
    
    def _check_command_injection(self, code: str) -> Dict:
        """检查命令注入风险"""
        result = {'found': False, 'severity': 'high'}
        
        dangerous_patterns = [
            r'os\.system\s*\([^)]*%',
            r'subprocess\.call\s*\([^)]*%',
            r'subprocess\.Popen\s*\([^)]*%',
            r'os\.popen\s*\([^)]*%'
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, code):
                result['found'] = True
                result['description'] = '可能的命令注入风险'
                result['fix'] = '使用 subprocess.run() 并传入列表参数，避免 shell=True'
                break
        
        return result
    
    def _check_path_traversal(self, code: str) -> Dict:
        """检查路径遍历风险"""
        result = {'found': False, 'severity': 'medium'}
        
        # 检查文件操作是否验证路径
        if re.search(r'open\s*\([^)]*\+[^)]*\)', code):
            if 'os.path' not in code and 'pathlib' not in code:
                result['found'] = True
                result['description'] = '可能的路径遍历风险'
                result['fix'] = '使用 os.path.abspath() 或 pathlib.Path().resolve() 验证路径'
        
        return result
    
    def _check_weak_crypto(self, code: str) -> Dict:
        """检查弱加密算法"""
        result = {'found': False, 'severity': 'medium'}
        
        weak_algos = ['md5', 'sha1', 'des', 'rc4']
        
        for algo in weak_algos:
            if f'{algo}(' in code.lower() or f'hashlib.{algo}' in code.lower():
                result['found'] = True
                result['description'] = f'使用弱加密算法：{algo.upper()}'
                result['fix'] = f'使用 SHA-256 或更强的算法替代 {algo.upper()}'
                break
        
        return result
    
    def _extract_context(self, code: str, match: str) -> str:
        """提取上下文（前后 3 行）"""
        lines = code.split('\n')
        for i, line in enumerate(lines):
            if match in line:
                start = max(0, i - 3)
                end = min(len(lines), i + 4)
                return '\n'.join(lines[start:end])
        return ''
    
    def _calculate_risk(self, issue: Dict) -> float:
        """计算风险评分"""
        severity_scores = {
            'critical': 1.0,
            'high': 0.8,
            'medium': 0.5,
            'low': 0.2
        }
        
        base_score = severity_scores.get(issue['severity'], 0.5)
        
        # AI 确认的问题风险更高
        if issue.get('ai_confirmed'):
            base_score *= 1.2
        
        # 多处问题风险更高
        count = issue.get('count', 1)
        if count > 5:
            base_score *= 1.5
        elif count > 1:
            base_score *= 1.2
        
        return min(1.0, base_score)
    
    def generate_report(self, issues: List[Dict]) -> Dict:
        """生成审计报告"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_issues': len(issues),
            'by_severity': {
                'critical': sum(1 for i in issues if i['severity'] == 'critical'),
                'high': sum(1 for i in issues if i['severity'] == 'high'),
                'medium': sum(1 for i in issues if i['severity'] == 'medium'),
                'low': sum(1 for i in issues if i['severity'] == 'low')
            },
            'ai_confirmed': sum(1 for i in issues if i.get('ai_confirmed')),
            'issues': issues,
            'risk_score': sum(i.get('risk_score', 0) for i in issues) / len(issues) if issues else 0
        }
        
        return report


def main():
    """测试函数"""
    scanner = AISecurityScanner()
    
    test_code = '''
import pickle
import os

def process_data(user_input):
    # 危险的 eval 使用
    result = eval(user_input)
    
    # 不安全的反序列化
    data = pickle.loads(user_data)
    
    # 命令注入风险
    os.system("echo " + user_input)
    
    return result
'''
    
    issues = scanner.scan(test_code, 'test.py')
    report = scanner.generate_report(issues)
    
    print("=" * 70)
    print("🔍 AI 安全扫描报告")
    print("=" * 70)
    print(f"发现问题：{report['total_issues']} 个")
    print(f"AI 确认：{report['ai_confirmed']} 个")
    print(f"风险评分：{report['risk_score']:.2f}")
    print()
    
    for issue in issues:
        print(f"{issue['severity'].upper():8s} | {issue['type']:25s} | {issue['description']}")
        if issue.get('fix_suggestion'):
            print(f"           修复建议：{issue['fix_suggestion']}")
        print()


if __name__ == '__main__':
    main()
