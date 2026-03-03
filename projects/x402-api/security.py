#!/usr/bin/env python3
# =============================================================================
# x402 API - 安全防护模块
# 功能：DDoS 防护、频率限制、IP 黑名单、攻击检测与记录
# =============================================================================

import os
import json
import time
import hashlib
import ipaddress
from datetime import datetime, timedelta
from collections import defaultdict
from pathlib import Path

# 配置
SECURITY_CONFIG = {
    # 频率限制
    "rate_limit": {
        "requests_per_minute": 60,      # 每分钟最大请求数
        "requests_per_hour": 1000,      # 每小时最大请求数
        "burst_limit": 10,              # 突发请求限制
    },
    
    # DDoS 防护
    "ddos": {
        "threshold_per_second": 100,    # 每秒请求阈值
        "block_duration": 3600,         # 封禁时长 (秒)
        "detection_window": 60,         # 检测窗口 (秒)
    },
    
    # 攻击检测
    "attack_detection": {
        "sql_injection": True,          # SQL 注入检测
        "xss": True,                    # XSS 检测
        "path_traversal": True,         # 路径遍历检测
        "command_injection": True,      # 命令注入检测
    },
    
    # IP 黑名单
    "ip_blacklist": {
        "enabled": True,
        "auto_block": True,             # 自动封禁
        "manual_block_list": [],        # 手动封禁列表
    },
    
    # 告警配置
    "alert": {
        "enabled": True,
        "email_alert": True,            # 邮件告警
        "threshold": 10,                # 触发告警的攻击次数
    },
    
    # 日志配置
    "logging": {
        "log_dir": "/home/admin/Ziwei/data/logs/security",
        "retention_days": 30,           # 日志保留天数
        "max_file_size": 100 * 1024 * 1024,  # 最大文件大小 (100MB)
    }
}

# 路径配置
SECURITY_DIR = Path("/home/admin/Ziwei/data/security")
SECURITY_DIR.mkdir(parents=True, exist_ok=True)

# 数据存储文件
IP_STATS_FILE = SECURITY_DIR / "ip_stats.json"
ATTACK_LOG_FILE = SECURITY_DIR / "attack_log.json"
BLACKLIST_FILE = SECURITY_DIR / "blacklist.json"
ALERT_LOG_FILE = SECURITY_DIR / "alert_log.json"


class SecurityManager:
    """安全管理器"""
    
    def __init__(self, config=None):
        self.config = config or SECURITY_CONFIG
        self.ip_stats = defaultdict(lambda: {
            "requests": [],
            "blocked_until": 0,
            "attack_count": 0,
            "last_seen": 0,
        })
        self.blacklist = set()
        self.attack_log = []
        self.alert_count = 0
        self.load_data()
    
    def load_data(self):
        """加载持久化数据"""
        try:
            if IP_STATS_FILE.exists():
                with open(IP_STATS_FILE, "r") as f:
                    data = json.load(f)
                    for ip, stats in data.items():
                        self.ip_stats[ip] = stats
            
            if BLACKLIST_FILE.exists():
                with open(BLACKLIST_FILE, "r") as f:
                    data = json.load(f)
                    self.blacklist = set(data.get("ips", []))
            
            if ATTACK_LOG_FILE.exists():
                with open(ATTACK_LOG_FILE, "r") as f:
                    self.attack_log = json.load(f)
        except Exception as e:
            self.log_security_event("error", f"加载安全数据失败：{e}")
    
    def save_data(self):
        """保存持久化数据"""
        try:
            # 保存 IP 统计 (只保留最近 1 小时的数据)
            now = time.time()
            cutoff = now - 3600
            ip_stats_clean = {}
            for ip, stats in self.ip_stats.items():
                stats["requests"] = [t for t in stats["requests"] if t > cutoff]
                if stats["requests"] or stats["blocked_until"] > now:
                    ip_stats_clean[ip] = stats
            
            with open(IP_STATS_FILE, "w") as f:
                json.dump(ip_stats_clean, f, indent=2)
            
            # 保存黑名单
            with open(BLACKLIST_FILE, "w") as f:
                json.dump({"ips": list(self.blacklist)}, f, indent=2)
            
            # 保存攻击日志 (只保留最近 30 天)
            cutoff = (datetime.now() - timedelta(days=30)).isoformat()
            self.attack_log = [log for log in self.attack_log if log["timestamp"] > cutoff]
            
            with open(ATTACK_LOG_FILE, "w") as f:
                json.dump(self.attack_log, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.log_security_event("error", f"保存安全数据失败：{e}")
    
    def check_ip(self, ip):
        """检查 IP 是否被封锁"""
        if ip in self.blacklist:
            return False, "IP 在黑名单中"
        
        stats = self.ip_stats[ip]
        if stats["blocked_until"] > time.time():
            remaining = int(stats["blocked_until"] - time.time())
            return False, f"IP 已被临时封禁，剩余 {remaining} 秒"
        
        return True, "OK"
    
    def record_request(self, ip):
        """记录请求并检查频率限制"""
        now = time.time()
        stats = self.ip_stats[ip]
        stats["requests"].append(now)
        stats["last_seen"] = now
        
        # 清理旧请求记录
        cutoff_minute = now - 60
        cutoff_hour = now - 3600
        stats["requests"] = [t for t in stats["requests"] if t > cutoff_minute]
        
        # 检查频率限制
        requests_last_minute = len([t for t in stats["requests"] if t > cutoff_minute])
        requests_last_hour = len([t for t in stats["requests"] if t > cutoff_hour])
        
        if requests_last_minute > self.config["rate_limit"]["requests_per_minute"]:
            self.block_ip(ip, 300, "频率限制：每分钟请求过多")
            return False, f"频率限制：每分钟最多 {self.config['rate_limit']['requests_per_minute']} 次请求"
        
        if requests_last_hour > self.config["rate_limit"]["requests_per_hour"]:
            self.block_ip(ip, 600, "频率限制：每小时请求过多")
            return False, f"频率限制：每小时最多 {self.config['rate_limit']['requests_per_hour']} 次请求"
        
        # 检查 DDoS
        requests_last_second = len([t for t in stats["requests"] if t > now - 1])
        if requests_last_second > self.config["ddos"]["threshold_per_second"]:
            self.block_ip(ip, self.config["ddos"]["block_duration"], "疑似 DDoS 攻击")
            self.log_attack(ip, "ddos", f"每秒请求数：{requests_last_second}")
            return False, "疑似 DDoS 攻击"
        
        return True, "OK"
    
    def block_ip(self, ip, duration, reason):
        """封禁 IP"""
        self.ip_stats[ip]["blocked_until"] = time.time() + duration
        self.ip_stats[ip]["attack_count"] += 1
        
        # 自动加入黑名单
        if self.config["ip_blacklist"]["auto_block"]:
            if self.ip_stats[ip]["attack_count"] >= self.config["alert"]["threshold"]:
                self.blacklist.add(ip)
                self.send_alert(ip, reason, self.ip_stats[ip]["attack_count"])
        
        self.log_security_event("block", f"IP {ip} 被封禁：{reason}")
        self.save_data()
    
    def detect_attack(self, ip, data):
        """检测攻击行为"""
        attacks = []
        
        # SQL 注入检测
        if self.config["attack_detection"]["sql_injection"]:
            sql_patterns = [
                r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|ALTER)\b)",
                r"(--|;|\/\*|\*\/)",
                r"(\b(OR|AND)\b\s+\d+\s*=\s*\d+)",
            ]
            for pattern in sql_patterns:
                if pattern.lower() in str(data).lower():
                    attacks.append("sql_injection")
        
        # XSS 检测
        if self.config["attack_detection"]["xss"]:
            xss_patterns = [
                r"<script",
                r"javascript:",
                r"on\w+\s*=",
                r"<iframe",
            ]
            for pattern in xss_patterns:
                if pattern.lower() in str(data).lower():
                    attacks.append("xss")
        
        # 路径遍历检测
        if self.config["attack_detection"]["path_traversal"]:
            if "../" in str(data) or "..\\" in str(data):
                attacks.append("path_traversal")
        
        # 命令注入检测
        if self.config["attack_detection"]["command_injection"]:
            cmd_patterns = [
                r"[;&|`]",
                r"\$\(",
                r"\b(exec|system|eval|passthru)\b",
            ]
            for pattern in cmd_patterns:
                if pattern in str(data):
                    attacks.append("command_injection")
        
        # 记录攻击
        if attacks:
            for attack_type in attacks:
                self.log_attack(ip, attack_type, str(data)[:200])
            
            # 封禁 IP
            if self.config["ip_blacklist"]["auto_block"]:
                self.ip_stats[ip]["attack_count"] += len(attacks)
                if self.ip_stats[ip]["attack_count"] >= self.config["alert"]["threshold"]:
                    self.blacklist.add(ip)
                    self.send_alert(ip, f"检测到攻击：{', '.join(attacks)}", self.ip_stats[ip]["attack_count"])
            
            self.save_data()
            return True, attacks
        
        return False, []
    
    def log_attack(self, ip, attack_type, details):
        """记录攻击日志"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "ip": ip,
            "attack_type": attack_type,
            "details": details,
            "blocked": ip in self.blacklist,
        }
        self.attack_log.append(log_entry)
        self.log_security_event("attack", f"检测到攻击：{ip} - {attack_type}")
    
    def log_security_event(self, event_type, message):
        """记录安全事件"""
        log_file = SECURITY_DIR / f"security_{datetime.now().strftime('%Y%m%d')}.log"
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] [{event_type.upper()}] {message}\n"
        
        try:
            with open(log_file, "a") as f:
                f.write(log_entry)
        except:
            pass
    
    def send_alert(self, ip, reason, attack_count):
        """发送告警"""
        if not self.config["alert"]["enabled"]:
            return
        
        self.alert_count += 1
        alert = {
            "timestamp": datetime.now().isoformat(),
            "ip": ip,
            "reason": reason,
            "attack_count": attack_count,
            "alert_id": self.alert_count,
        }
        
        # 记录告警日志
        try:
            with open(ALERT_LOG_FILE, "a") as f:
                f.write(json.dumps(alert, ensure_ascii=False) + "\n")
        except:
            pass
        
        # TODO: 发送邮件告警
        self.log_security_event("alert", f"安全告警 #{self.alert_count}: {ip} - {reason}")
    
    def get_stats(self):
        """获取安全统计"""
        now = time.time()
        cutoff_hour = now - 3600
        
        total_requests = sum(
            len([t for t in stats["requests"] if t > cutoff_hour])
            for stats in self.ip_stats.values()
        )
        
        return {
            "total_ips": len(self.ip_stats),
            "blocked_ips": len([ip for ip, stats in self.ip_stats.items() if stats["blocked_until"] > now]),
            "blacklisted_ips": len(self.blacklist),
            "total_attacks": len(self.attack_log),
            "attacks_last_hour": len([log for log in self.attack_log if log["timestamp"] > (now - 3600)]),
            "total_requests_last_hour": total_requests,
            "alerts": self.alert_count,
        }
    
    def get_attack_log(self, limit=100):
        """获取攻击日志"""
        return self.attack_log[-limit:]
    
    def get_blacklist(self):
        """获取黑名单"""
        return list(self.blacklist)
    
    def remove_from_blacklist(self, ip):
        """从黑名单移除"""
        if ip in self.blacklist:
            self.blacklist.remove(ip)
            self.ip_stats[ip]["attack_count"] = 0
            self.save_data()
            self.log_security_event("unblock", f"IP {ip} 已从黑名单移除")
            return True
        return False


# 全局安全管理器实例
security_manager = SecurityManager()


# HTTP 中间件集成
def security_middleware(handler_class):
    """安全中间件装饰器"""
    original_do_POST = handler_class.do_POST
    original_do_GET = handler_class.do_GET
    
    def wrapped_do_POST(self):
        # 获取客户端 IP
        client_ip = self.client_address[0]
        
        # 检查 IP 是否被封锁
        allowed, message = security_manager.check_ip(client_ip)
        if not allowed:
            self.send_response(403)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": message}).encode())
            return
        
        # 记录请求并检查频率限制
        allowed, message = security_manager.record_request(client_ip)
        if not allowed:
            self.send_response(429)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": message}).encode())
            return
        
        # 读取请求体并检测攻击
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length > 0:
            request_data = self.rfile.read(content_length).decode('utf-8', errors='ignore')
            
            # 检测攻击
            is_attack, attack_types = security_manager.detect_attack(client_ip, request_data)
            if is_attack:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "error": "检测到攻击行为",
                    "attack_types": attack_types
                }).encode())
                return
        
        # 继续原始处理
        return original_do_POST(self)
    
    def wrapped_do_GET(self):
        # 获取客户端 IP
        client_ip = self.client_address[0]
        
        # 检查 IP 是否被封锁
        allowed, message = security_manager.check_ip(client_ip)
        if not allowed:
            self.send_response(403)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": message}).encode())
            return
        
        # 记录请求并检查频率限制
        allowed, message = security_manager.record_request(client_ip)
        if not allowed:
            self.send_response(429)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": message}).encode())
            return
        
        # 继续原始处理
        return original_do_GET(self)
    
    handler_class.do_POST = wrapped_do_POST
    handler_class.do_GET = wrapped_do_GET
    return handler_class
