#!/usr/bin/env python3
# =============================================================================
# x402 API - 安全监控面板
# 功能：查看安全统计、攻击日志、管理黑名单
# =============================================================================

import json
import sys
from pathlib import Path
from datetime import datetime

SECURITY_DIR = Path("/home/admin/Ziwei/data/security")

def load_json(filepath):
    """加载 JSON 文件"""
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except:
        return {}

def show_dashboard():
    """显示安全监控面板"""
    print("=" * 70)
    print("🛡️  x402 API - 安全监控面板")
    print("=" * 70)
    print(f"📅 时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 加载统计数据
    ip_stats = load_json(SECURITY_DIR / "ip_stats.json")
    attack_log = load_json(SECURITY_DIR / "attack_log.json")
    blacklist = load_json(SECURITY_DIR / "blacklist.json")
    
    # 计算统计
    now = __import__('time').time()
    cutoff_hour = now - 3600
    
    total_ips = len(ip_stats)
    blocked_ips = len([ip for ip, stats in ip_stats.items() if stats.get("blocked_until", 0) > now])
    blacklisted_ips = len(blacklist.get("ips", []))
    total_attacks = len(attack_log) if isinstance(attack_log, list) else 0
    
    print("📊 安全统计")
    print("-" * 70)
    print(f"  总 IP 数：{total_ips}")
    print(f"  当前封禁：{blocked_ips}")
    print(f"  黑名单 IP: {blacklisted_ips}")
    print(f"  总攻击数：{total_attacks}")
    print()
    
    # 显示最近攻击
    if isinstance(attack_log, list) and attack_log:
        print("🚨 最近攻击 (最近 10 条)")
        print("-" * 70)
        for log in attack_log[-10:]:
            timestamp = log.get("timestamp", "Unknown")[:19]
            ip = log.get("ip", "Unknown")
            attack_type = log.get("attack_type", "Unknown")
            blocked = "🔒" if log.get("blocked") else "⚠️"
            print(f"  {blocked} {timestamp} | {ip:15s} | {attack_type}")
        print()
    
    # 显示黑名单
    if blacklist.get("ips"):
        print("⛔ 黑名单 IP")
        print("-" * 70)
        for ip in blacklist["ips"][:20]:
            print(f"  {ip}")
        if len(blacklist["ips"]) > 20:
            print(f"  ... 还有 {len(blacklist['ips']) - 20} 个")
        print()
    
    # 显示告警
    alert_log = SECURITY_DIR / "alert_log.json"
    if alert_log.exists():
        try:
            with open(alert_log, "r") as f:
                alerts = [json.loads(line) for line in f]
            if alerts:
                print("⚠️  最近告警 (最近 5 条)")
                print("-" * 70)
                for alert in alerts[-5:]:
                    timestamp = alert.get("timestamp", "Unknown")[:19]
                    alert_id = alert.get("alert_id", "?")
                    ip = alert.get("ip", "Unknown")
                    reason = alert.get("reason", "Unknown")[:50]
                    print(f"  #{alert_id} {timestamp} | {ip:15s} | {reason}")
                print()
        except:
            pass
    
    # 操作菜单
    print("🔧 操作菜单")
    print("-" * 70)
    print("  1. 查看完整攻击日志")
    print("  2. 查看完整黑名单")
    print("  3. 从黑名单移除 IP")
    print("  4. 清空攻击日志")
    print("  5. 导出安全报告")
    print("  0. 退出")
    print()
    
    choice = input("请选择操作 (0-5): ").strip()
    
    if choice == "1":
        show_attack_log()
    elif choice == "2":
        show_blacklist()
    elif choice == "3":
        remove_from_blacklist()
    elif choice == "4":
        clear_attack_log()
    elif choice == "5":
        export_report()
    elif choice == "0":
        print("👋 再见！")
        sys.exit(0)
    
    # 返回主菜单
    show_dashboard()


def show_attack_log():
    """显示完整攻击日志"""
    attack_log = load_json(SECURITY_DIR / "attack_log.json")
    if isinstance(attack_log, list):
        print(f"\n📋 攻击日志 (共 {len(attack_log)} 条)")
        print("-" * 70)
        for log in attack_log[-50:]:
            timestamp = log.get("timestamp", "Unknown")
            ip = log.get("ip", "Unknown")
            attack_type = log.get("attack_type", "Unknown")
            details = log.get("details", "")[:100]
            print(f"{timestamp} | {ip:15s} | {attack_type:20s} | {details}")
    else:
        print("\n⚠️  无攻击日志")
    input("\n按回车返回...")


def show_blacklist():
    """显示完整黑名单"""
    blacklist = load_json(SECURITY_DIR / "blacklist.json")
    ips = blacklist.get("ips", [])
    print(f"\n⛔ 黑名单 (共 {len(ips)} 个 IP)")
    print("-" * 70)
    for ip in ips:
        print(f"  {ip}")
    input("\n按回车返回...")


def remove_from_blacklist():
    """从黑名单移除 IP"""
    ip = input("\n请输入要移除的 IP: ").strip()
    blacklist = load_json(SECURITY_DIR / "blacklist.json")
    if ip in blacklist.get("ips", []):
        blacklist["ips"].remove(ip)
        with open(SECURITY_DIR / "blacklist.json", "w") as f:
            json.dump(blacklist, f, indent=2)
        print(f"✅ IP {ip} 已从黑名单移除")
    else:
        print(f"⚠️  IP {ip} 不在黑名单中")
    input("\n按回车返回...")


def clear_attack_log():
    """清空攻击日志"""
    confirm = input("\n确定要清空攻击日志吗？(y/n): ").strip().lower()
    if confirm == "y":
        with open(SECURITY_DIR / "attack_log.json", "w") as f:
            json.dump([], f)
        print("✅ 攻击日志已清空")
    input("\n按回车返回...")


def export_report():
    """导出安全报告"""
    report_file = SECURITY_DIR / f"security_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    ip_stats = load_json(SECURITY_DIR / "ip_stats.json")
    attack_log = load_json(SECURITY_DIR / "attack_log.json")
    blacklist = load_json(SECURITY_DIR / "blacklist.json")
    
    report = {
        "export_time": datetime.now().isoformat(),
        "statistics": {
            "total_ips": len(ip_stats),
            "blacklisted_ips": len(blacklist.get("ips", [])),
            "total_attacks": len(attack_log) if isinstance(attack_log, list) else 0,
        },
        "blacklist": blacklist,
        "recent_attacks": attack_log[-100:] if isinstance(attack_log, list) else [],
    }
    
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 安全报告已导出：{report_file}")
    input("\n按回车返回...")


if __name__ == "__main__":
    show_dashboard()
