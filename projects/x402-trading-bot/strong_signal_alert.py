#!/usr/bin/env python3
# =============================================================================
# 强信号警报器 - 多通道通知
# 功能：监控策略引擎信号，发现强信号立即通知
# 通道：本地日志 + Dashboard 警报 + 邮件（可选）
# =============================================================================

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path

# 配置
STRATEGY_DIR = Path("/home/admin/Ziwei/data/strategy")
SIGNAL_CACHE_FILE = Path("/home/admin/Ziwei/data/strategy/.last_signal_cache")
ALERT_LOG = Path("/home/admin/Ziwei/data/logs/soul-trader/strong_signal_alerts.log")

# 信号强度阈值
STRONG_BUY_THRESHOLD = 15.0  # STRONG_BUY 阈值
BUY_THRESHOLD = 10.0         # BUY 阈值


def ensure_dirs():
    """确保目录存在"""
    ALERT_LOG.parent.mkdir(parents=True, exist_ok=True)


def log_alert(message):
    """记录警报到日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] {message}\n"
    
    with open(ALERT_LOG, 'a', encoding='utf-8') as f:
        f.write(log_line)
    
    print(log_line.strip())


def load_last_signal():
    """加载最后处理的信号"""
    if SIGNAL_CACHE_FILE.exists():
        with open(SIGNAL_CACHE_FILE, 'r') as f:
            return json.load(f)
    return {'timestamp': '', 'signals': []}


def save_last_signal(data):
    """保存最后处理的信号"""
    with open(SIGNAL_CACHE_FILE, 'w') as f:
        json.dump(data, f)


def get_latest_signal():
    """获取最新信号文件"""
    signal_files = sorted(STRATEGY_DIR.glob("signals_*.json"), reverse=True)
    if not signal_files:
        return None
    
    with open(signal_files[0], 'r') as f:
        return json.load(f)


def get_latest_prices():
    """获取最新价格"""
    intel_files = sorted(Path("/home/admin/Ziwei/data/intel").glob("intel_*.json"), reverse=True)
    if not intel_files:
        return {}
    
    with open(intel_files[0], 'r') as f:
        intel = json.load(f)
        return intel.get('prices', {})


def find_strong_signals(signals):
    """找出强信号"""
    strong = []
    for signal in signals:
        score = signal.get('score', 0)
        signal_type = signal.get('signal', '')
        
        # STRONG_BUY 或分数超过阈值
        if signal_type == 'STRONG_BUY' or score >= STRONG_BUY_THRESHOLD:
            strong.append({
                **signal,
                'alert_level': 'STRONG_BUY'
            })
        elif signal_type == 'BUY' or score >= BUY_THRESHOLD:
            strong.append({
                **signal,
                'alert_level': 'BUY'
            })
    
    return strong


def create_alert_message(signals, prices):
    """创建警报消息"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    message = f"""
╔═══════════════════════════════════════════════════════════╗
║         🚨 紫微智控 - 强信号警报                           ║
╠═══════════════════════════════════════════════════════════╣
║ 发现时间：{now}
║ 信号数量：{len(signals)} 个
╚═══════════════════════════════════════════════════════════╝

【信号详情】
"""
    
    for signal in signals:
        symbol = signal['symbol']
        price_info = prices.get(symbol, {})
        current_price = price_info.get('price', signal['price'])
        
        message += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 {symbol} - {signal['alert_level']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  信号分数：{signal['score']}
  信号价格：${signal['price']:,.6f}
  当前价格：${current_price:,.6f}
  24h 变化：{signal['change_24h']:.2f}%
  
  💰 建议仓位：${signal['suggested_amount_usd']:,.2f} USDC
  🛑 止损价格：${signal['stop_loss']:,.6f}
  🎯 止盈价格：${signal['take_profit']:,.6f}
  📈 风险回报：{signal['risk_reward_ratio']}:1
  
  原因分析：
"""
        for reason in signal.get('reasons', []):
            message += f"    • {reason}\n"
        
        if signal.get('warnings'):
            message += "\n  ⚠️ 警告:\n"
            for warning in signal['warnings']:
                message += f"    • {warning}\n"
        
        message += "\n"
    
    message += f"""
【操作建议】
1. 立即登录 Dashboard 查看实时数据
2. 确认信号强度和风险
3. 考虑执行交易（模拟或真实）
4. 设置止损和止盈

【快速链接】
• Dashboard 内网：http://localhost:8081
• Dashboard 公网：http://panda66.duckdns.org:8081
• 策略引擎日志：/home/admin/Ziwei/data/logs/soul-trader/strategy_engine_*.out

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
紫微智控交易系统 | 信念×如意×爱人 联合监控
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    return message


def send_telegram_alert(message):
    """发送 Telegram 警报（通过系统消息）"""
    # 这里可以集成 Telegram Bot API
    # 目前先记录到日志
    log_alert("📱 Telegram 警报：" + message[:200] + "...")


def main():
    """主函数"""
    ensure_dirs()
    
    print("=" * 70)
    print("🚨 强信号警报器启动")
    print("=" * 70)
    print(f"监控目录：{STRATEGY_DIR}")
    print(f"警报日志：{ALERT_LOG}")
    print(f"STRONG_BUY 阈值：>={STRONG_BUY_THRESHOLD}")
    print(f"BUY 阈值：>={BUY_THRESHOLD}")
    print("=" * 70)
    
    last_signal = load_last_signal()
    
    while True:
        try:
            # 获取最新信号
            signals = get_latest_signal()
            
            if not signals:
                print("⏳ 暂无信号数据，等待...")
                time.sleep(30)
                continue
            
            # 获取最新价格
            prices = get_latest_prices()
            
            # 找出强信号
            strong_signals = find_strong_signals(signals)
            
            if strong_signals:
                # 检查是否是新信号（避免重复发送）
                current_timestamp = signals[0].get('timestamp', '') if signals else ''
                
                if current_timestamp != last_signal.get('timestamp', ''):
                    print(f"\n🚨 发现 {len(strong_signals)} 个强信号！")
                    
                    # 创建警报消息
                    message = create_alert_message(strong_signals, prices)
                    
                    # 记录到日志
                    log_alert(message)
                    
                    # 发送 Telegram 警报
                    send_telegram_alert(message)
                    
                    # 更新缓存
                    last_signal = {
                        'timestamp': current_timestamp,
                        'signals': [s['symbol'] for s in strong_signals]
                    }
                    save_last_signal(last_signal)
                    
                    print("✅ 警报已发送")
                else:
                    print("⏭️ 信号已处理，跳过")
            else:
                print("⏳ 暂无强信号，继续监控...")
            
            # 等待 30 秒后检查
            time.sleep(30)
            
        except KeyboardInterrupt:
            print("\n🛑 警报器已停止")
            break
        except Exception as e:
            print(f"❌ 错误：{e}")
            import traceback
            traceback.print_exc()
            time.sleep(60)


if __name__ == '__main__':
    main()
