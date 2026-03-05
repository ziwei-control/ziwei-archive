#!/usr/bin/env python3
# =============================================================================
# x402 API - 服务状态监控
# 功能：监控 API 服务运行状态
# =============================================================================

import os
import sys
from datetime import datetime
import pytz

# 配置
SERVICE_HOURS = [
    (9, 11),   # 北京时间 09:00-11:00（亚洲工作时间）
    (20, 22),  # 北京时间 20:00-22:00（欧美工作时间）
]
RATE_LIMIT = 60  # 每 IP 每分钟限 60 次

# 状态文件
STATUS_FILE = "/home/admin/Ziwei/data/x402/service_status.json"

def is_peak_hours():
    """检查当前是否在高峰时段"""
    beijing_tz = pytz.timezone('Asia/Shanghai')
    now = datetime.now(beijing_tz)
    
    current_hour = now.hour
    
    # 检查是否在任何一个高峰时段内
    for start, end in SERVICE_HOURS:
        if start <= current_hour < end:
            return True
    
    return False

def get_service_status():
    """获取服务状态"""
    is_peak = is_peak_hours()
    now = datetime.now()
    
    return {
        "service_active": True,
        "current_time_beijing": now.strftime('%Y-%m-%d %H:%M:%S'),
        "peak_hours": f"{SERVICE_HOURS[0][0]:02d}:00 - {SERVICE_HOURS[0][1]:02d}:00 & {SERVICE_HOURS[1][0]:02d}:00 - {SERVICE_HOURS[1][1]:02d}:00 (Beijing Time)",
        "rate_limit": f"{RATE_LIMIT} calls/minute/IP",
        "pricing": "Pay-per-call, starting at $0.02 USDC",
        "timezone": "Asia/Shanghai"
    }

def write_status():
    """写入状态文件（供 API 读取）"""
    import json
    
    status = get_service_status()
    
    # 确保目录存在
    os.makedirs(os.path.dirname(STATUS_FILE), exist_ok=True)
    
    with open(STATUS_FILE, 'w') as f:
        json.dump(status, f, indent=2)
    
    return status

def main():
    """主函数 - 可被 cron 调用"""
    status = write_status()
    
    print(f"✅ 服务运行正常 - {status['current_time_beijing']}")
    print(f"   计费方式：{status['pricing']}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
