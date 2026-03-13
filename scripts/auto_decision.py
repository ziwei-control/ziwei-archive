#!/usr/bin/env python3
# =============================================================================
# 紫微制造 - 自动决策引擎 v1.0
# 功能：在授权范围内自主决策，无需用户干预
# =============================================================================

import json
from datetime import datetime
from pathlib import Path

# 配置
KNOWLEDGE_BASE = Path("/home/admin/Ziwei/data/knowledge/work_methodology.json")
DECISION_LOG = Path("/home/admin/Ziwei/data/logs/observer/decisions.log")

# 授权范围
AUTHORIZATION = {
    'process_management': True,      # 进程管理（重启、清理）
    'take_profit_adjust': 0.05,      # 止盈调整 ±5%
    'position_adjust': 0.10,         # 仓位调整 ±10%
    'stop_loss_adjust': 0.02,        # 止损调整 ±2%
    'max_trade_usd': 1000,           # 最大交易金额 $1000
}


class AutoDecision:
    """自动决策引擎"""
    
    def __init__(self):
        self.decision_count = 0
        self.load_knowledge()
    
    def load_knowledge(self):
        """加载知识库"""
        if KNOWLEDGE_BASE.exists():
            with open(KNOWLEDGE_BASE, 'r', encoding='utf-8') as f:
                self.knowledge = json.load(f)
        else:
            self.knowledge = {}
    
    def log(self, message: str):
        """记录决策日志"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_line = f"[{timestamp}] [决策] {message}\n"
        
        with open(DECISION_LOG, 'a', encoding='utf-8') as f:
            f.write(log_line)
        
        print(log_line, end='')
    
    def can_decide(self, decision_type: str, risk_level: str, amount_usd: float = 0) -> bool:
        """判断是否可以自主决策"""
        # 检查授权
        if decision_type == 'process_management':
            return AUTHORIZATION['process_management']
        
        if decision_type == 'take_profit_adjust':
            return True  # 在范围内已检查
        
        if decision_type == 'position_adjust':
            return True  # 在范围内已检查
        
        # 检查金额
        if amount_usd > AUTHORIZATION['max_trade_usd']:
            return False
        
        # 检查风险
        if risk_level == 'high':
            return False
        
        return True
    
    def make_decision(self, context: dict) -> dict:
        """做决策"""
        decision_type = context.get('type')
        risk_level = context.get('risk', 'medium')
        amount_usd = context.get('amount', 0)
        
        # 检查是否可以自主
        if not self.can_decide(decision_type, risk_level, amount_usd):
            return {
                'action': 'need_approval',
                'reason': '超出授权范围'
            }
        
        # 检索类似案例
        similar_cases = self.find_similar_cases(context)
        
        # 生成决策
        decision = self.generate_decision(context, similar_cases)
        
        # 记录决策
        self.log_decision(context, decision)
        
        return decision
    
    def find_similar_cases(self, context: dict, limit: int = 3) -> list:
        """查找类似案例"""
        similar = []
        
        # 搜索知识库
        for case in self.knowledge.get('problem_solving', []):
            if context.get('problem', '') in case.get('problem', ''):
                similar.append(case)
        
        return similar[:limit]
    
    def generate_decision(self, context: dict, similar_cases: list) -> dict:
        """生成决策"""
        # 有类似案例，参考案例
        if similar_cases:
            best_case = similar_cases[0]
            return {
                'action': 'execute',
                'method': best_case.get('method', ''),
                'reason': f'参考历史案例：{best_case.get("problem", "")}'
            }
        
        # 没有类似案例，使用默认策略
        return {
            'action': 'execute',
            'method': context.get('default_method', '标准流程'),
            'reason': '使用默认策略'
        }
    
    def log_decision(self, context: dict, decision: dict):
        """记录决策"""
        self.decision_count += 1
        self.log(f"决策 #{self.decision_count}: {context.get('type', '未知')} → {decision.get('action', '未知')}")
        self.log(f"  原因：{decision.get('reason', '无')}")
        self.log(f"  方法：{decision.get('method', '无')}")


def main():
    """测试"""
    engine = AutoDecision()
    
    # 测试决策
    test_context = {
        'type': 'process_management',
        'problem': '策略引擎重复进程',
        'risk': 'low',
        'default_method': '清理旧进程 + 重启'
    }
    
    decision = engine.make_decision(test_context)
    print(f"\n测试结果：{decision}")


if __name__ == "__main__":
    main()
