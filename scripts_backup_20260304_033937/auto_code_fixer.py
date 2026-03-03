#!/usr/bin/env python3
# =============================================================================
# 自动代码修复引擎
# 功能：检测错误 + 自动修复 + 迭代优化
# =============================================================================

import ast
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class AutoCodeFixer:
    """自动代码修复引擎"""
    
    def __init__(self):
        self.fixes_applied = []
        self.max_iterations = 3
    
    def analyze_code(self, code: str) -> Dict:
        """分析代码问题"""
        issues = []
        
        # 1. 语法检查
        try:
            ast.parse(code)
        except SyntaxError as e:
            issues.append({
                'type': 'syntax',
                'severity': 'critical',
                'message': f'SyntaxError: {e.msg}',
                'line': e.lineno,
                'offset': e.offset
            })
        
        # 2. 安全检查
        if 'eval(' in code:
            issues.append({
                'type': 'security',
                'severity': 'high',
                'message': '使用 eval() 存在安全风险',
                'suggestion': '使用 ast.literal_eval() 替代'
            })
        
        if 'exec(' in code:
            issues.append({
                'type': 'security',
                'severity': 'high',
                'message': '使用 exec() 存在安全风险',
                'suggestion': '避免使用 exec()'
            })
        
        # 3. 代码规范检查
        if 'import *' in code:
            issues.append({
                'type': 'style',
                'severity': 'low',
                'message': '使用 import * 不符合规范',
                'suggestion': '明确导入需要的模块'
            })
        
        # 4. 常见错误模式
        if 'open(' in code and 'with ' not in code:
            issues.append({
                'type': 'best_practice',
                'severity': 'medium',
                'message': '文件未使用 with 语句',
                'suggestion': '使用 with open() 确保文件正确关闭'
            })
        
        # 5. 未使用的导入
        imports = re.findall(r'^import (\w+)|^from (\w+) import', code, re.MULTILINE)
        for imp in imports:
            module = imp[0] or imp[1]
            if module and code.count(module) == 1:
                issues.append({
                    'type': 'optimization',
                    'severity': 'low',
                    'message': f'可能未使用的导入：{module}',
                    'suggestion': '移除未使用的导入'
                })
        
        return {
            'issues': issues,
            'issue_count': len(issues),
            'critical': sum(1 for i in issues if i['severity'] == 'critical'),
            'high': sum(1 for i in issues if i['severity'] == 'high'),
            'medium': sum(1 for i in issues if i['severity'] == 'medium'),
            'low': sum(1 for i in issues if i['severity'] == 'low')
        }
    
    def fix_syntax_error(self, code: str, error: Dict) -> str:
        """修复语法错误"""
        lines = code.split('\n')
        
        # 常见语法错误修复
        if 'SyntaxError' in error.get('message', ''):
            # 缺少冒号
            if 'expected \':\'' in error.get('message', ''):
                line_num = error.get('line', 1) - 1
                if 0 <= line_num < len(lines):
                    lines[line_num] = lines[line_num].rstrip() + ':'
            
            # 括号不匹配
            if 'EOF while scanning triple-quoted string' in error.get('message', ''):
                # 添加缺失的引号
                if code.count('"""') % 2 != 0:
                    code += '\n"""'
                elif code.count("'''") % 2 != 0:
                    code += "\n'''"
        
        return '\n'.join(lines)
    
    def fix_security_issues(self, code: str, issues: List[Dict]) -> str:
        """修复安全问题"""
        for issue in issues:
            if issue['type'] == 'security':
                if 'eval()' in issue.get('message', ''):
                    # 替换 eval 为 ast.literal_eval
                    code = code.replace('eval(', 'ast.literal_eval(')
                    if 'import ast' not in code:
                        code = 'import ast\n' + code
                
                if 'exec()' in issue.get('message', ''):
                    # 标记 exec 为注释
                    code = code.replace('exec(', '# exec( # 已禁用\n')
        
        return code
    
    def fix_style_issues(self, code: str, issues: List[Dict]) -> str:
        """修复代码风格问题"""
        for issue in issues:
            if issue['type'] == 'style':
                if 'import *' in issue.get('message', ''):
                    # 这个需要手动修复，给出提示
                    pass
                
                if 'with ' not in code and 'open(' in code:
                    # 简单的 open 替换为 with open
                    pattern = r'(\w+) = open\(([^)]+)\)'
                    replacement = r'with open(\2) as \1:'
                    code = re.sub(pattern, replacement, code)
        
        return code
    
    def fix_all(self, code: str) -> Tuple[str, Dict]:
        """执行所有修复"""
        print("\n🔧 自动代码修复...")
        
        original_code = code
        iteration = 0
        
        while iteration < self.max_iterations:
            iteration += 1
            print(f"\n   第 {iteration} 次迭代...")
            
            # 分析
            analysis = self.analyze_code(code)
            
            print(f"   发现问题：{analysis['issue_count']} 个")
            print(f"   - 严重：{analysis['critical']}")
            print(f"   - 高：{analysis['high']}")
            print(f"   - 中：{analysis['medium']}")
            print(f"   - 低：{analysis['low']}")
            
            # 如果没有严重问题，停止
            if analysis['critical'] == 0 and analysis['high'] == 0:
                print("   ✅ 代码质量可接受")
                break
            
            # 修复
            fixed = False
            
            # 修复语法错误
            for issue in analysis['issues']:
                if issue['type'] == 'syntax':
                    new_code = self.fix_syntax_error(code, issue)
                    if new_code != code:
                        code = new_code
                        fixed = True
                        self.fixes_applied.append({
                            'iteration': iteration,
                            'type': 'syntax',
                            'issue': issue['message']
                        })
            
            # 修复安全问题
            security_issues = [i for i in analysis['issues'] if i['type'] == 'security']
            if security_issues:
                new_code = self.fix_security_issues(code, security_issues)
                if new_code != code:
                    code = new_code
                    fixed = True
                    self.fixes_applied.append({
                        'iteration': iteration,
                        'type': 'security',
                        'count': len(security_issues)
                    })
            
            # 修复风格问题
            style_issues = [i for i in analysis['issues'] if i['type'] == 'style']
            if style_issues:
                new_code = self.fix_style_issues(code, style_issues)
                if new_code != code:
                    code = new_code
                    fixed = True
                    self.fixes_applied.append({
                        'iteration': iteration,
                        'type': 'style',
                        'count': len(style_issues)
                    })
            
            # 如果没有修复任何东西，停止
            if not fixed:
                print("   ⚠️ 无法自动修复，需要人工干预")
                break
        
        # 最终分析
        final_analysis = self.analyze_code(code)
        
        print(f"\n📊 修复统计:")
        print(f"   迭代次数：{iteration}")
        print(f"   应用修复：{len(self.fixes_applied)} 次")
        print(f"   剩余问题：{final_analysis['issue_count']} 个")
        
        return code, final_analysis


def main():
    """主函数"""
    fixer = AutoCodeFixer()
    
    # 测试代码
    test_code = '''
def test():
    result = eval("1+1")
    f = open("file.txt")
    data = f.read()
'''
    
    print("原始代码:")
    print(test_code)
    
    fixed_code, analysis = fixer.fix_all(test_code)
    
    print("\n修复后代码:")
    print(fixed_code)
    
    print("\n修复记录:")
    for fix in fixer.fixes_applied:
        print(f"  - 迭代{fix['iteration']}: {fix['type']} - {fix.get('issue', fix.get('count'))}")


if __name__ == '__main__':
    main()
