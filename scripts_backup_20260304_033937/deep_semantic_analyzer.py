#!/usr/bin/env python3
# =============================================================================
# 深度语义理解引擎
# 功能：理解需求背后的真实意图 + 自动补全缺失信息 + 智能推荐
# =============================================================================

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple


class DeepSemanticAnalyzer:
    """深度语义理解引擎"""
    
    def __init__(self):
        self.intent_patterns = {
            'data_processing': ['处理', '分析', '转换', '解析', '提取', '验证'],
            'automation': ['自动', '批量', '脚本', '定时', '监控'],
            'web_service': ['网站', 'API', '服务', '接口', 'REST'],
            'cli_tool': ['工具', '命令行', '实用', '助手'],
            'bot': ['机器人', '自动回复', '通知', '推送'],
            'gui_app': ['界面', '图形', '窗口', '桌面'],
            'mobile': ['手机', '移动', 'APP', 'iOS', 'Android']
        }
        
        self.tech_stack_recommendations = {
            'data_processing': ['pandas', 'numpy', 'polars'],
            'automation': ['schedule', 'apscheduler', 'croniter'],
            'web_service': ['fastapi', 'flask', 'django'],
            'cli_tool': ['argparse', 'click', 'typer'],
            'bot': ['telegram', 'discord.py', 'aiogram'],
            'gui_app': ['tkinter', 'PyQt6', 'flet'],
            'mobile': ['kivy', 'flet', 'beekeep']
        }
    
    def analyze_intent(self, spec_text: str) -> Dict:
        """分析真实意图"""
        print("\n🧠 深度语义分析...")
        
        # 1. 意图识别
        intents = []
        for intent, keywords in self.intent_patterns.items():
            score = sum(1 for kw in keywords if kw in spec_text.lower())
            if score > 0:
                intents.append({
                    'intent': intent,
                    'confidence': score / len(keywords),
                    'matched_keywords': [kw for kw in keywords if kw in spec_text.lower()]
                })
        
        intents.sort(key=lambda x: x['confidence'], reverse=True)
        
        # 2. 缺失信息检测
        missing_info = self.detect_missing_info(spec_text)
        
        # 3. 技术栈推荐
        recommended_stack = self.recommend_tech_stack(intents[0]['intent'] if intents else 'cli_tool')
        
        # 4. 功能建议
        feature_suggestions = self.suggest_features(intents[0]['intent'] if intents else 'cli_tool')
        
        # 5. 风险评估
        risks = self.assess_risks(spec_text)
        
        result = {
            'intents': intents[:3],
            'missing_info': missing_info,
            'recommended_stack': recommended_stack,
            'feature_suggestions': feature_suggestions,
            'risks': risks,
            'complexity_score': self.calculate_complexity(spec_text)
        }
        
        print(f"   主要意图：{intents[0]['intent'] if intents else 'unknown'} (置信度：{intents[0]['confidence']:.0%} if intents else 0)")
        print(f"   缺失信息：{len(missing_info)} 项")
        print(f"   推荐技术栈：{', '.join(recommended_stack[:3])}")
        print(f"   功能建议：{len(feature_suggestions)} 条")
        print(f"   风险点：{len(risks)} 个")
        print(f"   复杂度：{result['complexity_score']}/10")
        
        return result
    
    def detect_missing_info(self, spec_text: str) -> List[Dict]:
        """检测缺失信息"""
        missing = []
        
        # 检查必要部分
        required_sections = {
            '任务描述': '缺少项目描述，AI 无法理解项目目标',
            '功能需求': '缺少功能需求，AI 无法生成完整代码',
            '技术栈': '缺少技术栈指定，AI 会自行选择可能不符合预期',
            '验收标准': '缺少验收标准，无法评估生成质量'
        }
        
        for section, message in required_sections.items():
            if section not in spec_text:
                missing.append({
                    'section': section,
                    'severity': 'high' if section in ['任务描述', '功能需求'] else 'medium',
                    'message': message,
                    'suggestion': f'请添加 {section} 部分'
                })
        
        # 检查具体信息
        if '输入' not in spec_text and '输出' not in spec_text:
            missing.append({
                'section': '输入输出',
                'severity': 'medium',
                'message': '未指定输入输出格式',
                'suggestion': '说明程序的输入和预期输出'
            })
        
        if '示例' not in spec_text and '例子' not in spec_text:
            missing.append({
                'section': '示例',
                'severity': 'low',
                'message': '缺少使用示例',
                'suggestion': '提供 1-2 个使用示例帮助 AI 理解'
            })
        
        return missing
    
    def recommend_tech_stack(self, intent: str) -> List[str]:
        """推荐技术栈"""
        base_stack = self.tech_stack_recommendations.get(intent, ['argparse'])
        
        # 添加通用推荐
        base_stack.extend(['pathlib', 'json', 'logging'])
        
        return base_stack
    
    def suggest_features(self, intent: str) -> List[Dict]:
        """功能建议"""
        suggestions = {
            'data_processing': [
                {'name': '进度条', 'priority': 'medium', 'description': '显示处理进度'},
                {'name': '错误恢复', 'priority': 'high', 'description': '失败后继续处理'},
                {'name': '日志记录', 'priority': 'high', 'description': '详细操作日志'}
            ],
            'automation': [
                {'name': '重试机制', 'priority': 'high', 'description': '失败自动重试'},
                {'name': '通知功能', 'priority': 'medium', 'description': '完成后通知'},
                {'name': '配置管理', 'priority': 'high', 'description': '外部配置文件'}
            ],
            'cli_tool': [
                {'name': '帮助文档', 'priority': 'high', 'description': '--help 详细说明'},
                {'name': '版本信息', 'priority': 'low', 'description': '--version 显示版本'},
                {'name': '配置文件', 'priority': 'medium', 'description': '支持配置文件'}
            ]
        }
        
        return suggestions.get(intent, [
            {'name': '错误处理', 'priority': 'high', 'description': '完善的错误处理'},
            {'name': '日志记录', 'priority': 'medium', 'description': '操作日志'}
        ])
    
    def assess_risks(self, spec_text: str) -> List[Dict]:
        """风险评估"""
        risks = []
        
        # 安全风险
        if '密码' in spec_text or '密钥' in spec_text or 'token' in spec_text.lower():
            risks.append({
                'type': 'security',
                'severity': 'high',
                'message': '涉及敏感信息处理',
                'mitigation': '使用环境变量或加密存储'
            })
        
        if '网络' in spec_text or 'HTTP' in spec_text or 'API' in spec_text:
            risks.append({
                'type': 'security',
                'severity': 'medium',
                'message': '涉及网络请求',
                'mitigation': '添加超时和重试机制'
            })
        
        # 性能风险
        if '批量' in spec_text or '大量' in spec_text or '并发' in spec_text:
            risks.append({
                'type': 'performance',
                'severity': 'medium',
                'message': '可能涉及大量数据处理',
                'mitigation': '考虑内存优化和并发处理'
            })
        
        # 依赖风险
        if '数据库' in spec_text or 'MySQL' in spec_text or 'MongoDB' in spec_text:
            risks.append({
                'type': 'dependency',
                'severity': 'low',
                'message': '需要外部依赖',
                'mitigation': '在 requirements.txt 中明确声明'
            })
        
        return risks
    
    def calculate_complexity(self, spec_text: str) -> int:
        """计算复杂度评分 (1-10)"""
        score = 3  # 基础分
        
        # 功能数量
        if spec_text.count('功能') > 5:
            score += 2
        elif spec_text.count('功能') > 2:
            score += 1
        
        # 技术复杂度
        complex_keywords = ['并发', '异步', '分布式', '微服务', '实时', '流处理']
        if any(kw in spec_text for kw in complex_keywords):
            score += 2
        
        # 集成复杂度
        integrations = ['API', '数据库', '第三方', 'OAuth', '支付']
        integration_count = sum(1 for kw in integrations if kw in spec_text)
        score += min(integration_count, 2)
        
        return min(score, 10)
    
    def enhance_spec(self, spec_text: str, analysis: Dict) -> str:
        """增强说明书"""
        enhanced = spec_text
        
        # 添加推荐技术栈
        if analysis['recommended_stack']:
            tech_section = "\n\n## 推荐技术栈\n"
            for tech in analysis['recommended_stack'][:5]:
                tech_section += f"- {tech}\n"
            enhanced += tech_section
        
        # 添加功能建议
        if analysis['feature_suggestions']:
            enhanced += "\n\n## 建议功能\n"
            for feature in analysis['feature_suggestions'][:3]:
                enhanced += f"- [{feature['priority']}] {feature['name']}: {feature['description']}\n"
        
        return enhanced


def main():
    """主函数"""
    analyzer = DeepSemanticAnalyzer()
    
    spec = """
    创建一个 Python 工具，批量处理 JSON 文件。
    需要验证格式，转换数据结构。
    """
    
    analysis = analyzer.analyze_intent(spec)
    
    print("\n📊 分析完成")
    print(f"   意图：{analysis['intents'][0]['intent']}")
    print(f"   复杂度：{analysis['complexity_score']}/10")


if __name__ == '__main__':
    main()
