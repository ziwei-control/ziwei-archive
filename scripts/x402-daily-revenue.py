#!/usr/bin/env python3
# =============================================================================
# x402 API - 每日收入报告生成器
# 功能：自动汇总每日收入，生成报告
# =============================================================================

import json
import os
from datetime import datetime
from pathlib import Path

# 配置
DATA_DIR = Path("/home/admin/Ziwei/projects/x402-api/data")
REPORTS_DIR = Path("/home/admin/Ziwei/data/x402/reports/daily")
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

def generate_daily_report():
    """生成每日收入报告"""
    today = datetime.now().strftime('%Y-%m-%d')
    payments_file = DATA_DIR / "payments.json"
    
    if not payments_file.exists():
        return "今日无交易数据"
    
    with open(payments_file) as f:
        data = json.load(f)
    
    payments = data.get('payments', {})
    
    # 筛选今日交易
    today_payments = []
    for tx_hash, payment in payments.items():
        tx_date = payment.get('timestamp', '')[:10]
        if tx_date == today:
            today_payments.append(payment)
    
    if not today_payments:
        return f"{today} 暂无交易"
    
    # 统计
    total_revenue = sum(p.get('amount', 0) for p in today_payments)
    total_calls = len(today_payments)
    avg_order = total_revenue / total_calls if total_calls > 0 else 0
    
    # 按端点统计（从 tx_hash 推断）
    by_endpoint = {}
    for p in today_payments:
        endpoint = p.get('endpoint', 'unknown')
        by_endpoint[endpoint] = by_endpoint.get(endpoint, 0) + p.get('amount', 0)
    
    # 生成报告
    report = f"""
📊 x402 API 每日收入报告
日期：{today}

💰 总收入：{total_revenue:.4f} USDC
📞 总调用：{total_calls} 次
📈 平均客单：{avg_order:.4f} USDC

📋 按端点统计：
"""
    
    for endpoint, revenue in sorted(by_endpoint.items(), key=lambda x: -x[1]):
        report += f"  - {endpoint}: {revenue:.4f} USDC\n"
    
    # 写入报告文件
    report_file = REPORTS_DIR / f"daily_{today}.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    # 同时输出到控制台
    print(report)
    
    return report

def generate_weekly_summary():
    """生成周度总结（简单版）"""
    from datetime import timedelta
    
    today = datetime.now()
    week_start = today - timedelta(days=today.weekday())
    
    payments_file = DATA_DIR / "payments.json"
    if not payments_file.exists():
        return "无数据"
    
    with open(payments_file) as f:
        data = json.load(f)
    
    payments = data.get('payments', {})
    
    # 筛选本周交易
    week_payments = []
    for payment in payments.values():
        tx_date = payment.get('timestamp', '')[:10]
        if tx_date >= week_start.strftime('%Y-%m-%d'):
            week_payments.append(payment)
    
    total_revenue = sum(p.get('amount', 0) for p in week_payments)
    total_calls = len(week_payments)
    
    summary = f"""
📈 x402 API 周度总结
周期：{week_start.strftime('%Y-%m-%d')} 至 {today.strftime('%Y-%m-%d')}

💰 总收入：{total_revenue:.4f} USDC
📞 总调用：{total_calls} 次
📊 日均收入：{total_revenue/7:.4f} USDC
"""
    
    # 写入文件
    summary_file = REPORTS_DIR / f"weekly_{week_start.strftime('%Y%m%d')}.md"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    print(summary)
    return summary

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'weekly':
        generate_weekly_summary()
    else:
        generate_daily_report()
