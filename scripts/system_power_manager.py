#!/usr/bin/env python3
"""
紫微智控 - 系统电源管理服务
提供关机、重启、定时开机等功能的 HTTP API 接口
"""

import os
import sys
import json
import subprocess
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

# 配置
PORT = 9002
Ziwei_DIR = Path("/home/admin/Ziwei")
POWER_LOG = Ziwei_DIR / "data/logs/power/power_actions.log"
SCHEDULE_FILE = Ziwei_DIR / "data/config/power_schedule.json"

class PowerHandler(BaseHTTPRequestHandler):
    """电源管理 HTTP 处理器"""
    
    def log_message(self, format, *args):
        """自定义日志"""
        pass
    
    def send_json(self, data, status=200):
        """发送 JSON 响应"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())
    
    def do_GET(self):
        """处理 GET 请求"""
        if self.path == '/status':
            self.get_status()
        elif self.path == '/schedule':
            self.get_schedule()
        elif self.path.startswith('/shutdown'):
            self.shutdown()
        elif self.path.startswith('/reboot'):
            self.reboot()
        elif self.path.startswith('/cancel'):
            self.cancel_schedule()
        else:
            self.send_json({'error': '未知接口'}, 404)
    
    def do_POST(self):
        """处理 POST 请求"""
        if self.path == '/schedule':
            self.set_schedule()
        else:
            self.send_json({'error': '未知接口'}, 404)
    
    def get_status(self):
        """获取系统状态"""
        try:
            # 获取运行时间
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.readline().split()[0])
                uptime_str = str(timedelta(seconds=int(uptime_seconds)))
            
            # 获取计划任务
            schedule = None
            if SCHEDULE_FILE.exists():
                with open(SCHEDULE_FILE, 'r') as f:
                    schedule = json.load(f)
            
            self.send_json({
                'status': 'online',
                'uptime': uptime_str,
                'scheduled_action': schedule,
                'current_time': datetime.now().isoformat()
            })
        except Exception as e:
            self.send_json({'error': str(e)}, 500)
    
    def get_schedule(self):
        """获取计划任务"""
        if not SCHEDULE_FILE.exists():
            self.send_json({'scheduled': None})
            return
        
        try:
            with open(SCHEDULE_FILE, 'r') as f:
                schedule = json.load(f)
            self.send_json({'scheduled': schedule})
        except Exception as e:
            self.send_json({'error': str(e)}, 500)
    
    def shutdown(self):
        """立即关机"""
        try:
            self.log_action('shutdown', 'immediate')
            self.send_json({'status': 'executing', 'action': 'shutdown'})
            # 延迟 2 秒执行，让响应先发送
            subprocess.Popen(['sleep', '2', '&&', 'poweroff'], shell=True)
        except Exception as e:
            self.send_json({'error': str(e)}, 500)
    
    def reboot(self):
        """立即重启"""
        try:
            self.log_action('reboot', 'immediate')
            self.send_json({'status': 'executing', 'action': 'reboot'})
            # 延迟 2 秒执行，让响应先发送
            subprocess.Popen(['sleep', '2', '&&', 'reboot'], shell=True)
        except Exception as e:
            self.send_json({'error': str(e)}, 500)
    
    def set_schedule(self):
        """设置定时任务"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode()
            data = json.loads(body)
            
            action = data.get('action')  # shutdown / reboot / poweron
            time_str = data.get('time')  # ISO 格式或 HH:MM
            
            if not action or not time_str:
                self.send_json({'error': '缺少 action 或 time 参数'}, 400)
                return
            
            # 解析时间
            if 'T' in time_str:
                # ISO 格式
                schedule_time = datetime.fromisoformat(time_str)
            else:
                # HH:MM 格式，设为今天或明天
                today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                hour, minute = map(int, time_str.split(':'))
                schedule_time = today + timedelta(hours=hour, minutes=minute)
                if schedule_time < datetime.now():
                    schedule_time += timedelta(days=1)
            
            schedule = {
                'action': action,
                'time': schedule_time.isoformat(),
                'created_at': datetime.now().isoformat()
            }
            
            # 保存计划
            SCHEDULE_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(SCHEDULE_FILE, 'w') as f:
                json.dump(schedule, f, ensure_ascii=False, indent=2)
            
            # 设置定时任务
            if action in ['shutdown', 'reboot']:
                self.set_system_schedule(schedule_time, action)
            
            self.log_action('schedule', f'{action} at {schedule_time.isoformat()}')
            self.send_json({'status': 'scheduled', 'schedule': schedule})
            
        except Exception as e:
            self.send_json({'error': str(e)}, 500)
    
    def cancel_schedule(self):
        """取消计划任务"""
        try:
            if SCHEDULE_FILE.exists():
                SCHEDULE_FILE.unlink()
            
            # 取消系统定时任务
            subprocess.run(['atrm', 'ziwei_power'], stderr=subprocess.DEVNULL)
            
            self.log_action('cancel', 'scheduled task')
            self.send_json({'status': 'cancelled'})
        except Exception as e:
            self.send_json({'error': str(e)}, 500)
    
    def set_system_schedule(self, schedule_time, action):
        """设置系统级定时任务"""
        try:
            # 计算延迟秒数
            delay = (schedule_time - datetime.now()).total_seconds()
            if delay < 0:
                delay = 0
            
            # 使用 at 命令设置定时任务
            cmd = f"""
echo '{'poweroff' if action == 'shutdown' else 'reboot'}' | at -M ziwei_power now + {int(delay)} seconds
"""
            subprocess.run(cmd, shell=True)
        except Exception as e:
            print(f"设置系统定时任务失败：{e}", file=sys.stderr)
    
    def log_action(self, action, details):
        """记录操作日志"""
        POWER_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(POWER_LOG, 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.now().isoformat()}] {action}: {details}\n")


def main():
    """主函数"""
    print(f"[{datetime.now().isoformat()}] 紫微电源管理服务启动")
    print(f"监听端口：{PORT}")
    print(f"API 接口:")
    print(f"  GET  /status    - 获取系统状态")
    print(f"  GET  /schedule  - 获取计划任务")
    print(f"  GET  /shutdown  - 立即关机")
    print(f"  GET  /reboot    - 立即重启")
    print(f"  GET  /cancel    - 取消计划")
    print(f"  POST /schedule  - 设置计划任务")
    print(f"访问地址：http://localhost:{PORT}")
    
    try:
        server = HTTPServer(('0.0.0.0', PORT), PowerHandler)
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[电源管理] 收到停止信号，正常退出")
        sys.exit(0)
    except Exception as e:
        print(f"[电源管理] 启动失败：{e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
