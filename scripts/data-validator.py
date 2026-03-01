#!/usr/bin/env python3
# =============================================================================
# 全球战情室 - 数据验证与去重模块
# 功能：双信源交叉验证、内容指纹生成、去重机制
# =============================================================================

import hashlib
import json
import time
from datetime import datetime, timedelta
from collections import defaultdict

class DataValidator:
    def __init__(self):
        self.alert_history = defaultdict(list)  # 存储历史警报
        self.source_cache = {}  # 缓存数据源信息
        
    def generate_content_fingerprint(self, content):
        """生成内容指纹（哈希值）"""
        if isinstance(content, dict):
            content_str = json.dumps(content, sort_keys=True, ensure_ascii=False)
        else:
            content_str = str(content)
        return hashlib.md5(content_str.encode('utf-8')).hexdigest()
    
    def validate_cross_sources(self, alert_data, sources):
        """
        双信源交叉验证
        alert_data: 警报数据
        sources: 数据源列表 [{'name': 'source1', 'data': {...}}, ...]
        """
        if len(sources) < 2:
            print(f"❌ 验证失败: 不足2个数据源 (只有{len(sources)}个)")
            return False
            
        # 检查关键字段是否一致
        key_fields = ['price', 'symbol', 'change_percent', 'timestamp']
        validation_passed = True
        
        for field in key_fields:
            if field in alert_data:
                values = []
                for source in sources:
                    if field in source['data']:
                        values.append(source['data'][field])
                
                if len(values) >= 2:
                    # 检查数值差异是否在可接受范围内
                    if field == 'price':
                        # 价格差异不超过5%
                        max_val = max(values)
                        min_val = min(values)
                        if (max_val - min_val) / max_val > 0.05:
                            print(f"❌ 价格验证失败: {field} 差异过大 {min_val} vs {max_val}")
                            validation_passed = False
                    elif field == 'change_percent':
                        # 涨跌幅差异不超过10%
                        max_val = max(values)
                        min_val = min(values)
                        if abs(max_val - min_val) > 10.0:
                            print(f"❌ 涨跌幅验证失败: {field} 差异过大 {min_val} vs {max_val}")
                            validation_passed = False
        
        if validation_passed:
            print("✅ 双信源验证通过")
        else:
            print("❌ 双信源验证失败")
            
        return validation_passed
    
    def check_duplicate_alert(self, alert_type, symbol, content_fingerprint, cooldown_hours=24):
        """
        检查重复警报
        实施"双发封顶"规则：24小时内同一标的最多推送2次
        """
        current_time = datetime.now()
        cutoff_time = current_time - timedelta(hours=cooldown_hours)
        
        # 清理过期的历史记录
        self.alert_history[(alert_type, symbol)] = [
            record for record in self.alert_history[(alert_type, symbol)]
            if record['timestamp'] > cutoff_time
        ]
        
        # 检查相似度
        similar_alerts = []
        for record in self.alert_history[(alert_type, symbol)]:
            if record['fingerprint'] == content_fingerprint:
                similar_alerts.append(record)
        
        # 如果已经有2个相同类型的警报，阻止发送
        if len(self.alert_history[(alert_type, symbol)]) >= 2:
            print(f"⚠️  警报限制: {alert_type} {symbol} 在{cooldown_hours}小时内已发送2次，阻止重复发送")
            return False
            
        # 检查内容相似度（简化版）
        if similar_alerts:
            print(f"⚠️  发现相似警报，但仍允许发送（未达到2次限制）")
            
        # 记录本次警报
        self.alert_history[(alert_type, symbol)].append({
            'timestamp': current_time,
            'fingerprint': content_fingerprint,
            'alert_type': alert_type,
            'symbol': symbol
        })
        
        return True
    
    def validate_ignis_special_rule(self, price_data):
        """
        Ignis专项验证规则
        价格必须突破并站稳0.01美元（1美分）整数关口
        """
        symbol = price_data.get('symbol', '').lower()
        if symbol not in ['ignis', 'ardr']:
            return True  # 不是Ignis/ARDR，跳过特殊验证
            
        current_price = price_data.get('price', 0)
        if current_price < 0.01:
            print(f"❌ Ignis验证失败: 价格 {current_price} < 0.01 USD")
            return False
            
        # 检查是否稳定在0.01以上（需要历史数据支持）
        # 这里简化处理，实际需要连续多次采样
        print(f"✅ Ignis验证通过: 价格 {current_price} >= 0.01 USD")
        return True

def test_validator():
    """测试验证器"""
    validator = DataValidator()
    
    # 测试内容指纹
    test_content = {"symbol": "BTC", "price": 50000, "change": 35.5}
    fingerprint = validator.generate_content_fingerprint(test_content)
    print(f"内容指纹: {fingerprint}")
    
    # 测试重复检查
    can_send = validator.check_duplicate_alert("crypto_alert", "BTC", fingerprint)
    print(f"可以发送: {can_send}")
    
    # 再次检查（应该仍然可以发送，因为还没达到2次）
    can_send2 = validator.check_duplicate_alert("crypto_alert", "BTC", fingerprint)
    print(f"可以发送(第二次): {can_send2}")
    
    # 第三次检查（应该被阻止）
    can_send3 = validator.check_duplicate_alert("crypto_alert", "BTC", fingerprint)
    print(f"可以发送(第三次): {can_send3}")

if __name__ == "__main__":
    test_validator()