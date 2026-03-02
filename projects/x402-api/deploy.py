#!/usr/bin/env python3
# =============================================================================
# x402 API - 生产环境部署脚本
# 功能：一键部署到公网服务器
# =============================================================================

import os
import sys
import subprocess
import signal
from datetime import datetime

# 配置
PROJECT_DIR = "/home/admin/Ziwei/projects/x402-api"
APP_FILE = "app_production.py"
PORT = 5002
PID_FILE = f"{PROJECT_DIR}/api.pid"
LOG_FILE = f"{PROJECT_DIR}/api.log"

class Deployer:
    """部署器"""

    def __init__(self):
        self.project_dir = PROJECT_DIR
        self.app_file = APP_FILE
        self.port = PORT
        self.pid_file = PID_FILE
        self.log_file = LOG_FILE

    def stop_service(self):
        """停止服务"""
        if os.path.exists(self.pid_file):
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            try:
                os.kill(pid, signal.SIGTERM)
                print(f"✅ 服务已停止 (PID: {pid})")
                os.remove(self.pid_file)
            except ProcessLookupError:
                print(f"⚠️  进程不存在，清理 PID 文件")
                os.remove(self.pid_file)
        else:
            print("ℹ️  服务未运行")

    def start_service(self):
        """启动服务"""
        # 检查端口是否被占用
        try:
            import socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', self.port))
        except OSError:
            print(f"❌ 端口 {self.port} 已被占用，请先停止旧服务")
            return False

        # 启动服务
        cmd = f"cd {self.project_dir} && nohup python3 {self.app_file} > {self.log_file} 2>&1 &"
        process = subprocess.Popen(cmd, shell=True)
        
        # 保存 PID
        with open(self.pid_file, 'w') as f:
            f.write(str(process.pid))
        
        print(f"✅ 服务已启动 (PID: {process.pid})")
        print(f"📍 服务地址: http://0.0.0.0:{self.port}")
        print(f"📄 日志文件: {self.log_file}")
        return True

    def restart_service(self):
        """重启服务"""
        print("🔄 重启服务...")
        self.stop_service()
        import time
        time.sleep(2)
        return self.start_service()

    def check_status(self):
        """检查状态"""
        if os.path.exists(self.pid_file):
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            try:
                os.kill(pid, 0)  # 检查进程是否存在
                print(f"✅ 服务运行中 (PID: {pid})")
                print(f"📍 访问地址: http://0.0.0.0:{self.port}")
                print(f"📊 健康检查: http://0.0.0.0:{self.port}/health")
                return True
            except ProcessLookupError:
                print("❌ 进程不存在，需要启动服务")
                return False
        else:
            print("❌ 服务未运行")
            return False

    def show_logs(self):
        """显示日志"""
        if os.path.exists(self.log_file):
            print(f"📄 最近 50 行日志 ({self.log_file}):")
            print("-" * 70)
            result = subprocess.run(
                ['tail', '-n', '50', self.log_file],
                capture_output=True,
                text=True
            )
            print(result.stdout)
        else:
            print("❌ 日志文件不存在")

    def test_api(self):
        """测试 API"""
        import urllib.request
        import json
        
        try:
            # 健康检查
            url = f"http://localhost:{self.port}/health"
            response = urllib.request.urlopen(url, timeout=5)
            health = json.loads(response.read().decode('utf-8'))
            
            print(f"✅ 健康检查: {health['status']}")
            print(f"   版本: {health['version']}")
            print(f"   API Key: {'已配置' if health.get('api_key_configured') else '未配置'}")
            print(f"   模式: {health.get('mode', 'unknown')}")
            
            return True
        except Exception as e:
            print(f"❌ API 测试失败: {e}")
            return False

def main():
    """主函数"""
    print("=" * 70)
    print("🚀 x402 API - 生产环境部署工具")
    print("=" * 70)
    print()

    deployer = Deployer()

    if len(sys.argv) < 2:
        print("用法:")
        print("  python deploy.py start    - 启动服务")
        print("  python deploy.py stop     - 停止服务")
        print("  python deploy.py restart  - 重启服务")
        print("  python deploy.py status   - 检查状态")
        print("  python deploy.py logs     - 查看日志")
        print("  python deploy.py test     - 测试 API")
        print()
        print("当前状态:")
        deployer.check_status()
        print()
        return

    command = sys.argv[1].lower()

    if command == 'start':
        deployer.start_service()
    elif command == 'stop':
        deployer.stop_service()
    elif command == 'restart':
        deployer.restart_service()
    elif command == 'status':
        deployer.check_status()
    elif command == 'logs':
        deployer.show_logs()
    elif command == 'test':
        deployer.test_api()
    else:
        print(f"❌ 未知命令: {command}")

if __name__ == "__main__":
    main()