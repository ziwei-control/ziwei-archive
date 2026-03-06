#!/usr/bin/env python3
# =============================================================================
# 全球战情室 - 市场影响分析 Dashboard 数据接口
# =============================================================================

import json
import sys
from pathlib import Path

# 添加脚本路径
sys.path.insert(0, str(Path(__file__).parent))

from news_market_analyzer import NewsMarketAnalyzer

def get_dashboard_html():
    """获取 Dashboard HTML 片段"""
    analyzer = NewsMarketAnalyzer()
    data = analyzer.get_dashboard_data()
    
    if data.get('status') != 'success':
        return f'<div class="error">❌ {data.get("error", "未知错误")}</div>'
    
    html = f"""
    <div class="market-analysis">
        <div class="summary-cards">
            <div class="card bullish">
                <div class="value">{data['summary']['bullish_count']}</div>
                <div class="label">📈 看涨币种</div>
            </div>
            <div class="card bearish">
                <div class="value">{data['summary']['bearish_count']}</div>
                <div class="label">📉 看跌币种</div>
            </div>
            <div class="card neutral">
                <div class="value">{data['summary']['neutral_count']}</div>
                <div class="label">➖ 中性币种</div>
            </div>
            <div class="card total">
                <div class="value">{data['summary']['analyzed_news']}</div>
                <div class="label">📰 分析新闻</div>
            </div>
        </div>
        
        <div class="predictions-table">
            <h3>🔮 价格预测（按影响程度排序）</h3>
            <table>
                <thead>
                    <tr>
                        <th>币种</th>
                        <th>情感得分</th>
                        <th>当前价格</th>
                        <th>预测价格</th>
                        <th>变化</th>
                        <th>影响</th>
                        <th>置信度</th>
                    </tr>
                </thead>
                <tbody>
"""
    
    for pred in data['top_predictions']:
        change_class = 'positive' if pred['change_percent'] > 0 else 'negative' if pred['change_percent'] < 0 else 'neutral'
        change_sign = '+' if pred['change_percent'] > 0 else ''
        
        html += f"""
                    <tr>
                        <td><strong>{pred['coin']}</strong><br><small>{pred['symbol']}</small></td>
                        <td>{pred['sentiment_score']:+.2f}</td>
                        <td>${pred['current_price']:,.2f}</td>
                        <td>${pred['predicted_price']:,.2f}</td>
                        <td class="{change_class}">{change_sign}{pred['change_percent']:.2f}%</td>
                        <td>{pred['impact'].replace('_', ' ').title()}</td>
                        <td>{pred['confidence'].title()}</td>
                    </tr>
"""
    
    html += """
                </tbody>
            </table>
        </div>
        
        <div class="recommendations">
            <h3>💡 投资建议</h3>
            <div class="rec-list">
"""
    
    for rec in data['recommendations']:
        rec_class = 'buy' if rec['type'] == 'BUY' else 'sell'
        rec_icon = '🟢' if rec['type'] == 'BUY' else '🔴'
        
        html += f"""
                <div class="rec-item {rec_class}">
                    <div class="rec-header">
                        <span class="rec-type">{rec_icon} {rec['type']}</span>
                        <span class="rec-coin">{rec['symbol']}</span>
                    </div>
                    <div class="rec-reason">{rec['reason']}</div>
                    <div class="rec-details">
                        <span class="rec-target">目标：${rec['target_price']:,.2f}</span>
                        <span class="rec-confidence">置信度：{rec['confidence'].title()}</span>
                    </div>
                </div>
"""
    
    html += f"""
            </div>
        </div>
        
        <div class="update-time">
            🕐 更新时间：{data['update_time']}
        </div>
    </div>
    
    <style>
        .market-analysis {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }}
        
        .summary-cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }}
        
        .card {{
            background: rgba(30, 30, 30, 0.8);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
        }}
        
        .card.bullish {{ border-color: #22c55e; }}
        .card.bearish {{ border-color: #ef4444; }}
        .card.neutral {{ border-color: #f59e0b; }}
        .card.total {{ border-color: #667eea; }}
        
        .card .value {{
            font-size: 2.5em;
            font-weight: 700;
            margin-bottom: 5px;
        }}
        
        .card.bullish .value {{ color: #22c55e; }}
        .card.bearish .value {{ color: #ef4444; }}
        .card.neutral .value {{ color: #f59e0b; }}
        .card.total .value {{ color: #667eea; }}
        
        .card .label {{
            color: #888;
            font-size: 0.9em;
        }}
        
        .predictions-table {{
            margin-bottom: 30px;
        }}
        
        .predictions-table h3 {{
            color: #667eea;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid rgba(102, 126, 234, 0.3);
        }}
        
        .predictions-table table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        .predictions-table th {{
            background: rgba(102, 126, 234, 0.2);
            color: #667eea;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }}
        
        .predictions-table td {{
            padding: 12px;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }}
        
        .predictions-table td.positive {{ color: #22c55e; }}
        .predictions-table td.negative {{ color: #ef4444; }}
        .predictions-table td.neutral {{ color: #888; }}
        
        .recommendations {{
            margin-bottom: 30px;
        }}
        
        .recommendations h3 {{
            color: #667eea;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid rgba(102, 126, 234, 0.3);
        }}
        
        .rec-list {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 15px;
        }}
        
        .rec-item {{
            background: rgba(30, 30, 30, 0.8);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 8px;
            padding: 15px;
        }}
        
        .rec-item.buy {{ border-left: 4px solid #22c55e; }}
        .rec-item.sell {{ border-left: 4px solid #ef4444; }}
        
        .rec-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}
        
        .rec-type {{
            font-weight: 700;
            font-size: 1.1em;
        }}
        
        .rec-coin {{
            color: #667eea;
            font-weight: 600;
        }}
        
        .rec-reason {{
            color: #888;
            margin-bottom: 10px;
            font-size: 0.9em;
        }}
        
        .rec-details {{
            display: flex;
            justify-content: space-between;
            font-size: 0.85em;
        }}
        
        .rec-target {{
            color: #22c55e;
        }}
        
        .rec-confidence {{
            color: #f59e0b;
        }}
        
        .update-time {{
            color: #666;
            font-size: 0.85em;
            text-align: right;
            padding-top: 15px;
            border-top: 1px solid rgba(255,255,255,0.1);
        }}
    </style>
"""
    
    return html


if __name__ == '__main__':
    print(get_dashboard_html())
