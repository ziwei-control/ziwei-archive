#!/usr/bin/env python3
# =============================================================================
# 紫微制造 - 智能审计系统 v5.0
# 功能：AI 驱动 + 深度理解 + 自动修复 + 持续学习
# =============================================================================

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List

# 导入升级模块
from ai_security_scanner import AISecurityScanner
from deep_code_understanding import DeepCodeUnderstanding


class IntelligentAuditSystem:
    """智能审计系统 v5.0"""
    
    def __init__(self):
        self.security_scanner = AISecurityScanner()
        self.code_understanding = DeepCodeUnderstanding()
        self.learning_data = self._load_learning_data()
        
    def _load_learning_data(self) -> Dict:
        """加载学习数据"""
        learning_file = Path('/home/admin/Ziwei/data/audit_learning.json')
        if learning_file.exists():
            with open(learning_file, 'r') as f:
                return json.load(f)
        return {'false_positives': [], 'false_negatives': [], 'experiences': []}
    
    def audit_project(self, project_path: str) -> Dict:
        """审计项目"""
        print("\n" + "=" * 70)
        print(f"🔍 智能审计系统 v5.0 - {project_path}")
        print("=" * 70)
        
        audit_result = {
            'timestamp': datetime.now().isoformat(),
            'project': project_path,
            'files_audited': 0,
            'security': {'issues': [], 'risk_score': 0},
            'quality': {'score': 0, 'grade': 'N/A'},
            'understanding': {},
            'recommendations': [],
            'auto_fixes': []
        }
        
        # 扫描所有 Python 文件
        py_files = list(Path(project_path).rglob('*.py'))
        print(f"\n📁 发现 {len(py_files)} 个 Python 文件")
        
        all_issues = []
        all_understandings = []
        
        for py_file in py_files:
            if '.git' in str(py_file) or '__pycache__' in str(py_file):
                continue
            
            print(f"\n审计：{py_file.name}")
            
            # 读取代码
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    code = f.read()
            except:
                continue
            
            audit_result['files_audited'] += 1
            
            # 1. AI 安全扫描
            security_issues = self.security_scanner.scan(code, str(py_file))
            all_issues.extend(security_issues)
            
            # 2. 深度代码理解
            understanding = self.code_understanding.understand(code)
            all_understandings.append(understanding)
            
            # 3. 生成自动修复建议
            auto_fixes = self._generate_auto_fixes(security_issues)
            audit_result['auto_fixes'].extend(auto_fixes)
        
        # 汇总结果
        audit_result['security']['issues'] = all_issues
        audit_result['security']['risk_score'] = sum(i.get('risk_score', 0) for i in all_issues) / len(all_issues) if all_issues else 0
        
        # 质量评估
        if all_understandings:
            avg_quality = sum(u['quality']['overall_score'] for u in all_understandings) / len(all_understandings)
            audit_result['quality']['score'] = avg_quality
            audit_result['quality']['grade'] = self._score_to_grade(avg_quality)
        
        # 理解汇总
        intents = [u['intent']['primary'] for u in all_understandings if u['intent']['primary'] != 'unknown']
        if intents:
            audit_result['understanding']['primary_intent'] = max(set(intents), key=intents.count)
        
        # 生成建议
        audit_result['recommendations'] = self._generate_recommendations(audit_result)
        
        # 保存学习数据
        self._save_learning_data(audit_result)
        
        # 打印报告
        self._print_report(audit_result)
        
        return audit_result
    
    def _generate_auto_fixes(self, issues: List[Dict]) -> List[Dict]:
        """生成自动修复"""
        auto_fixes = []
        
        for issue in issues:
            if issue.get('fix_suggestion'):
                auto_fixes.append({
                    'file': issue['file'],
                    'issue': issue['type'],
                    'fix': issue['fix_suggestion'],
                    'auto_fixable': self._is_auto_fixable(issue)
                })
        
        return auto_fixes
    
    def _is_auto_fixable(self, issue: Dict) -> bool:
        """判断是否可以自动修复"""
        auto_fixable_types = [
            'hardcoded_secret',
            'weak_crypto',
            'unsafe_import'
        ]
        
        return issue['type'] in auto_fixable_types
    
    def _generate_recommendations(self, audit_result: Dict) -> List[str]:
        """生成建议"""
        recommendations = []
        
        # 基于风险评分
        if audit_result['security']['risk_score'] > 0.7:
            recommendations.append('🔴 高风险：立即修复安全问题')
        elif audit_result['security']['risk_score'] > 0.4:
            recommendations.append('🟡 中风险：尽快修复安全问题')
        
        # 基于质量
        if audit_result['quality']['score'] < 6:
            recommendations.append('💡 代码质量较低，建议重构')
        
        # 基于理解
        if audit_result['understanding'].get('primary_intent') == 'unknown':
            recommendations.append('❓ 代码意图不明确，建议添加文档')
        
        return recommendations
    
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
    
    def _save_learning_data(self, audit_result: Dict):
        """保存学习数据"""
        # 保存审计结果用于学习
        learning_file = Path('/home/admin/Ziwei/data/audit_learning.json')
        learning_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 追加学习数据
        self.learning_data['experiences'].append({
            'timestamp': audit_result['timestamp'],
            'risk_score': audit_result['security']['risk_score'],
            'quality_score': audit_result['quality']['score'],
            'issue_count': len(audit_result['security']['issues'])
        })
        
        # 只保留最近 100 次
        self.learning_data['experiences'] = self.learning_data['experiences'][-100:]
        
        with open(learning_file, 'w') as f:
            json.dump(self.learning_data, f, indent=2)
    
    def _print_report(self, audit_result: Dict):
        """打印审计报告"""
        print("\n" + "=" * 70)
        print("📊 审计报告")
        print("=" * 70)
        
        print(f"\n📁 审计文件：{audit_result['files_audited']} 个")
        print(f"⏰ 审计时间：{audit_result['timestamp']}")
        
        print(f"\n🔒 安全状态:")
        print(f"   风险评分：{audit_result['security']['risk_score']:.2f}/1.00")
        print(f"   发现问题：{len(audit_result['security']['issues'])} 个")
        
        # 按严重程度分组
        by_severity = {}
        for issue in audit_result['security']['issues']:
            severity = issue['severity']
            by_severity[severity] = by_severity.get(severity, 0) + 1
        
        for severity, count in sorted(by_severity.items()):
            emoji = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}.get(severity, '⚪')
            print(f"   {emoji} {severity.upper()}: {count} 个")
        
        print(f"\n📊 质量评估:")
        print(f"   评分：{audit_result['quality']['score']:.1f}/10")
        print(f"   等级：{audit_result['quality']['grade']}")
        
        if audit_result['understanding'].get('primary_intent'):
            print(f"\n🧠 代码理解:")
            print(f"   主要意图：{audit_result['understanding']['primary_intent']}")
        
        if audit_result['auto_fixes']:
            print(f"\n🔧 自动修复:")
            print(f"   可自动修复：{sum(1 for f in audit_result['auto_fixes'] if f['auto_fixable'])} 个")
            print(f"   需手动修复：{sum(1 for f in audit_result['auto_fixes'] if not f['auto_fixable'])} 个")
        
        if audit_result['recommendations']:
            print(f"\n💡 建议:")
            for rec in audit_result['recommendations']:
                print(f"   {rec}")
        
        print("\n" + "=" * 70)


def main():
    """主函数"""
    audit_system = IntelligentAuditSystem()
    
    # 审计紫微制造项目
    projects_to_audit = [
        '/home/admin/Ziwei/scripts',
        '/home/admin/Ziwei/tasks/CRYPTO-WALLET-TRACKER-001',
        '/home/admin/Ziwei/tasks/DATA-CONVERTER-PRO-001'
    ]
    
    for project in projects_to_audit:
        if Path(project).exists():
            audit_system.audit_project(project)
        else:
            print(f"⚠️  项目不存在：{project}")


if __name__ == '__main__':
    main()
