#!/usr/bin/env python3
"""
紫微智控 - OpenClaw Gateway 看门狗
监控 OpenClaw Gateway 进程，确保其持续运行
如果 Gateway 挂掉，自动重启并记录日志
"""

import os
import sys
import time
import subprocess
import json
from datetime import datetime
from pathlib import Path

# 配置
WATCHDOG_INTERVAL = 60  # 检查间隔（秒）- 优化：从 20 秒改为 60 秒
GATEWAY_CMD = "/usr/bin/node /opt/openclaw/dist/index.js gateway --port 18789"
GATEWAY_PORT = 18789
PID_FILE = None  # OpenClaw 不使用传统 PID 文件
LOG_FILE = Path("/home/admin/Ziwei/data/logs/supervisor/openclaw_watchdog.log")
RESTART_HISTORY_FILE = Path("/home/admin/Ziwei/data/logs/supervisor/gateway_restart_history.json")
ALERT_FILE = Path("/home/admin/Ziwei/data/alerts/gateway_critical.json")
MAX_RESTART_ATTEMPTS = 5
RESTART_COOLDOWN = 30  # 重启冷却时间（秒）
HEALTH_CHECK_TIMEOUT = 10  # 健康检查超时（秒）
RESTART_WINDOW_SECONDS = 300  # 重启时间窗口（5 分钟）
MAX_RESTARTS_IN_WINDOW = 3  # 5 分钟内最多重启 3 次

class OpenClawWatchdog:
    def __init__(self):
        self.restart_attempts = 0
        self.last_restart_time = 0
        self.running = True
        self.gateway_token = self._load_gateway_token()
        self.restart_history = self._load_restart_history()
    
    def _load_restart_history(self):
        """加载重启历史记录"""
        if RESTART_HISTORY_FILE.exists():
            try:
                with open(RESTART_HISTORY_FILE, 'r') as f:
                    return json.load(f)
            except:
                pass
        return []
    
    def _save_restart_history(self):
        """保存重启历史记录"""
        RESTART_HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        # 只保留最近 100 条记录
        self.restart_history = self.restart_history[-100:]
        with open(RESTART_HISTORY_FILE, 'w') as f:
            json.dump(self.restart_history, f, indent=2)
    
    def _record_restart(self):
        """记录重启事件"""
        self.restart_history.append({
            'timestamp': time.time(),
            'datetime': datetime.now().isoformat(),
            'attempt': self.restart_attempts
        })
        self._save_restart_history()
    
    def should_restart(self):
        """检查是否应该重启（去重机制）"""
        current_time = time.time()
        
        # 统计 5 分钟内的重启次数
        recent_restarts = [
            r for r in self.restart_history 
            if current_time - r['timestamp'] < RESTART_WINDOW_SECONDS
        ]
        
        if len(recent_restarts) >= MAX_RESTARTS_IN_WINDOW:
            self.log(f"🚨 5 分钟内已重启 {len(recent_restarts)} 次，达到上限 ({MAX_RESTARTS_IN_WINDOW})")
            return False
        
        return True
    
    def report_critical_issue(self, message):
        """报告严重问题（写入告警文件）"""
        ALERT_FILE.parent.mkdir(parents=True, exist_ok=True)
        alert = {
            'timestamp': datetime.now().isoformat(),
            'service': 'OpenClaw Gateway',
            'message': message,
            'restart_attempts': self.restart_attempts,
            'requires_attention': True,
            'severity': 'critical'
        }
        with open(ALERT_FILE, 'w') as f:
            json.dump(alert, f, indent=2)
        self.log(f"🚨 已写入告警：{message}")
    
    def _load_gateway_token(self):
        """从配置文件加载 Gateway Token"""
        try:
            config_file = Path("/root/.openclaw/openclaw.json")
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)
                return config.get('gateway', {}).get('auth', {}).get('token', '')
        except Exception as e:
            print(f"加载配置失败：{e}", file=sys.stderr)
        return ''
    
    def log(self, message):
        """记录日志"""
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().isoformat()
        log_line = f"[{timestamp}] {message}\n"
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_line)
        print(log_line.strip())
    
    def is_gateway_running(self):
        """检查 Gateway 是否运行"""
        try:
            result = subprocess.run(
                ['pgrep', '-f', 'openclaw.*gateway'],
                capture_output=True,
                text=True
            )
            return bool(result.stdout.strip())
        except:
            return False
    
    def check_gateway_health(self):
        """检查 Gateway 健康状态"""
        try:
            # 尝试连接 Gateway RPC
            result = subprocess.run(
                ['openclaw', 'gateway', 'status'],
                capture_output=True,
                text=True,
                timeout=HEALTH_CHECK_TIMEOUT
            )
            
            # 检查输出中是否包含 "running"
            if 'running' in result.stdout.lower() or 'pid' in result.stdout.lower():
                return True
            
            # 检查是否是 token 不匹配（这是配置问题，不是服务问题）
            if 'unauthorized' in result.stdout.lower() or 'token mismatch' in result.stdout.lower():
                self.log("⚠️ Gateway 运行中，但 Token 不匹配（配置问题）")
                return True  # 服务在运行，只是配置问题
            
            return False
            
        except subprocess.TimeoutExpired:
            self.log("⚠️ Gateway 健康检查超时")
            return False
        except Exception as e:
            self.log(f"⚠️ Gateway 健康检查失败：{e}")
            return False
    
    def start_gateway(self):
        """启动 Gateway"""
        self.log("⚠️ 尝试启动 OpenClaw Gateway...")
        
        try:
            # 设置环境变量
            env = os.environ.copy()
            env['OPENCLAW_GATEWAY_PORT'] = '18789'
            if self.gateway_token:
                env['OPENCLAW_GATEWAY_TOKEN'] = self.gateway_token
            env['HOME'] = '/root'
            env['PATH'] = '/root/.local/share/pnpm:/root/.local/bin:/root/.npm-global/bin:/root/bin:/root/.nvm/current/bin:/root/.fnm/current/bin:/root/.volta/bin:/root/.asdf/shims:/root/.bun/bin:/usr/local/bin:/usr/bin:/bin'
            
            # 启动 Gateway
            subprocess.Popen(
                ['/usr/bin/node', '/opt/openclaw/dist/index.js', 'gateway', '--port', '18789'],
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # 等待启动
            time.sleep(5)
            
            if self.is_gateway_running():
                self.log("✅ OpenClaw Gateway 启动成功")
                self.restart_attempts = 0  # 重置重启计数
                return True
            else:
                self.log("❌ OpenClaw Gateway 启动失败 - 进程未运行")
                return False
                
        except Exception as e:
            self.log(f"❌ 启动 OpenClaw Gateway 异常：{e}")
            return False
    
    def restart_gateway(self):
        """重启 Gateway（带保护机制）"""
        current_time = time.time()
        
        # 检查冷却时间
        if current_time - self.last_restart_time < RESTART_COOLDOWN:
            self.log(f"⏳ 冷却期内，跳过重启 (剩余 {int(RESTART_COOLDOWN - (current_time - self.last_restart_time))}秒)")
            return False
        
        # 🧠 去重检查：5 分钟内重启次数
        if not self.should_restart():
            self.report_critical_issue(f"OpenClaw Gateway 在 5 分钟内重启 {MAX_RESTARTS_IN_WINDOW} 次，需要人工干预！")
            self.log(f"📞 已写入告警文件：{ALERT_FILE}")
            return False
        
        # 检查重启次数
        if self.restart_attempts >= MAX_RESTART_ATTEMPTS:
            self.log(f"🚨 达到最大重启次数 ({MAX_RESTART_ATTEMPTS})，停止自动重启")
            self.report_critical_issue(f"OpenClaw Gateway 累计重启 {MAX_RESTART_ATTEMPTS} 次，需要人工干预！")
            return False
        
        self.log(f"🔄 重启 OpenClaw Gateway (尝试 {self.restart_attempts + 1}/{MAX_RESTART_ATTEMPTS})")
        
        # 先停止现有进程
        try:
            subprocess.run(['pkill', '-f', 'openclaw.*gateway'], timeout=5)
            time.sleep(3)
        except:
            pass
        
        # 启动
        if self.start_gateway():
            self.last_restart_time = current_time
            self.restart_attempts += 1
            self._record_restart()  # 记录重启历史
            return True
        
        return False
    
    def run(self):
        """主循环"""
        self.log("=" * 60)
        self.log("🐕 OpenClaw Gateway 看门狗启动")
        self.log(f"检查间隔：{WATCHDOG_INTERVAL}秒")
        self.log(f"最大重启次数：{MAX_RESTART_ATTEMPTS}")
        self.log(f"重启冷却时间：{RESTART_COOLDOWN}秒")
        self.log(f"健康检查超时：{HEALTH_CHECK_TIMEOUT}秒")
        self.log("=" * 60)
        
        try:
            while self.running:
                # 检查 Gateway 是否运行
                if not self.is_gateway_running():
                    self.log("❌ OpenClaw Gateway 未运行！")
                    if self.restart_gateway():
                        self.log("✅ 重启成功")
                    else:
                        self.log("🚨 重启失败或已跳过")
                elif not self.check_gateway_health():
                    self.log("❌ OpenClaw Gateway 无响应！")
                    if self.restart_gateway():
                        self.log("✅ 重启成功")
                    else:
                        self.log("🚨 重启失败或已跳过")
                else:
                    self.log("✅ OpenClaw Gateway 运行正常")
                
                # 等待下次检查
                time.sleep(WATCHDOG_INTERVAL)
        
        except KeyboardInterrupt:
            self.log("\n👋 收到停止信号，看门狗退出")
            self.running = False
        except Exception as e:
            self.log(f"🚨 看门狗异常：{e}")
            raise


def main():
    watchdog = OpenClawWatchdog()
    watchdog.run()


if __name__ == "__main__":
    main()
