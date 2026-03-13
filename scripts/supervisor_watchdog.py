#!/usr/bin/env python3
"""
紫微智控 - Supervisor 看门狗
监控 Supervisor 主进程，确保其持续运行
如果 Supervisor 挂掉，自动重启并记录日志
"""

import os
import sys
import time
import subprocess
from datetime import datetime
from pathlib import Path

# 配置
WATCHDOG_INTERVAL = 60  # 检查间隔（秒）- 优化：从 30 秒改为 60 秒
SUPERVISOR_CMD = "/usr/local/bin/supervisord"
SUPERVISOR_CONF = "/etc/supervisord.conf"
PID_FILE = "/var/run/supervisord.pid"
LOG_FILE = Path("/home/admin/Ziwei/data/logs/supervisor/watchdog.log")
RESTART_HISTORY_FILE = Path("/home/admin/Ziwei/data/logs/supervisor/supervisor_restart_history.json")
ALERT_FILE = Path("/home/admin/Ziwei/data/alerts/supervisor_critical.json")
MAX_RESTART_ATTEMPTS = 5
RESTART_COOLDOWN = 60  # 重启冷却时间（秒）
RESTART_WINDOW_SECONDS = 300  # 重启时间窗口（5 分钟）
MAX_RESTARTS_IN_WINDOW = 3  # 5 分钟内最多重启 3 次

class SupervisorWatchdog:
    def __init__(self):
        self.restart_attempts = 0
        self.last_restart_time = 0
        self.running = True
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
        recent_restarts = [
            r for r in self.restart_history 
            if current_time - r['timestamp'] < RESTART_WINDOW_SECONDS
        ]
        
        if len(recent_restarts) >= MAX_RESTARTS_IN_WINDOW:
            self.log(f"🚨 5 分钟内已重启 {len(recent_restarts)} 次，达到上限 ({MAX_RESTARTS_IN_WINDOW})")
            return False
        
        return True
    
    def report_critical_issue(self, message):
        """报告严重问题"""
        ALERT_FILE.parent.mkdir(parents=True, exist_ok=True)
        alert = {
            'timestamp': datetime.now().isoformat(),
            'service': 'Supervisor',
            'message': message,
            'restart_attempts': self.restart_attempts,
            'requires_attention': True,
            'severity': 'critical'
        }
        with open(ALERT_FILE, 'w') as f:
            json.dump(alert, f, indent=2)
        self.log(f"🚨 已写入告警：{message}")
    
    def log(self, message):
        """记录日志"""
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().isoformat()
        log_line = f"[{timestamp}] {message}\n"
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_line)
        print(log_line.strip())
    
    def is_supervisor_running(self):
        """检查 Supervisor 是否运行"""
        # 方法 1: 检查 PID 文件
        if os.path.exists(PID_FILE):
            try:
                with open(PID_FILE, 'r') as f:
                    pid = int(f.read().strip())
                # 检查进程是否存在
                os.kill(pid, 0)
                return True
            except (ProcessLookupError, ValueError, PermissionError):
                pass
        
        # 方法 2: 检查进程
        try:
            result = subprocess.run(
                ['pgrep', '-f', 'supervisord'],
                capture_output=True,
                text=True
            )
            return bool(result.stdout.strip())
        except:
            return False
    
    def check_supervisorctl(self):
        """检查 supervisorctl 是否能正常响应"""
        try:
            result = subprocess.run(
                ['supervisorctl', 'status'],
                capture_output=True,
                text=True,
                timeout=10
            )
            # 如果有输出，说明 Supervisor 正常
            return bool(result.stdout.strip())
        except:
            return False
    
    def start_supervisor(self):
        """启动 Supervisor"""
        self.log("⚠️ 尝试启动 Supervisor...")
        
        try:
            # 先清理可能存在的旧 PID 文件
            if os.path.exists(PID_FILE):
                os.remove(PID_FILE)
                self.log("🗑️ 已清理旧 PID 文件")
            
            # 启动 Supervisor
            subprocess.Popen(
                [SUPERVISOR_CMD, '-c', SUPERVISOR_CONF],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # 等待启动
            time.sleep(3)
            
            if self.is_supervisor_running():
                self.log("✅ Supervisor 启动成功")
                self.restart_attempts = 0  # 重置重启计数
                return True
            else:
                self.log("❌ Supervisor 启动失败 - 进程未运行")
                return False
                
        except Exception as e:
            self.log(f"❌ 启动 Supervisor 异常：{e}")
            return False
    
    def restart_supervisor(self):
        """重启 Supervisor（带保护机制）"""
        current_time = time.time()
        
        # 检查冷却时间
        if current_time - self.last_restart_time < RESTART_COOLDOWN:
            self.log(f"⏳ 冷却期内，跳过重启 (剩余 {int(RESTART_COOLDOWN - (current_time - self.last_restart_time))}秒)")
            return False
        
        # 🧠 去重检查：5 分钟内重启次数
        if not self.should_restart():
            self.report_critical_issue(f"Supervisor 在 5 分钟内重启 {MAX_RESTARTS_IN_WINDOW} 次，需要人工干预！")
            return False
        
        # 检查重启次数
        if self.restart_attempts >= MAX_RESTART_ATTEMPTS:
            self.log(f"🚨 达到最大重启次数 ({MAX_RESTART_ATTEMPTS})，停止自动重启")
            self.report_critical_issue(f"Supervisor 累计重启 {MAX_RESTART_ATTEMPTS} 次，需要人工干预！")
            return False
        
        self.log(f"🔄 重启 Supervisor (尝试 {self.restart_attempts + 1}/{MAX_RESTART_ATTEMPTS})")
        
        # 先停止现有进程
        try:
            subprocess.run(['pkill', '-f', 'supervisord'], timeout=5)
            time.sleep(2)
        except:
            pass
        
        # 启动
        if self.start_supervisor():
            self.last_restart_time = current_time
            self.restart_attempts += 1
            self._record_restart()
            return True
        
        return False
    
    def check_managed_processes(self):
        """检查 Supervisor 管理的进程状态"""
        try:
            result = subprocess.run(
                ['supervisorctl', 'status'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if not result.stdout.strip():
                self.log("⚠️ supervisorctl 无输出")
                return False
            
            # 统计运行中的进程
            running = 0
            failed = 0
            failed_processes = []
            
            for line in result.stdout.split('\n'):
                if 'RUNNING' in line:
                    running += 1
                elif 'FATAL' in line or 'BACKOFF' in line:
                    failed += 1
                    failed_processes.append(line.strip())
                    self.log(f"⚠️ 进程异常：{line.strip()}")
            
            self.log(f"📊 进程状态：{running} 运行中，{failed} 异常")
            
            if failed > 0:
                # 只重启需要自动重启的进程（配置了 autorestart=true 的进程）
                # 忽略设置了 autostart=false 的进程
                processes_to_restart = []
                for proc_line in failed_processes:
                    process_name = proc_line.split()[0]
                    # 检查这个进程是否设置了 autorestart=true
                    try:
                        config_result = subprocess.run(
                            ['supervisorctl', 'avail'],
                            capture_output=True,
                            text=True,
                            timeout=5
                        )
                        # 只重启那些应该自动重启的进程
                        # 忽略设置了 autostart=false 的进程
                        if process_name not in ['ziwei-continuous-learner', 'ziwei-self-learn', 
                                                'ziwei-self-evolution', 'ziwei-observer-watchdog']:
                            processes_to_restart.append(process_name)
                    except:
                        pass
                
                if processes_to_restart:
                    self.log(f"ℹ️ 重启异常进程：{', '.join(processes_to_restart)}")
                    for proc in processes_to_restart:
                        try:
                            subprocess.run(['supervisorctl', 'restart', proc], timeout=10)
                        except:
                            self.log(f"⚠️ 重启 {proc} 失败")
                else:
                    self.log("ℹ️ 没有需要自动重启的进程")
            
            return True
            
        except Exception as e:
            self.log(f"❌ 检查进程状态失败：{e}")
            return False
    
    def run(self):
        """主循环"""
        self.log("=" * 60)
        self.log("🐕 Supervisor 看门狗启动")
        self.log(f"检查间隔：{WATCHDOG_INTERVAL}秒")
        self.log(f"最大重启次数：{MAX_RESTART_ATTEMPTS}")
        self.log(f"重启冷却时间：{RESTART_COOLDOWN}秒")
        self.log("=" * 60)
        
        try:
            while self.running:
                # 检查 Supervisor 是否运行
                if not self.is_supervisor_running():
                    self.log("❌ Supervisor 未运行！")
                    self.restart_supervisor()
                elif not self.check_supervisorctl():
                    self.log("❌ Supervisor 无响应！")
                    self.restart_supervisor()
                else:
                    # Supervisor 正常，检查管理的进程
                    self.check_managed_processes()
                
                # 等待下次检查
                time.sleep(WATCHDOG_INTERVAL)
        
        except KeyboardInterrupt:
            self.log("\n👋 收到停止信号，看门狗退出")
            self.running = False
        except Exception as e:
            self.log(f"🚨 看门狗异常：{e}")
            raise


def main():
    watchdog = SupervisorWatchdog()
    watchdog.run()


if __name__ == "__main__":
    main()
