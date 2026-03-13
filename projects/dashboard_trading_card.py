#!/usr/bin/env python3
# =============================================================================
# 紫微智控 Dashboard - 独立交易持仓卡片 v2.0
# 功能：实时显示交易机器人持仓、余额、交易历史，每 30 秒自动刷新
# =============================================================================

import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

Ziwei_DIR = Path("/home/admin/Ziwei/data")

def get_trade_history():
    """获取交易历史记录（从独立文件读取）"""
    trade_history = []
    jsonl_file = Ziwei_DIR / "strategy" / "trade_history.jsonl"
    
    if not jsonl_file.exists():
        return []
    
    try:
        with open(jsonl_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    trade = json.loads(line)
                    # 过滤异常交易
                    if trade.get('value', 0) > 0.001:
                        trade_history.append(trade)
    except Exception as e:
        print(f"读取交易历史失败：{e}")
    
    # 按时间排序（最新的在前）
    trade_history.sort(key=lambda x: x.get('time', ''), reverse=True)
    
    return trade_history


def get_my_holdings():
    """我的持仓 - 独立大卡片（实时显示余额和持仓）"""
    try:
        # 读取账户状态
        account_file = Ziwei_DIR / "strategy" / "account_status.json"
        
        if not account_file.exists():
            return """
            <div class="card" style="grid-column:span 3;">
                <h2>💰 我的持仓</h2>
                <p style="color:#666;">暂无持仓数据</p>
            </div>
            """
        
        with open(account_file) as f:
            account = json.load(f)
        
        balance = account.get('balance', 0)
        portfolio = account.get('portfolio', {})
        total_trades = account.get('total_trades', 0)
        
        # 计算持仓总价值
        total_portfolio_value = sum(
            holding['amount'] * holding['entry_price'] 
            for holding in portfolio.values()
        )
        
        # 总资产
        total_assets = balance + total_portfolio_value
        
        # 仓位计算
        position_ratio = (total_portfolio_value / total_assets * 100) if total_assets > 0 else 0
        position_status = "保守" if position_ratio < 40 else "适中" if position_ratio < 70 else "激进"
        position_color = "#22c55e" if position_ratio < 40 else "#f59e0b" if position_ratio < 70 else "#ef4444"
        
        # 获取交易历史
        trade_history = get_trade_history()
        
        # 按类型分组
        by_type = defaultdict(list)
        for t in trade_history:
            by_type[t.get('type', 'unknown')].append(t)
        
        # 生成交易时间线 HTML（只显示建仓和清仓）
        timeline_html = ""
        important_trades = by_type.get('建仓', []) + by_type.get('清仓', [])
        important_trades.sort(key=lambda x: x.get('time', ''), reverse=True)
        
        if important_trades:
            for trade in important_trades[:20]:  # 最多显示 20 笔重要交易
                trade_type = trade.get('type', '')
                
                if trade_type == '建仓':
                    icon = "🟢"
                    bg_color = "rgba(34,197,94,0.05)"
                    border_color = "#22c55e"
                    text_color = "#22c55e"
                elif trade_type == '清仓':
                    icon = "🔴"
                    bg_color = "rgba(239,68,68,0.05)"
                    border_color = "#ef4444"
                    text_color = "#ef4444"
                else:
                    continue  # 跳过加仓
                
                # 格式化时间
                time_str = trade.get('time', 'N/A')
                if 'T' in time_str:
                    time_str = time_str.replace('T', ' ').split('.')[0]
                
                # 计算盈亏（如果是清仓）
                pnl_html = ""
                if trade_type == '清仓':
                    pnl = trade.get('pnl', 0)
                    pnl_color = "#22c55e" if pnl >= 0 else "#ef4444"
                    pnl_sign = "+" if pnl >= 0 else ""
                    pnl_html = f"""
                    <div style="margin-top:6px;color:{pnl_color};font-weight:600;font-size:0.85em;">
                        📈 盈亏：{pnl_sign}${pnl:,.2f}
                    </div>
                    """
                
                timeline_html += f"""
                <div style="padding:10px;margin:8px 0;background:{bg_color};border-left:3px solid {border_color};border-radius:4px;font-size:0.85em;">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                        <div style="display:flex;align-items:center;gap:8px;">
                            <span style="font-size:1.2em;">{icon}</span>
                            <span style="font-weight:600;color:{text_color};">{trade_type}</span>
                            <span style="color:#e0e0e0;font-weight:600;">{trade.get('symbol', 'UNKNOWN')}</span>
                        </div>
                        <span style="color:#888;font-size:0.85em;">🕐 {time_str}</span>
                    </div>
                    <div style="color:#666;font-size:0.85em;">
                        💵 ${trade.get('price', 0):,.6f} × {trade.get('amount', 0):,.2f} = ${trade.get('value', 0):,.2f}
                    </div>
                    {pnl_html}
                </div>
                """
        else:
            timeline_html = """
            <div style="padding:20px;text-align:center;background:rgba(107,116,128,0.05);border-radius:8px;">
                <div style="color:#888;font-size:0.9em;">暂无交易记录</div>
            </div>
            """
        
        # 生成持仓卡片
        holdings_html = ""
        if portfolio:
            for coin, holding in sorted(portfolio.items(), key=lambda x: x[1]['amount'] * x[1]['entry_price'], reverse=True):
                value = holding['amount'] * holding['entry_price']
                
                # 格式化入场时间
                entry_time = holding.get('entry_time', 'N/A')
                if 'T' in entry_time:
                    entry_time = entry_time.replace('T', ' ').split('.')[0]
                
                holdings_html += f"""
                <div style="padding:15px;margin:10px 0;background:rgba(34,197,94,0.05);border:1px solid rgba(34,197,94,0.2);border-radius:10px;">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
                        <div style="display:flex;align-items:center;gap:10px;">
                            <span style="font-size:1.3em;font-weight:700;color:#22c55e;">{coin}</span>
                            <span style="font-size:0.75em;padding:3px 8px;background:rgba(102,126,234,0.2);border-radius:4px;color:#667eea;">持仓</span>
                        </div>
                        <span style="font-size:1.1em;font-weight:700;color:#e0e0e0;">💰 ${value:,.2f}</span>
                    </div>
                    
                    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;">
                        <div>
                            <div style="color:#666;font-size:0.75em;margin-bottom:4px;">📊 持仓数量</div>
                            <div style="font-weight:600;color:#e0e0e0;font-size:0.9em;">{holding['amount']:,.2f}</div>
                        </div>
                        <div>
                            <div style="color:#666;font-size:0.75em;margin-bottom:4px;">💵 入场价格</div>
                            <div style="font-weight:600;color:#e0e0e0;font-size:0.9em;">${holding['entry_price']:,.6f}</div>
                        </div>
                        <div>
                            <div style="color:#666;font-size:0.75em;margin-bottom:4px;">🕐 建仓时间</div>
                            <div style="font-weight:600;color:#e0e0e0;font-size:0.9em;">{entry_time}</div>
                        </div>
                        <div>
                            <div style="color:#666;font-size:0.75em;margin-bottom:4px;">🎯 止盈</div>
                            <div style="font-weight:600;color:#22c55e;font-size:0.9em;">${holding.get('take_profit', 0):,.6f}</div>
                        </div>
                    </div>
                </div>
                """
        else:
            holdings_html = """
            <div style="padding:30px;text-align:center;background:rgba(107,116,128,0.05);border-radius:10px;">
                <div style="font-size:1.2em;color:#888;margin-bottom:10px;">⏳ 空仓等待信号中...</div>
            </div>
            """
        
        # 统计信息
        stats_html = f"""
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:20px;">
            <div style="background:linear-gradient(135deg, rgba(102,126,234,0.2), rgba(118,75,162,0.2));border:1px solid rgba(102,126,234,0.3);border-radius:10px;padding:15px;text-align:center;">
                <div style="color:#667eea;font-size:0.75em;margin-bottom:5px;">💵 可用余额</div>
                <div style="color:#e0e0e0;font-size:1.5em;font-weight:700;">${balance:,.2f}</div>
                <div style="color:#888;font-size:0.7em;">USDC</div>
            </div>
            <div style="background:linear-gradient(135deg, rgba(34,197,94,0.2), rgba(34,197,94,0.1));border:1px solid rgba(34,197,94,0.3);border-radius:10px;padding:15px;text-align:center;">
                <div style="color:#22c55e;font-size:0.75em;margin-bottom:5px;">📦 持仓价值</div>
                <div style="color:#e0e0e0;font-size:1.5em;font-weight:700;">${total_portfolio_value:,.2f}</div>
                <div style="color:#888;font-size:0.7em;">USDC</div>
            </div>
            <div style="background:linear-gradient(135deg, rgba(139,92,246,0.2), rgba(139,92,246,0.1));border:1px solid rgba(139,92,246,0.3);border-radius:10px;padding:15px;text-align:center;">
                <div style="color:#8b5cf6;font-size:0.75em;margin-bottom:5px;">💎 总资产</div>
                <div style="color:#e0e0e0;font-size:1.5em;font-weight:700;">${total_assets:,.2f}</div>
                <div style="color:#888;font-size:0.7em;">USDC</div>
            </div>
        </div>
        
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:20px;">
            <div style="background:linear-gradient(135deg, rgba(245,158,11,0.2), rgba(245,158,11,0.1));border:1px solid rgba(245,158,11,0.3);border-radius:10px;padding:15px;text-align:center;">
                <div style="color:#f59e0b;font-size:0.75em;margin-bottom:5px;">📊 总交易数</div>
                <div style="color:#e0e0e0;font-size:1.5em;font-weight:700;">{total_trades}</div>
                <div style="color:#888;font-size:0.7em;">笔</div>
            </div>
            <div style="background:linear-gradient(135deg, rgba(34,197,94,0.2), rgba(34,197,94,0.1));border:1px solid rgba(34,197,94,0.3);border-radius:10px;padding:15px;text-align:center;">
                <div style="color:#22c55e;font-size:0.75em;margin-bottom:5px;">🟢 建仓次数</div>
                <div style="color:#e0e0e0;font-size:1.5em;font-weight:700;">{len(by_type.get('建仓', []))}</div>
                <div style="color:#888;font-size:0.7em;">次</div>
            </div>
            <div style="background:linear-gradient(135deg, rgba(239,68,68,0.2), rgba(239,68,68,0.1));border:1px solid rgba(239,68,68,0.3);border-radius:10px;padding:15px;text-align:center;">
                <div style="color:#ef4444;font-size:0.75em;margin-bottom:5px;">🔴 清仓次数</div>
                <div style="color:#e0e0e0;font-size:1.5em;font-weight:700;">{len(by_type.get('清仓', []))}</div>
                <div style="color:#888;font-size:0.7em;">次</div>
            </div>
        </div>
        """
        
        # 获取当前时间
        from datetime import datetime
        current_time = datetime.now().strftime('%H:%M:%S')
        
        return f"""
        <div class="card" style="grid-column:span 3;position:relative;">
            <div style="position:absolute;top:10px;right:15px;font-size:0.75em;color:#888;" data-last-update>
                📅 最后更新：{current_time}
            </div>
            <h2 style="margin-bottom:20px;">💰 我的持仓 (实时)</h2>
            
            {stats_html}
            
            <div style="margin-bottom:20px;padding:12px;background:rgba({102 if position_ratio < 40 else 245 if position_ratio < 70 else 239},{126 if position_ratio < 40 else 158 if position_ratio < 70 else 68},{234 if position_ratio < 40 else 11 if position_ratio < 70 else 68},0.1);border-left:4px solid {position_color};border-radius:8px;">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <span style="font-weight:600;color:{position_color};">📊 当前仓位：{position_ratio:.1f}%</span>
                    <span style="font-size:0.85em;color:#888;">({position_status})</span>
                </div>
            </div>
            
            <!-- 交易时间线（只显示建仓和清仓） -->
            <div style="margin-top:20px;">
                <div style="font-weight:600;color:#667eea;margin-bottom:15px;font-size:1.1em;display:flex;justify-content:space-between;align-items:center;">
                    <span>📜 建仓/清仓记录</span>
                    <span style="font-size:0.85em;color:#888;">最近 {len(important_trades)} 笔重要交易</span>
                </div>
                <div style="background:rgba(0,0,0,0.2);border-radius:10px;padding:15px;max-height:500px;overflow-y:auto;">
                    {timeline_html}
                </div>
            </div>
            
            <!-- 持仓详情 -->
            <div style="margin-top:20px;">
                <div style="font-weight:600;color:#667eea;margin-bottom:15px;font-size:1.1em;display:flex;justify-content:space-between;align-items:center;">
                    <span>📦 持仓详情 ({len(portfolio)} 个币种)</span>
                    <span style="font-size:0.85em;color:#22c55e;font-weight:600;">总价值：${total_portfolio_value:,.2f}</span>
                </div>
                {holdings_html}
            </div>
            
            <div style="margin-top:20px;padding-top:15px;border-top:1px solid rgba(255,255,255,0.1);font-size:0.8em;color:#666;">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <span>🤖 策略引擎 v4.0 | 自动交易 | 实时风控</span>
                    <span data-refresh-timer>🔄 下次刷新：30 秒</span>
                </div>
            </div>
        </div>
        """
    except Exception as e:
        import traceback
        return f'<div class="card" style="grid-column:span 3;"><h2>💰 我的持仓</h2><span class="error">加载失败：{e}</span></div>'


if __name__ == "__main__":
    print(get_my_holdings())
