#!/usr/bin/env python3
# =============================================================================
# 深度语义理解引擎 v2.0 - AI 增强版
# 功能：AI 驱动的深度需求理解 + 意图识别 + 主动澄清
# =============================================================================

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional


class DeepSemanticAnalyzerV2:
    """深度语义理解引擎 v2.0"""
    
    def __init__(self):
        self.domain_knowledge = self._load_domain_knowledge()
        self.intent_patterns = self._load_intent_patterns()
    
    def _load_domain_knowledge(self) -> Dict:
        """加载领域知识"""
        return {
            'cryptocurrency': {
                'keywords': ['加密货币', '区块链', '钱包', 'BTC', 'ETH', '币圈', 'token'],
                'concepts': ['去中心化', '智能合约', 'DeFi', 'NFT', '交易所'],
                'tools': ['钱包管理', '价格追踪', '交易机器人', '数据分析']
            },
            'web_development': {
                'keywords': ['网站', 'Web', 'API', '前端', '后端', 'Flask', 'Django'],
                'concepts': ['RESTful', '微服务', '数据库', '认证'],
                'tools': ['CMS', '博客', '电商', '管理系统']
            },
            'data_processing': {
                'keywords': ['数据', '分析', '转换', 'CSV', 'JSON', 'Excel'],
                'concepts': ['ETL', '数据清洗', '数据验证', '批量处理'],
                'tools': ['转换器', '分析工具', '报表生成']
            },
            'automation': {
                'keywords': ['自动', '批量', '脚本', '定时', '监控'],
                'concepts': ['工作流', '任务调度', '事件驱动'],
                'tools': ['自动化工具', '监控工具', '通知系统']
            },
            'file_management': {
                'keywords': ['文件', '批量', '重命名', '整理', '分类'],
                'concepts': ['文件系统', '元数据', '标签'],
                'tools': ['文件管理器', '批量工具', '同步工具']
            }
        }
    
    def _load_intent_patterns(self) -> Dict:
        """加载意图模式"""
        return {
            'create_tool': {
                'patterns': ['创建', '开发', '做一个', '需要一个'],
                'confidence': 0.9
            },
            'automate_task': {
                'patterns': ['自动', '批量', '定时', '一键'],
                'confidence': 0.85
            },
            'process_data': {
                'patterns': ['处理', '转换', '分析', '统计'],
                'confidence': 0.8
            },
            'manage_files': {
                'patterns': ['管理', '整理', '分类', '同步'],
                'confidence': 0.75
            },
            'monitor_system': {
                'patterns': ['监控', '检测', '警报', '通知'],
                'confidence': 0.7
            }
        }
    
    def analyze(self, spec_text: str) -> Dict:
        """深度语义分析"""
        print("\n🧠 深度语义分析 v2.0...")
        
        # 1. 领域识别
        domain = self._identify_domain(spec_text)
        
        # 2. 意图识别
        intents = self._identify_intents(spec_text)
        
        # 3. 需求提取
        requirements = self._extract_requirements(spec_text)
        
        # 4. 缺失检测
        missing = self._detect_missing(spec_text, domain)
        
        # 5. 功能建议
        suggestions = self._suggest_features(domain, requirements)
        
        # 6. 风险评估
        risks = self._assess_risks(domain, requirements)
        
        # 7. 技术推荐
        tech_stack = self._recommend_tech(domain, requirements)
        
        # 8. 复杂度评估
        complexity = self._calculate_complexity(requirements, domain)
        
        result = {
            'domain': domain,
            'intents': intents,
            'requirements': requirements,
            'missing_info': missing,
            'feature_suggestions': suggestions,
            'risks': risks,
            'recommended_tech': tech_stack,
            'complexity_score': complexity,
            'understanding_confidence': self._calculate_confidence(domain, intents)
        }
        
        print(f"   领域：{domain['name']} (置信度：{domain['confidence']:.0%})")
        print(f"   意图：{len(intents)} 个")
        print(f"   需求：{len(requirements)} 项")
        print(f"   缺失：{len(missing)} 项")
        print(f"   建议：{len(suggestions)} 条")
        print(f"   风险：{len(risks)} 个")
        print(f"   理解置信度：{result['understanding_confidence']:.0%}")
        
        return result
    
    def _identify_domain(self, spec_text: str) -> Dict:
        """识别领域"""
        best_match = None
        best_score = 0
        
        for domain_name, domain_info in self.domain_knowledge.items():
            score = 0
            for keyword in domain_info['keywords']:
                if keyword.lower() in spec_text.lower():
                    score += 1
            
            if score > best_score:
                best_score = score
                best_match = {
                    'name': domain_name,
                    'confidence': min(score / len(domain_info['keywords']), 1.0),
                    'matched_keywords': [kw for kw in domain_info['keywords'] if kw.lower() in spec_text.lower()]
                }
        
        return best_match or {'name': 'general', 'confidence': 0.5, 'matched_keywords': []}
    
    def _identify_intents(self, spec_text: str) -> List[Dict]:
        """识别意图"""
        intents = []
        
        for intent_name, intent_info in self.intent_patterns.items():
            matched = []
            for pattern in intent_info['patterns']:
                if pattern in spec_text.lower():
                    matched.append(pattern)
            
            if matched:
                intents.append({
                    'name': intent_name,
                    'confidence': intent_info['confidence'],
                    'matched_patterns': matched
                })
        
        intents.sort(key=lambda x: x['confidence'], reverse=True)
        return intents
    
    def _extract_requirements(self, spec_text: str) -> List[Dict]:
        """提取需求"""
        requirements = []
        
        # 提取功能需求
        if '功能' in spec_text:
            func_section = spec_text.split('功能')[1].split('\n\n')[0]
            for line in func_section.split('\n'):
                if line.strip() and not line.strip().startswith('#'):
                    requirements.append({
                        'type': 'functional',
                        'description': line.strip(),
                        'priority': 'high'
                    })
        
        # 提取技术需求
        if '技术栈' in spec_text or 'Python' in spec_text:
            requirements.append({
                'type': 'technical',
                'description': 'Python 3.8+',
                'priority': 'high'
            })
        
        # 提取安全需求
        if '安全' in spec_text or '错误处理' in spec_text:
            requirements.append({
                'type': 'security',
                'description': '错误处理完善',
                'priority': 'medium'
            })
        
        return requirements
    
    def _detect_missing(self, spec_text: str, domain: Dict) -> List[Dict]:
        """检测缺失信息"""
        missing = []
        
        # 检查必要部分
        required_sections = {
            '任务描述': '缺少项目描述',
            '功能需求': '缺少功能需求',
            '验收标准': '缺少验收标准'
        }
        
        for section, message in required_sections.items():
            if section not in spec_text:
                missing.append({
                    'section': section,
                    'severity': 'high',
                    'message': message
                })
        
        # 领域特定检查
        if domain['name'] == 'cryptocurrency':
            if 'API' not in spec_text and '接口' not in spec_text:
                missing.append({
                    'section': 'API 配置',
                    'severity': 'medium',
                    'message': '加密货币工具需要 API 配置'
                })
        
        return missing
    
    def _suggest_features(self, domain: Dict, requirements: List[Dict]) -> List[Dict]:
        """功能建议"""
        suggestions = []
        
        # 基于领域建议
        if domain['name'] == 'cryptocurrency':
            suggestions.extend([
                {'name': '价格警报', 'priority': 'medium', 'description': '价格波动通知'},
                {'name': '历史记录', 'priority': 'low', 'description': '查询历史记录'},
                {'name': '多钱包支持', 'priority': 'high', 'description': '支持多个钱包地址'}
            ])
        elif domain['name'] == 'data_processing':
            suggestions.extend([
                {'name': '进度条', 'priority': 'medium', 'description': '显示处理进度'},
                {'name': '错误恢复', 'priority': 'high', 'description': '失败后继续处理'},
                {'name': '日志记录', 'priority': 'high', 'description': '详细操作日志'}
            ])
        
        return suggestions
    
    def _assess_risks(self, domain: Dict, requirements: List[Dict]) -> List[Dict]:
        """风险评估"""
        risks = []
        
        # 通用风险
        if any('网络' in str(req) or 'API' in str(req) for req in requirements):
            risks.append({
                'type': 'network',
                'severity': 'medium',
                'message': '涉及网络请求',
                'mitigation': '添加超时和重试机制'
            })
        
        # 领域特定风险
        if domain['name'] == 'cryptocurrency':
            risks.append({
                'type': 'security',
                'severity': 'high',
                'message': '涉及敏感信息（API Key）',
                'mitigation': '使用环境变量存储'
            })
        
        return risks
    
    def _recommend_tech(self, domain: Dict, requirements: List[Dict]) -> List[str]:
        """技术推荐"""
        base_stack = ['Python 3.8+', 'pathlib', 'argparse']
        
        if domain['name'] == 'cryptocurrency':
            base_stack.extend(['requests', 'python-dotenv'])
        elif domain['name'] == 'data_processing':
            base_stack.extend(['pandas', 'json'])
        elif domain['name'] == 'web_development':
            base_stack.extend(['Flask', 'SQLAlchemy'])
        
        return base_stack
    
    def _calculate_complexity(self, requirements: List[Dict], domain: Dict) -> int:
        """计算复杂度"""
        score = 3
        
        # 需求数量
        if len(requirements) > 10:
            score += 2
        elif len(requirements) > 5:
            score += 1
        
        # 领域复杂度
        if domain['name'] in ['cryptocurrency', 'web_development']:
            score += 1
        
        return min(score, 10)
    
    def _calculate_confidence(self, domain: Dict, intents: List[Dict]) -> float:
        """计算理解置信度"""
        domain_conf = domain.get('confidence', 0.5)
        intent_conf = intents[0]['confidence'] if intents else 0.5
        
        return (domain_conf + intent_conf) / 2
    
    def ask_clarifying_questions(self, spec_text: str, analysis: Dict) -> List[str]:
        """生成澄清问题"""
        questions = []
        
        # 基于缺失信息
        for missing in analysis['missing_info']:
            if missing['severity'] == 'high':
                questions.append(f"请问{missing['section']}具体是什么？")
        
        # 基于领域
        if analysis['domain']['name'] == 'cryptocurrency':
            questions.append("需要支持哪些加密货币？（BTC/ETH/XRP 等）")
            questions.append("使用哪个 API 获取价格？（CoinGecko/CoinMarketCap）")
        
        # 基于功能
        if len(analysis['feature_suggestions']) > 0:
            questions.append("是否需要以下功能：" + ", ".join(
                f["name"] for f in analysis['feature_suggestions'][:3]
            ) + "?")
        
        return questions


def main():
    """测试函数"""
    analyzer = DeepSemanticAnalyzerV2()
    
    spec = """
    创建一个加密货币钱包余额查询工具
    支持 BTC/ETH/XRP
    需要实时价格
    """
    
    analysis = analyzer.analyze(spec)
    
    print("\n📊 分析完成")
    print(f"理解置信度：{analysis['understanding_confidence']:.0%}")
    
    questions = analyzer.ask_clarifying_questions(spec, analysis)
    if questions:
        print("\n❓ 澄清问题:")
        for q in questions:
            print(f"  - {q}")


if __name__ == '__main__':
    main()
